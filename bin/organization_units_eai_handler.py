import logging
import os
import sys
import splunk.admin as admin
import organization_units_schema
import urllib3
import base_eai_handler
import log_helper
libpath = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(libpath, '3rdparty')]
import boto3

if sys.platform == 'win32':
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup the handler
logger = log_helper.setup(logging.INFO, 'OrganizationUnitsEAIHandler', 'organization_units_handler.log')

class OrganizationUnitsEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in organization_units_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Organization account list requested.')

        # Get the grand central account information for the organization account
        conf_handler_path = self.get_conf_handler_path_name('grand_central_aws_accounts', 'nobody')
        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET', get_args={'count': -1})

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

            # Make call to AWS API endpoint
            client = boto3.client('organizations', aws_access_key_id=aws_access_key, aws_secret_access_key=SECRET_KEY)

            root_id = client.list_roots()['Roots'][0]['Id']
            ou_response = client.list_organizational_units_for_parent(ParentId=root_id)

            child_to_ou_map = {}

            for ou in ou_response['OrganizationalUnits']:
                ou_id = ou['Id']
                inner_response = client.list_children(ParentId=ou_id, ChildType='ACCOUNT')

                for child in inner_response['Children']:
                    child_to_ou_map[child['Id']] = {'Id': ou['Id'], 'Name': ou['Name'], 'Arn': ou['Arn']}

                while 'NextToken' in inner_response:
                    inner_response = client.list_children(NextToken=inner_response['NextToken'], ParentId=ou_id, ChildType='ACCOUNT')

                    for child in inner_response['Children']:
                        child_to_ou_map[child['Id']] = {'Id': ou['Id'], 'Name': ou['Name'], 'Arn': ou['Arn']}

            response = client.list_accounts()

            self.update_account_list_payload(account_list_payload, response, aws_account_id, child_to_ou_map)

            while 'NextToken' in response:
                response = client.list_accounts(NextToken=response['NextToken'])

                self.update_account_list_payload(account_list_payload, response, aws_account_id, child_to_ou_map)

        self.set_conf_info_from_eai_payload(confInfo, account_list_payload)

    def handleCreate(self, confInfo):
        """
        Called when user invokes the "create" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        pass



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

    def update_account_list_payload(self, account_list_payload, response, master_account_id, child_to_ou_map):
        for account in response['Accounts']:
            account_id = account['Id']
            del account['Id']
            account['ParentAccountId'] = master_account_id
            account['AccountId'] = account_id
            if account_id in child_to_ou_map:
                account['OuName'] = child_to_ou_map[account_id]['Name']
                account['OuArn'] = child_to_ou_map[account_id]['Arn']
                account['OuId'] = child_to_ou_map[account_id]['Id']
            else:
                account['OuName'] = ''
                account['OuArn'] = ''
                account['OuId'] = ''
            account['JoinedTimestamp'] = account['JoinedTimestamp'].strftime('%m/%d/%Y')
            account_entry = {'name': account_id, 'content': account}
            account_list_payload['entry'].append(account_entry)

    def validate_organization_units_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=organization_units_schema, filter=organization_units_schema.ORGANIZATION_UNIT_FIELDS)
        return self.validate_params(organization_units_schema.organizaiton_unit_schema, params)


admin.init(OrganizationUnitsEAIHandler, admin.CONTEXT_NONE)
