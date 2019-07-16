import logging
import os
import sys
import splunk.admin as admin
import cloudformation_templates_schema
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
logger = log_helper.setup(logging.INFO, 'CloudFormationTemplatesEAIHandler', 'cloudformation_templates_handler.log')

class CloudFormationTemplatesEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in cloudformation_templates_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('CloudFormation Templates list requested.')

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
        logger.info('AWS CloudFormation template creation requested.')

        # Validate and extract correct POST params
        params = self.validate_cloudformation_templates_schema_params()

        # cloudformation_templates.conf creation and response
        post_args = {
            'name': params['name'],
            'label': params['label'],
            'description': params['description'],
            'filename': params['filename']
        }

        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'local'))  + '/' +  params['filename'], 'w') as outfile:
            outfile.write(params['template'])

        cloudformation_templates_eai_response_payload = self.simple_request_eai(self.get_conf_handler_path_name('cloudformation_templates'),
                                                                    'create', 'POST', post_args)

        # Always populate entry content from request to list handler.
        cloudformation_templates_rest_path = '/servicesNS/%s/%s/cloudformation_templates/%s' % (
            'nobody', self.appName, urllib.quote_plus(params['name']))
        cloudformation_templates_eai_response_payload = self.simple_request_eai(cloudformation_templates_rest_path, 'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, cloudformation_templates_eai_response_payload)

    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action. Index modification is not supported through this endpoint. Both the
        scripted input and the grand_central_aws_accounts.conf stanza will be overwritten on ANY call to this endpoint.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Cloudformation template edit requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)
        params = self.validate_server_schema_params()
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('cloudformation_templates', 'nobody'), conf_stanza)

        # Create post args - remove name to ensure edit instead of create
        cloudformation_templates_conf_postargs = {
            'label': params['label'],
            'description': params['description'],
            'filename': params['filename']
        }

        # Edit cloudformation_templates.conf
        cloudformation_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'edit', 'POST',
                                                                                cloudformation_templates_conf_postargs)

        # Always populate entry content from request to list handler.
        cloudformation_templates_rest_path = '/servicesNS/%s/%s/cloudformation_templates/%s' % ('nobody', self.appName, conf_stanza)
        cloudformation_templates_eai_response_payload = self.simple_request_eai(cloudformation_templates_rest_path, 'read', 'GET')
        self.set_conf_info_from_eai_payload(confInfo, cloudformation_templates_eai_response_payload)

    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'remove' action. Removes the requested stanza from inputs.conf (scripted input),
        removes the requested stanza from grand_central_aws_accounts.conf, and removes all related credentials

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('CloudFormation template removal requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)

        cloudformation_templates_rest_path = '/servicesNS/%s/%s/cloudformation_templates/%s' % (
            'nobody', self.appName, urllib.quote_plus(name))
        cloudformation_templates_eai_response_payload = self.simple_request_eai(cloudformation_templates_rest_path,
                                                                                'read', 'GET')

        filename = cloudformation_templates_eai_response_payload['entry'][0]['content']['filename']

        # Delete actual CloudFormation template file
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'local'))  + '/' + filename

        if os.path.exists(filepath):
            os.remove(filepath)

        # Delete cloudformation_templates.conf stanza
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('cloudformation_templates'), conf_stanza)
        cloudformation_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'remove', 'DELETE')
        self.set_conf_info_from_eai_payload(confInfo, cloudformation_templates_eai_response_payload)

    def validate_cloudformation_templates_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=cloudformation_templates_schema, filter=cloudformation_templates_schema.CLOUDFORMATION_TEMPLATE_FIELDS)
        return self.validate_params(cloudformation_templates_schema.cloudformation_template_schema, params)


admin.init(CloudFormationTemplatesEAIHandler, admin.CONTEXT_NONE)
