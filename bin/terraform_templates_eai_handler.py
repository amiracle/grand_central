import logging
import os
import sys
import splunk.admin as admin
import terraform_templates_schema
import urllib
import base_eai_handler
import log_helper

if sys.platform == 'win32':
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup the handler
logger = log_helper.setup(logging.INFO, 'TerraformTemplatesEAIHandler', 'terraform_templates_handler.log')

class TerraformTemplatesEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in terraform_templates_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Terraform templates list requested.')

        # Fetch from terraform_templates conf handler
        conf_handler_path = self.get_conf_handler_path_name('terraform_templates', 'nobody')
        terraform_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')

        # Add link alternate (without mgmt, scheme, host, port) to list response
        for terraform_template in terraform_templates_eai_response_payload['entry']:
            grand_central_gcp_accounts_link_alternate = terraform_template['links']['alternate'].replace('/configs/conf-terraform_templates/', '/terraform_templates/')

            terraform_template['content']['terraform_templates_link_alternate'] = grand_central_gcp_accounts_link_alternate
            terraform_template['content']['terraform_template_name'] = terraform_template['name']
            terraform_template['content']['label'] = terraform_template['content'].get('label', '')
            terraform_template['content']['description'] = terraform_template['content'].get('description', '')
            terraform_template['content']['filename'] = terraform_template['content'].get('filename', '')

        self.set_conf_info_from_eai_payload(confInfo, terraform_templates_eai_response_payload)

    def handleCreate(self, confInfo):
        """
        Called when user invokes the "create" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Terraform template creation requested.')

        # Validate and extract correct POST params
        params = self.validate_terraform_template_schema_params()

        # terraform_templates.conf creation and response
        post_args = {
            'name': params['name'],
            'label': params['label'],
            'description': params['description'],
            'filename': params['filename']
        }

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'local'))  + '/' +  params['filename'], 'w') as outfile:
            outfile.write(params['template'])

        terraform_templates_eai_response_payload = self.simple_request_eai(self.get_conf_handler_path_name('terraform_templates'),
                                                                    'create', 'POST', post_args)

        # Always populate entry content from request to list handler.
        terraform_templates_rest_path = '/servicesNS/%s/%s/terraform_templates/%s' % (
            'nobody', self.appName, urllib.quote_plus(params['name']))
        terraform_templates_eai_response_payload = self.simple_request_eai(terraform_templates_rest_path, 'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, terraform_templates_eai_response_payload)

    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action. Index modification is not supported through this endpoint. Both the
        scripted input and the grand_central_gcp_accounts.conf stanza will be overwritten on ANY call to this endpoint.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Terraform template edit requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)
        params = self.validate_server_schema_params()
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('terraform_templates', 'nobody'), conf_stanza)

        # Create post args - remove name to ensure edit instead of create
        terraform_templates_conf_postargs = {
            'label': params['label'],
            'description': params['description'],
            'filename': params['filename']
        }

        # Edit terraform_templates.conf
        terraform_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'edit', 'POST',
                                                                                terraform_templates_conf_postargs)

        # Always populate entry content from request to list handler.
        terraform_templates_rest_path = '/servicesNS/%s/%s/terraform_templates/%s' % ('nobody', self.appName, conf_stanza)
        terraform_templates_eai_response_payload = self.simple_request_eai(terraform_templates_rest_path, 'read', 'GET')
        self.set_conf_info_from_eai_payload(confInfo, terraform_templates_eai_response_payload)

    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'remove' action. Removes the requested stanza from inputs.conf (scripted input),
        removes the requested stanza from grand_central_gcp_accounts.conf, and removes all related credentials

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Terraform template removal requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)

        terraform_templates_rest_path = '/servicesNS/%s/%s/terraform_templates/%s' % (
            'nobody', self.appName, urllib.quote_plus(name))
        terraform_templates_eai_response_payload = self.simple_request_eai(terraform_templates_rest_path,
                                                                                'read', 'GET')

        filename = terraform_templates_eai_response_payload['entry'][0]['content']['filename']

        # Delete actual Terraform template file
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'local'))  + '/' + filename

        if os.path.exists(filepath):
            os.remove(filepath)

        # Delete terraform_templates.conf stanza
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('terraform_templates'), conf_stanza)
        terraform_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'remove', 'DELETE')
        self.set_conf_info_from_eai_payload(confInfo, terraform_templates_eai_response_payload)

    def validate_terraform_template_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=terraform_templates_schema, filter=terraform_templates_schema.TERRAFORM_TEMPLATE_FIELDS)
        return self.validate_params(terraform_templates_schema.terraform_template_schema, params)


admin.init(TerraformTemplatesEAIHandler, admin.CONTEXT_NONE)
