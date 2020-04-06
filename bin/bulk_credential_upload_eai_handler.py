import logging
import os
import sys
import splunk.admin as admin
import bulk_credential_upload_schema
import urllib
import base_eai_handler
import log_helper
import json
import boto3

if sys.platform == 'win32':
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup the handler
logger = log_helper.setup(logging.INFO, 'BulkCredentialUploadEAIHandler', 'bulk_credential_upload_handler.log')

class BulkCredentialUploadEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in bulk_credential_upload_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Bulk credential upload list requested.')

    def handleCreate(self, confInfo):
        """
        Called when user invokes the "create" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Bulk credential upload requested.')

        # Validate and extract correct POST params
        params = self.validate_bulk_credential_upload_schema_params()

        grand_central_aws_accounts_rest_path = '/servicesNS/%s/%s/grand_central_aws_accounts' % ('nobody', self.appName)

        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(grand_central_aws_accounts_rest_path,
                                                                                  'list', 'GET', get_args={'count': -1})
        grand_central_aws_accounts = {}

        for grand_central_aws_account in grand_central_aws_accounts_eai_response_payload['entry']:
            grand_central_aws_accounts[grand_central_aws_account['content']['aws_account_id']] = grand_central_aws_account['content']

        # Get CloudFormation template from params or from template link alternate
        if 'credential_file' in params and params['credential_file'] != '0' and params['credential_file'] != '':
            credentials = json.loads(params['credential_file'])[0]['credentials']
        else:
            credentials = []

        for credential in credentials:
            # Get the acct id of the credential
            aws_access_key = credential['key_id']
            SECRET_KEY = credential['secret_key']
            try:
                client = boto3.client('sts', aws_access_key_id=aws_access_key,
                                      aws_secret_access_key=SECRET_KEY)

                response = client.get_caller_identity()

            except Exception, e:
                logger.error(e)
                raise admin.InternalException('Error connecting to AWS %s' % e)

            if response['Account'] in grand_central_aws_accounts:
                # update the GC acct credential
                post_args = {
                    'display_name': grand_central_aws_accounts[response['Account']]['display_name'],
                    'aws_account_id': response['Account'],
                    'aws_access_key': aws_access_key,
                    'aws_secret_key': SECRET_KEY,
                }

                if 'aws_account_arn' not in grand_central_aws_accounts[response['Account']] or grand_central_aws_accounts[response['Account']]['aws_account_arn'] == '':
                    post_args['aws_account_arn'] = response['Arn']

                grand_central_aws_account_rest_path = '%s/%s' % (grand_central_aws_accounts_rest_path, response['Account'])

                grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(
                    grand_central_aws_account_rest_path, 'edit', 'POST', post_args)

            else:
                # create a new GC acct
                post_args = {
                    'name': response['Account'],
                    'display_name': response['Account'],
                    'aws_account_id': response['Account'],
                    'aws_access_key': aws_access_key,
                    'aws_secret_key': SECRET_KEY,
                    'aws_account_arn': response['Arn']
                }

                grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(grand_central_aws_accounts_rest_path, 'create', 'POST', post_args)

        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(grand_central_aws_accounts_rest_path,
                                                                                  'list', 'GET', get_args={'count': -1})

        self.set_conf_info_from_eai_payload(confInfo, grand_central_aws_accounts_eai_response_payload)


    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action. Index modification is not supported through this endpoint. Both the
        scripted input and the deployed_cloudformation_templates.conf stanza will be overwritten on ANY call to this endpoint.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Bulk credential upload edit requested.')


    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'remove' action. Removes the requested stanza from inputs.conf (scripted input),
        removes the requested stanza from deployed_cloudformation_templates.conf, and removes all related credentials

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Bulk credential upload removal requested.')


    def validate_bulk_credential_upload_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=bulk_credential_upload_schema, filter=bulk_credential_upload_schema.BULK_CREDENTIAL_UPLOAD_FIELDS)
        return self.validate_params(bulk_credential_upload_schema.bulk_credential_upload_schema, params)


admin.init(BulkCredentialUploadEAIHandler, admin.CONTEXT_NONE)
