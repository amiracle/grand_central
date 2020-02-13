import logging
import os
import sys
import uuid
import splunk.admin as admin
import ensemble_aws_accounts_schema
import urllib
import hashlib
import base_eai_handler
import log_helper
import boto3
import botocore
import json

if sys.platform == 'win32':
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup the handler
logger = log_helper.setup(logging.INFO, 'EnsembleAWSAccountsEAIHandler', 'ensemble_aws_accounts_handler.log')

class EnsembleAWSAccountsEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in ensemble_aws_accounts_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def assumed_role_session(self, role_arn):
        base_session = None
        base_session = base_session or boto3.session.Session()._session
        fetcher = botocore.credentials.AssumeRoleCredentialFetcher(
            client_creator = base_session.create_client,
            source_credentials = base_session.get_credentials(),
            role_arn = role_arn,
            extra_args = {
            #    'RoleSessionName': None # set this if you want something non-default
            }
        )
        creds = botocore.credentials.DeferredRefreshableCredentials(
            method = 'assume-role',
            refresh_using = fetcher.fetch_credentials,
            time_fetcher = lambda: datetime.datetime.now(tzlocal())
        )
        botocore_session = botocore.session.Session()
        botocore_session._credentials = creds
        return boto3.Session(botocore_session = botocore_session)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Ensemble AWS accounts list requested.')

        # Fetch from ensemble_aws_accounts conf handler
        conf_handler_path = self.get_conf_handler_path_name('ensemble_aws_accounts', 'nobody')
        ensemble_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')

        # Add link alternate (without mgmt, scheme, host, port) to list response
        for ensemble_aws_accounts in ensemble_aws_accounts_eai_response_payload['entry']:
            ensemble_aws_accounts_link_alternate = ensemble_aws_accounts['links']['alternate'].replace('/configs/conf-ensemble_aws_accounts/', '/ensemble_aws_accounts/')

            if ensemble_aws_accounts['content'].get('cloudformation_stack_id', '') != '':
                ensemble_aws_accounts['content']['data_collection_deployed'] = '1'

                # Get AWS Secret Key
                passwords_conf_payload = self.simple_request_eai(ensemble_aws_accounts['content']['aws_secret_key_link_alternate'], 'list', 'GET')
                SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

                aws_account_id = ensemble_aws_accounts['entry'][0]['content']['aws_account_id']
                role_arn = "arn:aws:iam::{0}:role/SplunkDataCollectionCrossAccountRole".format(aws_account_id)
                session = self.assumed_role_session(role_arn)

                try:
                    client = session.client('cloudformation', region_name=params['aws_region'])
                    response = client.describe_stacks(
                        StackName=ensemble_aws_accounts['name'],
                    )
                except Exception, e:
                    ensemble_aws_accounts['content']['data_collection_deployed'] = '0'
                    ensemble_aws_accounts['content']['data_collection_deployment_success'] = '0'

                    # Remove stack_id from the Ensemble AWS Account conf entry
                    ensemble_aws_accounts['content']['cloudformation_stack_id'] = ''
                    continue

                data_collection_deployment_success = '0'

                for stack in response['Stacks']:
                    if stack['StackName'] == ensemble_aws_accounts['name']:
                        if stack['StackStatus'] == 'DELETE_IN_PROGRESS':
                            data_collection_deployment_success = '3'
                            ensemble_aws_accounts['content']['data_collection_deployed'] = '2'
                        if stack['StackStatus'] == 'CREATE_IN_PROGRESS':
                            data_collection_deployment_success = '2'
                        if stack['StackStatus'] == 'UPDATE_IN_PROGRESS':
                            data_collection_deployment_success = '2'
                        if stack['StackStatus'] == 'CREATE_COMPLETE':
                            data_collection_deployment_success = '1'
                        if stack['StackStatus'] == 'UPDATE_COMPLETE':
                            data_collection_deployment_success = '1'

                ensemble_aws_accounts['content']['data_collection_deployment_success'] = data_collection_deployment_success

            else:
                ensemble_aws_accounts['content']['data_collection_deployed'] = '0'

            ensemble_aws_accounts['content']['ensemble_aws_accounts_link_alternate'] = ensemble_aws_accounts_link_alternate
            ensemble_aws_accounts['content']['ensemble_aws_accounts_name'] = ensemble_aws_accounts['name']
            ensemble_aws_accounts['content']['aws_access_key'] = ensemble_aws_accounts['content'].get('aws_access_key', '')
            ensemble_aws_accounts['content']['cloudformation_stack_id'] = ensemble_aws_accounts['content'].get(
                'cloudformation_stack_id', '')
            ensemble_aws_accounts['content']['tags'] = ensemble_aws_accounts['content'].get('tags', '')

        self.set_conf_info_from_eai_payload(confInfo, ensemble_aws_accounts_eai_response_payload)

    def handleCreate(self, confInfo):
        """
        Called when user invokes the "create" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Ensemble AWS account creation requested.')

        # Validate and extract correct POST params
        server_params = self.validate_server_schema_params()
        auth_params = self.validate_auth_schema_params()
        params = auth_params.copy()
        params.update(server_params)

        # Password creation
        aws_secret_key_link_alternate = self.password_create(params['aws_access_key'], params['aws_secret_key'])

        # ensemble_aws_accounts.conf creation and response
        post_args = {
            'name': params['name'],
            'aws_account_id': params['aws_account_id'],
            'aws_access_key': params['aws_access_key'],
            'aws_secret_key_link_alternate': aws_secret_key_link_alternate,
            'data_collection_deployed': '0',
            'data_collection_deployment_success': '0',
            'tags': params['tags']
        }

        ensemble_aws_accounts_eai_response_payload = self.simple_request_eai(self.get_conf_handler_path_name('ensemble_aws_accounts'),
                                                                    'create', 'POST', post_args)

        # Always populate entry content from request to list handler.
        ensemble_aws_accounts_rest_path = '/servicesNS/%s/%s/ensemble_aws_accounts/%s' % (
            'nobody', self.appName, urllib.quote_plus(params['name']))
        ensemble_aws_accounts_eai_response_payload = self.simple_request_eai(ensemble_aws_accounts_rest_path, 'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, ensemble_aws_accounts_eai_response_payload)

    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action. Index modification is not supported through this endpoint. Both the
        scripted input and the ensemble_aws_accounts.conf stanza will be overwritten on ANY call to this endpoint.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Ensemble AWS Account edit requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)
        params = self.validate_server_schema_params()
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('ensemble_aws_accounts', 'nobody'), conf_stanza)

        ensemble_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')
        old_aws_access_key = ensemble_aws_accounts_eai_response_payload['entry'][0]['content']['aws_access_key']
        old_aws_secret_key_link_alternate = ensemble_aws_accounts_eai_response_payload['entry'][0]['content']['aws_secret_key_link_alternate']

        # Create post args - remove name to ensure edit instead of create
        ensemble_aws_accounts_conf_postargs = {
            'aws_access_key': params['aws_access_key'],
            'tags': params['tags'],
        }

        # Change password if provided in params
        if old_aws_access_key != params['aws_access_key']:
            if self.get_param('aws_secret_key'):
                # New username and password provided
                auth_params = self.validate_auth_schema_params()
                params.update(auth_params)
                # Edit passwords.conf stanza
                ensemble_aws_accounts_conf_postargs['aws_secret_key_link_alternate'] = self.password_edit(old_aws_secret_key_link_alternate, params['aws_access_key'], params['aws_secret_key'])
            else:
                # Can't change username without providing password
                raise admin.InternalException('AWS Secret Key must be provided on AWS Access Key change.')
        if (old_aws_access_key == params['aws_access_key'] and self.get_param('aws_secret_key')):
            # Password update to existing username
            auth_params = self.validate_auth_schema_params()
            params.update(auth_params)
            # Edit passwords.conf stanza
            ensemble_aws_accounts_conf_postargs['aws_secret_key_link_alternate'] = self.password_edit(old_aws_secret_key_link_alternate, params['aws_access_key'], params['aws_secret_key'])

        if self.get_param('aws_secret_key'):
            aws_secret_key_link_alternate = self.get_param('aws_secret_key')
        else:
            aws_secret_key_link_alternate = old_aws_secret_key_link_alternate

        # Get AWS Secret Key
        passwords_conf_payload = self.simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET')
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

        aws_account_id = ensemble_aws_accounts_eai_response_payload['entry'][0]['content']['aws_account_id']
        role_arn = "arn:aws:iam::{0}:role/SplunkDataCollectionCrossAccountRole".format(aws_account_id)
        session = self.assumed_role_session(role_arn)

        if params['template_link_alternate'] and params['template_link_alternate'] != '' and params['cloudformation_template_action'] and params['cloudformation_template_action'] == 'apply':
            # Get CloudFormation template string
            cloudformation_templates_conf_payload = self.simple_request_eai(params['template_link_alternate'], 'list', 'GET')
            template_filename = cloudformation_templates_conf_payload['entry'][0]['content']['filename']

            with open(os.path.dirname(os.path.abspath(__file__)) + '/cloudformation_templates/' + template_filename) as json_file:
                json_data = json.dumps(json.load(json_file))


            try:
                client = session.client('cloudformation', region_name=params['aws_region'])
                response = client.create_stack(
                    StackName=params['name'],
                    TemplateBody=json_data,
                    Capabilities=[
                        'CAPABILITY_IAM'
                    ]
                )
            except Exception, e:
                logger.error(e)
                raise admin.InternalException('Error connecting to AWS or deploying CloudFormation template %s' % e)

            ensemble_aws_accounts_conf_postargs['cloudformation_stack_id'] = response['StackId']
    
        if params['cloudformation_template_action'] and params['cloudformation_template_action'] == 'remove':
            try:
                client = session.client('cloudformation', region_name=params['aws_region'])
                response = client.delete_stack(
                    StackName=params['name']
                )
            except Exception, e:
                logger.error(e)
                raise admin.InternalException('Error connecting to AWS or deleting CloudFormation template %s' % e)

        if params['template_link_alternate'] and params['template_link_alternate'] != '' and params[
                'cloudformation_template_action'] and params['cloudformation_template_action'] == 'update':
            # Get CloudFormation template string
            cloudformation_templates_conf_payload = self.simple_request_eai(params['template_link_alternate'], 'list',
                                                                            'GET')
            template_filename = cloudformation_templates_conf_payload['entry'][0]['content']['filename']

            with open(os.path.dirname(os.path.abspath(__file__)) + '/cloudformation_templates/' + template_filename) as json_file:
                json_data = json.dumps(json.load(json_file))

            try:
                client = session.client('cloudformation', region_name=params['aws_region'])
                response = client.update_stack(
                    StackName=params['name'],
                    TemplateBody=json_data,
                    Capabilities=[
                        'CAPABILITY_IAM'
                    ]
                )
            except Exception, e:
                logger.error(e)
                raise admin.InternalException('Error connecting to AWS or deploying CloudFormation template %s' %  e)

            ensemble_aws_accounts_conf_postargs['cloudformation_stack_id'] = response['StackId']

        # Edit ensemble_aws_accounts.conf
        ensemble_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'edit', 'POST',
                                                                                     ensemble_aws_accounts_conf_postargs)

        # Always populate entry content from request to list handler.
        ensemble_aws_accounts_rest_path = '/servicesNS/%s/%s/ensemble_aws_accounts/%s' % ('nobody', self.appName, conf_stanza)
        ensemble_aws_accounts_eai_response_payload = self.simple_request_eai(ensemble_aws_accounts_rest_path, 'read', 'GET')
        self.set_conf_info_from_eai_payload(confInfo, ensemble_aws_accounts_eai_response_payload)

    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'remove' action. Removes the requested stanza from inputs.conf (scripted input),
        removes the requested stanza from ensemble_aws_accounts.conf, and removes all related credentials

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Ensemble AWS Account removal requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)

        # Grab the link alternate and username from the ensemble_aws_accounts GET response payload before it gets deleted
        ensemble_aws_accounts_rest_path = '/servicesNS/%s/%s/ensemble_aws_accounts/%s' % ('nobody', self.appName, conf_stanza)
        ensemble_aws_accounts_eai_response_payload = self.simple_request_eai(ensemble_aws_accounts_rest_path, 'read', 'GET')
        aws_secret_key_link_alternate = ensemble_aws_accounts_eai_response_payload['entry'][0]['content']['aws_secret_key_link_alternate']

        # Delete passwords.conf stanza
        self.password_delete(aws_secret_key_link_alternate)

        # Delete ensemble_aws_accounts.conf stanza
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('ensemble_aws_accounts'), conf_stanza)
        ensemble_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'remove', 'DELETE')
        self.set_conf_info_from_eai_payload(confInfo, ensemble_aws_accounts_eai_response_payload)

    def password_edit(self, password_link_alternate, new_username, password):
        """
        Edits a password entry using the storage/passwords endpoint. This endpoint will first delete the existing
        entry, then creates a new one.

        Arguments
        password_link_alternate -- The link alternate of the password entry
        password -- The actual password which will be encrypted and stored in passwords.conf
        """
        self.password_delete(password_link_alternate)
        return self.password_create(new_username, password)

    def password_delete(self, password_link_alternate):
        """
        Deletes a password entry using the storage/passwords endpoint.

        Arguments
        password_link_alternate -- The link alternate of the password entry
        """
        passwords_conf_payload = self.simple_request_eai(password_link_alternate, 'remove', 'DELETE')

    def hash_len_confirm(self, password, password_after, password_orig_hash, password_after_hash):
        """
        Confirms length of plaintext password matches retrieved decrypted password. Also compares the hashes of
        the initial and retrieved passwords.

        Arguments
        password -- The actual password which was encrypted and stored in passwords.conf
        password_after -- The decrypted password retrieved from passwords.conf
        password_orig_hash -- The hash of the actual password which was encrypted and stored in passwords.conf
        password_after_hash -- The hash of the decrypted password retrieved from passwords.conf
         """
        assert len(password_after) == len(password)
        assert password_orig_hash == password_after_hash

    def password_create(self, username, password):
        """
        Creates a password entry using the storage/passwords endpoint. This endpoint will validate successful creationof the password by comparing length and hashes of the provided password and the retrieved cleartext password. Password realm will include a unique GUID.

        Arguments
        username -- The username associated with the provided password
        password -- The actual password which will be encrypted and stored in passwords.conf
        """
        m = hashlib.md5()
        m.update(password)
        password_orig_hash = m.hexdigest()

        realm = str(uuid.uuid4().hex)

        passwords_conf_postargs = {
            'realm': realm,
            'name': username,
            'password': password
        }

        passwords_rest_path = '/servicesNS/%s/%s/storage/passwords/' % ('nobody', self.appName)

        # Create password
        passwords_conf_payload = self.simple_request_eai(passwords_rest_path, 'create', 'POST', passwords_conf_postargs)
        password_link_alternate = passwords_conf_payload['entry'][0]['links']['alternate']

        # Load password to check hash and length
        passwords_conf_payload = self.simple_request_eai(password_link_alternate, 'list', 'GET')
        password_after = passwords_conf_payload['entry'][0]['content']['clear_password']

        m = hashlib.md5()
        m.update(password_after)
        password_after_hash = m.hexdigest()

        try:
            self.hash_len_confirm(password, password_after, password_orig_hash, password_after_hash)
        except Exception, e:
            logger.error(e)
            raise admin.InternalException('Password stored incorrectly %s' % e)

        return password_link_alternate

    def validate_server_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=ensemble_aws_accounts_schema, filter=ensemble_aws_accounts_schema.SERVER_FIELDS)
        return self.validate_params(ensemble_aws_accounts_schema.server_schema, params)

    def validate_auth_schema_params(self):
        """
        Validates raw request params against the auth schema
        """
        params = self.get_params(schema=ensemble_aws_accounts_schema, filter=ensemble_aws_accounts_schema.AUTH_FIELDS)
        return self.validate_params(ensemble_aws_accounts_schema.auth_schema, params)

admin.init(EnsembleAWSAccountsEAIHandler, admin.CONTEXT_NONE)
