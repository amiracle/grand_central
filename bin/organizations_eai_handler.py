import logging
import os
import sys
import splunk.admin as admin
import organizations_schema
import boto3
import botocore
import urllib3
import base_eai_handler
import log_helper
import datetime
from tzlocal import get_localzone

if sys.platform == 'win32':
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup the handler
logger = log_helper.setup(logging.INFO, 'OrganizationsEAIHandler', 'organizations_handler.log')

class OrganizationsEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in organizations_schema.ALL_FIELDS:
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
            time_fetcher = lambda: datetime.datetime.now(get_localzone())
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
        logger.info('Organization account list requested.')

        # Get the grand central account information for the organization account
        conf_handler_path = self.get_conf_handler_path_name('grand_central_aws_accounts', 'nobody')
        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')

        account_list_payload = {'entry': []}

        for grand_central_aws_account in grand_central_aws_accounts_eai_response_payload['entry']:

            if grand_central_aws_account['content']['organization_master_account'] == '0':
                continue

            aws_secret_key_link_alternate = grand_central_aws_account['content'][
                'aws_secret_key_link_alternate']
            aws_access_key = grand_central_aws_account['content'][
                'aws_access_key']
            aws_account_id = grand_central_aws_account['content']['aws_account_id']

            passwords_conf_payload = self.simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET')
            SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

            role_arn = "arn:aws:iam::{0}:role/SplunkOrgListerCrossAccountRole".format(aws_account_id)
            session = self.assumed_role_session(role_arn)

            # Make call to AWS API endpoint
            client = session.client('organizations')

            response = client.list_accounts()

            self.update_account_list_payload(account_list_payload, response, aws_account_id)

            if 'NextToken' in response:
                response = client.list_accounts(NextToken=response['NextToken'])

                self.update_account_list_payload(account_list_payload, response, aws_account_id)

        self.set_conf_info_from_eai_payload(confInfo, account_list_payload)

    def handleCreate(self, confInfo):
        """
        Called when user invokes the "create" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        aws_account_id = self.callerArgs.id

        logger.info('Add organization accounts requested.')

        if aws_account_id != '0':
            # Get list of all Grand Central accounts
            conf_handler_path = self.get_conf_handler_path_name('grand_central_aws_accounts', 'nobody')
            grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')

            account_id_to_account_map = {}
            # Build map of account_id/name to account information
            for grand_central_aws_account in grand_central_aws_accounts_eai_response_payload['entry']:
                account_id_to_account_map[grand_central_aws_account['content']['aws_account_id']] = grand_central_aws_account['content']

            # Get list of all AWS accounts in org
            organizations_rest_path = '/servicesNS/nobody/%s/organizations' % self.appName
            organizations_eai_response_payload = self.simple_request_eai(organizations_rest_path, 'read', 'GET')

            # If the account is not in the list of Grand Central accounts, add it
            grand_central_aws_accounts_rest_path = '/servicesNS/nobody/%s/grand_central_aws_accounts' % self.appName

            for organization in organizations_eai_response_payload['entry']:
                if organization['content']['AccountId'] not in account_id_to_account_map:
                    post_args = {
                        'name': organization['content']['AccountId'],
                        'aws_account_id': organization['content']['AccountId'],
                        'display_name': organization['content']['Name'],
                        'organization_master_account': '0',
                        'aws_access_key': 'placeholder',
                        'aws_secret_key': 'placeholder',
                        'aws_account_status': organization['content']['Status'],
                        'aws_account_arn': organization['content']['Arn'],
                        'aws_account_email': organization['content']['Email'],
                        'aws_account_joined_method': organization['content']['JoinedMethod'],
                        'aws_account_joined_timestamp': organization['content']['JoinedTimestamp'],
                        'parent_aws_account_id': organization['content']['ParentAccountId'],
                    }
                    grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(grand_central_aws_accounts_rest_path, 'create', 'POST', post_args)

                if organization['content']['AccountId'] in account_id_to_account_map:
                    account_id = organization['content']['AccountId']
                    # Update the account info
                    grand_central_specific_aws_account_rest_path = '%s/%s' % (grand_central_aws_accounts_rest_path, account_id)
                    post_args = {
                        'display_name': account_id_to_account_map[account_id]['display_name'],
                        'aws_access_key': account_id_to_account_map[account_id]['aws_access_key'],
                        'aws_account_id': organization['content']['AccountId'],
                        'aws_account_status': organization['content']['Status'],
                        'aws_account_arn': organization['content']['Arn'],
                        'aws_account_email': organization['content']['Email'],
                        'aws_account_joined_method': organization['content']['JoinedMethod'],
                        'aws_account_joined_timestamp': organization['content']['JoinedTimestamp'],
                        'parent_aws_account_id': organization['content']['ParentAccountId'],
                    }

                    grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(
                        grand_central_specific_aws_account_rest_path, 'update', 'POST', post_args)

            conf_handler_path = self.get_conf_handler_path_name('grand_central_aws_accounts', 'nobody')
            grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')
            self.set_conf_info_from_eai_payload(confInfo, grand_central_aws_accounts_eai_response_payload)



    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action. Index modification is not supported through this endpoint. Both the
        scripted input and the grand_central_aws_accounts.conf stanza will be overwritten on ANY call to this endpoint.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        pass

    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'remove' action. Removes the requested stanza from inputs.conf (scripted input),
        removes the requested stanza from grand_central_aws_accounts.conf, and removes all related credentials

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        pass

    def update_account_list_payload(self, account_list_payload, response, master_account_id):
        for account in response['Accounts']:
            account_id = account['Id']
            del account['Id']
            account['ParentAccountId'] = master_account_id
            account['AccountId'] = account_id
            account['JoinedTimestamp'] = account['JoinedTimestamp'].strftime('%m/%d/%Y')
            account_entry = {'name': account_id, 'content': account}
            account_list_payload['entry'].append(account_entry)

    def validate_organizations_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=organizations_schema, filter=organizations_schema.ORGANIZATION_FIELDS)
        return self.validate_params(organizations_schema.organizaiton_schema, params)


admin.init(OrganizationsEAIHandler, admin.CONTEXT_NONE)
