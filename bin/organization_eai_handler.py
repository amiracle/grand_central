import logging
import os
import sys
import splunk.admin as admin
import organization_schema
import boto3
import base_eai_handler
import log_helper

if sys.platform == 'win32':
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup the handler
logger = log_helper.setup(logging.INFO, 'OrganizationEAIHandler', 'organization_handler.log')

class OrganizationEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in organization_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Organization account list requested.')

        # Get the grand central account information for the organization account
        params = self.validate_organization_schema_params()

        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('grand_central_aws_accounts', 'nobody'), params.get('account_id'))
        grand_central_aws_accounts_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')

        aws_secret_key_link_alternate = grand_central_aws_accounts_eai_response_payload['entry'][0]['content'][
            'aws_secret_key_link_alternate']

        passwords_conf_payload = self.simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET')
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

        # Make call to AWS API endpoint

        # Loop through results and construct a response

        account_list_payload = {'entry': [{'name': params.get('account_id'), 'content': {'KEY': SECRET_KEY}}]}
        self.set_conf_info_from_eai_payload(confInfo, account_list_payload)




        # Fetch from cloudformation_templates conf handler
        conf_handler_path = self.get_conf_handler_path_name('cloudformation_templates', 'nobody')
        cloudformation_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')

        # Add link alternate (without mgmt, scheme, host, port) to list response
        for cloudformation_template in cloudformation_templates_eai_response_payload['entry']:
            grand_central_aws_accounts_link_alternate = cloudformation_template['links']['alternate'].replace('/configs/conf-cloudformation_templates/', '/cloudformation_templates/')

            cloudformation_template['content']['cloudformation_templates_link_alternate'] = grand_central_aws_accounts_link_alternate
            cloudformation_template['content']['cloudformation_template_name'] =cloudformation_template['name']
            cloudformation_template['content']['label'] = cloudformation_template['content'].get('label', '')
            cloudformation_template['content']['description'] = cloudformation_template['content'].get('description', '')
            cloudformation_template['content']['filename'] = cloudformation_template['content'].get('filename', '')

        self.set_conf_info_from_eai_payload(confInfo, cloudformation_templates_eai_response_payload)

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

    def validate_organization_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=organization_schema, filter=organization_schema.ORGANIZATION_FIELDS)
        return self.validate_params(organization_schema.organizaiton_schema, params)


admin.init(OrganizationEAIHandler, admin.CONTEXT_NONE)
