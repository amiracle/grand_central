import logging
import os
import sys
import uuid
import splunk.admin as admin
import grand_central_aws_accounts_schema
import urllib
import hashlib
import base_eai_handler
import log_helper
import boto3
import json
import time
from datetime import datetime

if sys.platform == 'win32':
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup the handler
logger = log_helper.setup(logging.INFO, 'GrandCentralAWSAccountsEAIHandler', 'grand_central_aws_accounts_handler.log')

class GrandCentralAWSAccountsEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in grand_central_aws_accounts_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Grand Central AWS accounts list requested.')

        # Fetch from grand_central_aws_accounts conf handler
        conf_handler_path = self.get_conf_handler_path_name('grand_central_aws_accounts', 'nobody')
        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')

        # Add link alternate (without mgmt, scheme, host, port) to list response
        for grand_central_aws_account in grand_central_aws_accounts_eai_response_payload['entry']:
            grand_central_aws_account_link_alternate = grand_central_aws_account['links']['alternate'].replace('/configs/conf-grand_central_aws_accounts/', '/grand_central_aws_accounts/')

            grand_central_aws_account['content']['grand_central_aws_accounts_link_alternate'] = grand_central_aws_account_link_alternate
            grand_central_aws_account['content']['aws_account_age'] = self.convert_date_to_age(grand_central_aws_account['content'].get('aws_account_joined_timestamp', '0'))

        self.set_conf_info_from_eai_payload(confInfo, grand_central_aws_accounts_eai_response_payload)

    def handleCreate(self, confInfo):
        """
        Called when user invokes the "create" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Grand Central AWS account creation requested.')

        # Validate and extract correct POST params
        server_params = self.validate_server_schema_params()
        auth_params = self.validate_auth_schema_params()
        params = auth_params.copy()
        params.update(server_params)

        # Password creation
        aws_secret_key_link_alternate = self.password_create(params['aws_access_key'], params['aws_secret_key'])

        # grand_central_aws_accounts.conf creation and response
        post_args = {
            'name': params['name'],
            'display_name': params['display_name'],
            'aws_account_id': params['aws_account_id'],
            'aws_access_key': params['aws_access_key'],
            'aws_account_status': self.get_param('aws_account_status', default=''),
            'aws_account_email': self.get_param('aws_account_email', default=''),
            'aws_account_arn': self.get_param('aws_account_arn', default=''),
            'aws_account_joined_method': self.get_param('aws_account_joined_method', default=''),
            'aws_account_joined_timestamp': self.get_param('aws_account_joined_timestamp', default=''),
            'organization_master_account': params['organization_master_account'],
            'aws_secret_key_link_alternate': aws_secret_key_link_alternate,
            'data_collection_deployed': '0',
            'data_collection_deployment_success': '0',
            'tags': params['tags'],
            'splunk_account_link_alternate': self.get_param('splunk_account_link_alternate', default=''),
            'parent_aws_account_id': self.get_param('parent_aws_account_id', default=''),
        }

        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(self.get_conf_handler_path_name('grand_central_aws_accounts'),
                                                                    'create', 'POST', post_args)

        # Always populate entry content from request to list handler.
        grand_central_aws_accounts_rest_path = '/servicesNS/%s/%s/grand_central_aws_accounts/%s' % (
            'nobody', self.appName, urllib.quote_plus(params['name']))
        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(grand_central_aws_accounts_rest_path, 'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, grand_central_aws_accounts_eai_response_payload)

    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action. Index modification is not supported through this endpoint. Both the
        scripted input and the grand_central_aws_accounts.conf stanza will be overwritten on ANY call to this endpoint.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Grand Central AWS Account edit requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)
        params = self.validate_server_schema_params()
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('grand_central_aws_accounts', 'nobody'), conf_stanza)

        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')
        old_aws_access_key = grand_central_aws_accounts_eai_response_payload['entry'][0]['content']['aws_access_key']
        old_aws_secret_key_link_alternate = grand_central_aws_accounts_eai_response_payload['entry'][0]['content']['aws_secret_key_link_alternate']

        # Create post args - remove name to ensure edit instead of create

        grand_central_aws_accounts_conf_postargs = {
            'aws_access_key': params['aws_access_key'],
            'display_name': params['display_name'],
        }

        # Handle optional post args
        if 'tags' in params and params['tags'] != '':
            grand_central_aws_accounts_conf_postargs['tags'] = params['tags']
        if 'aws_account_status' in params and params['aws_account_status'] != '':
            grand_central_aws_accounts_conf_postargs['aws_account_status'] = params['aws_account_status']
        if 'aws_account_email' in params and params['aws_account_email'] != '':
            grand_central_aws_accounts_conf_postargs['aws_account_email'] = params['aws_account_email']
        if 'aws_account_arn' in params and params['aws_account_arn'] != '':
            grand_central_aws_accounts_conf_postargs['aws_account_arn'] = params['aws_account_arn']
        if 'aws_account_joined_method' in params and params['aws_account_joined_method'] != '':
            grand_central_aws_accounts_conf_postargs['aws_account_joined_method'] = params['aws_account_joined_method']
        if 'aws_account_joined_timestamp' in params and params['aws_account_joined_timestamp'] != '':
            grand_central_aws_accounts_conf_postargs['aws_account_joined_timestamp'] = params['aws_account_joined_timestamp']
        if 'splunk_account_link_alternate' in params and params['splunk_account_link_alternate'] != '':
            grand_central_aws_accounts_conf_postargs['splunk_account_link_alternate'] = params['splunk_account_link_alternate']
        if 'parent_aws_account_id' in params and params['parent_aws_account_id'] != '':
            grand_central_aws_accounts_conf_postargs['parent_aws_account_id'] = params['parent_aws_account_id']

        # Change password if provided in params
        if old_aws_access_key != params['aws_access_key']:
            if self.get_param('aws_secret_key'):
                # New username and password provided
                auth_params = self.validate_auth_schema_params()
                params.update(auth_params)
                # Edit passwords.conf stanza
                grand_central_aws_accounts_conf_postargs['aws_secret_key_link_alternate'] = self.password_edit(old_aws_secret_key_link_alternate, params['aws_access_key'], params['aws_secret_key'])
            else:
                # Can't change username without providing password
                raise admin.InternalException('AWS Secret Key must be provided on AWS Access Key change.')
        if (old_aws_access_key == params['aws_access_key'] and self.get_param('aws_secret_key')):
            # Password update to existing username
            auth_params = self.validate_auth_schema_params()
            params.update(auth_params)
            # Edit passwords.conf stanza
            grand_central_aws_accounts_conf_postargs['aws_secret_key_link_alternate'] = self.password_edit(old_aws_secret_key_link_alternate, params['aws_access_key'], params['aws_secret_key'])

        # Edit grand_central_aws_accounts.conf
        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'edit', 'POST',
                                                                                  grand_central_aws_accounts_conf_postargs)

        # Always populate entry content from request to list handler.
        grand_central_aws_accounts_rest_path = '/servicesNS/%s/%s/grand_central_aws_accounts/%s' % ('nobody', self.appName, conf_stanza)
        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(grand_central_aws_accounts_rest_path, 'read', 'GET')
        self.set_conf_info_from_eai_payload(confInfo, grand_central_aws_accounts_eai_response_payload)

    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'remove' action. Removes the requested stanza from inputs.conf (scripted input),
        removes the requested stanza from grand_central_aws_accounts.conf, and removes all related credentials

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Grand Central AWS Account removal requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)

        # Grab the link alternate and username from the grand_central_aws_accounts GET response payload before it gets deleted
        grand_central_aws_accounts_rest_path = '/servicesNS/%s/%s/grand_central_aws_accounts/%s' % ('nobody', self.appName, conf_stanza)
        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(grand_central_aws_accounts_rest_path, 'read', 'GET')
        aws_secret_key_link_alternate = grand_central_aws_accounts_eai_response_payload['entry'][0]['content']['aws_secret_key_link_alternate']

        # Delete passwords.conf stanza
        self.password_delete(aws_secret_key_link_alternate)

        # Delete grand_central_aws_accounts.conf stanza
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('grand_central_aws_accounts'), conf_stanza)
        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'remove', 'DELETE')
        self.set_conf_info_from_eai_payload(confInfo, grand_central_aws_accounts_eai_response_payload)

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

    def convert_date_to_age(self, datetime_string):

        if datetime_string == '0' or datetime_string == '':
            return datetime_string

        epoch = datetime(1970, 1, 1)
        joined_date = int((datetime.strptime(datetime_string, '%m/%d/%Y') - epoch).total_seconds())

        today = int(time.time())
        return str((today - joined_date)/(60*60*24))

    def validate_server_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=grand_central_aws_accounts_schema, filter=grand_central_aws_accounts_schema.SERVER_FIELDS)
        return self.validate_params(grand_central_aws_accounts_schema.server_schema, params)

    def validate_auth_schema_params(self):
        """
        Validates raw request params against the auth schema
        """
        params = self.get_params(schema=grand_central_aws_accounts_schema, filter=grand_central_aws_accounts_schema.AUTH_FIELDS)
        return self.validate_params(grand_central_aws_accounts_schema.auth_schema, params)

admin.init(GrandCentralAWSAccountsEAIHandler, admin.CONTEXT_NONE)
