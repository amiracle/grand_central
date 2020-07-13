import logging
import os
import sys
import splunk.admin as admin
import deployed_terraform_templates_schema
import urllib
import base_eai_handler
import log_helper
import json

libpath = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(libpath, '3rdparty')]
import boto3
from python_terraform import *

if sys.platform == 'win32':
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup the handler
logger = log_helper.setup(logging.INFO, 'DeployedTerraformTemplatesEAIHandler', 'deployed_terraform_templates_handler.log')

class DeployedTerraformTemplatesEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in deployed_terraform_templates_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Deployed Terraform templates list requested.')

        # Fetch from deployed terraform templates conf handler
        conf_handler_path = self.get_conf_handler_path_name('deployed_terraform_templates', 'nobody')
        deployed_terraform_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')

        for deployed_terraform_template in deployed_terraform_templates_eai_response_payload['entry']:

            if deployed_terraform_template['content'].get('terraform_stack_id', '') != '':
                deployed_terraform_template['content']['data_collection_deployed'] = '1'

                terraform_stack_name = deployed_terraform_template['content']['terraform_stack_name']
                gcp_region = deployed_terraform_template['content']['gcp_region']
                grand_central_gcp_account_link_alternate = deployed_terraform_template['content']['grand_central_gcp_account_link_alternate']

                grand_central_gcp_account_eai_response_payload = self.simple_request_eai(grand_central_gcp_account_link_alternate, 'read', 'GET')
                gcp_project_id = grand_central_gcp_account_eai_response_payload['entry'][0]['content']['gcp_project_id']

                gcp_json_key_link_alternate = grand_central_gcp_account_eai_response_payload['entry'][0]['content']['gcp_json_key_link_alternate']

                passwords_conf_payload = self.simple_request_eai(gcp_json_key_link_alternate, 'list', 'GET')
                SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

                data_collection_deployment_success = '1'

                # for stack in response['Stacks']:
                #     if stack['StackName'] == terraform_stack_name:
                #         if stack['StackStatus'] == 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS':
                #             data_collection_deployment_success = '5'
                #         if stack['StackStatus'] == 'UPDATE_COMPLETE':
                #             data_collection_deployment_success = '5'
                #         if stack['StackStatus'] == 'UPDATE_IN_PROGRESS':
                #             data_collection_deployment_success = '4'
                #         if stack['StackStatus'] == 'DELETE_IN_PROGRESS':
                #             data_collection_deployment_success = '3'
                #             deployed_terraform_template['content']['data_collection_deployed'] = '2'
                #         if stack['StackStatus'] == 'CREATE_IN_PROGRESS':
                #             data_collection_deployment_success = '2'
                #         if stack['StackStatus'] == 'CREATE_COMPLETE':
                #             data_collection_deployment_success = '1'

                deployed_terraform_template['content']['data_collection_deployment_success'] = data_collection_deployment_success

            else:
                deployed_terraform_template['content']['data_collection_deployed'] = '0'

        self.set_conf_info_from_eai_payload(confInfo, deployed_terraform_templates_eai_response_payload)

    def handleCreate(self, confInfo):
        """
        Called when user invokes the "create" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Terraform template deployment requested.')

        # Validate and extract correct POST params
        params = self.validate_deployed_terraform_templates_schema_params()

        # Get terraform template from params or from template link alternate
        # if 'custom_terraform_template' in params and params['custom_terraform_template'] != '0' and params['custom_terraform_template'] != '':
        #     json_data = json.loads(params['custom_terraform_template'])
        # else:
        #     terraform_templates_conf_payload = self.simple_request_eai(params['terraform_template_link_alternate'], 'list',
        #                                                                     'GET')
        #     template_filename = terraform_templates_conf_payload['entry'][0]['content']['filename']
        #
        #     with open(os.path.abspath(
        #         os.path.join(os.path.dirname(__file__), '..', 'local')) + '/' + template_filename) as json_file:
        #         json_data = json.load(json_file)

        # Get Splunk account details
        splunk_account_conf_payload = self.simple_request_eai(params['splunk_account_link_alternate'], 'list', 'GET')
        splunk_hec_endpoint = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_endpoint']
        splunk_hec_ack_token = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_ack_token']
        splunk_hec_no_ack_token = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_no_ack_token']

        # json_data = json.dumps(json_data)

        grand_central_gcp_account_eai_response_payload = self.simple_request_eai(params['grand_central_gcp_account_link_alternate'], 'list', 'GET')
        gcp_json_key_link_alternate = grand_central_gcp_account_eai_response_payload['entry'][0]['content']['gcp_json_key_link_alternate']
        gcp_project_id = grand_central_gcp_account_eai_response_payload['entry'][0]['content']['gcp_project_id']
        gcp_region = params['gcp_region']

        passwords_conf_payload = self.simple_request_eai(gcp_json_key_link_alternate, 'list', 'GET')
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

        apply_vars = {
            'hec_token': splunk_hec_no_ack_token,
            'hec_url': splunk_hec_endpoint.replace('https://', ''),
            'logging_filter': 'logName:"/logs/cloudaudit.googleapis.com" OR resource.type:gce OR resource.type=gcs_bucket OR resource.type=bigquery_resource',
            'project_id': gcp_project_id,
        }

        #t = Terraform()
        #return_code, stdout, stderr = t.apply(var=apply_vars, capture_output=False, auto_approve=IsFlagged)

        post_args = {
            'name': params['name'],
            'terraform_stack_name': params['terraform_stack_name'],
            'gcp_region': params['gcp_region'],
            'splunk_account_link_alternate': params['splunk_account_link_alternate'],
            'grand_central_gcp_account_link_alternate': params['grand_central_gcp_account_link_alternate'],
            'terraform_template_link_alternate': params['terraform_template_link_alternate'],
            'terraform_stack_id': 'asdf', # TODO
            'data_collection_deployed': '0',
            'data_collection_deployment_success': '0',
            #'data_selections': params['data_selections'],
        }

        deployed_terraform_templates_eai_response_payload = self.simple_request_eai(self.get_conf_handler_path_name('deployed_terraform_templates'),
            'create', 'POST', post_args)

        deployed_terraform_templates_rest_path = '/servicesNS/%s/%s/deployed_terraform_templates/%s' % (
            'nobody', self.appName, urllib.quote_plus(params['name']))
        deployed_terraform_templates_eai_response_payload = self.simple_request_eai(deployed_terraform_templates_rest_path,
                                                                                'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, deployed_terraform_templates_eai_response_payload)


    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action. Index modification is not supported through this endpoint. Both the
        scripted input and the deployed_terraform_templates.conf stanza will be overwritten on ANY call to this endpoint.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Deployed Terraform template edit requested.')

        name = self.callerArgs.id
        params = self.validate_deployed_terraform_templates_schema_params()
        conf_stanza = urllib.quote_plus(name)
        conf_handler_path = '%s/%s' % (
        self.get_conf_handler_path_name('deployed_terraform_templates', 'nobody'), conf_stanza)

        # terraform_templates_conf_payload = self.simple_request_eai(
        #     params['terraform_template_link_alternate'], 'list',
        #     'GET')
        # template_filename = terraform_templates_conf_payload['entry'][0]['content']['filename']
        #
        # with open(os.path.abspath(
        #     os.path.join(os.path.dirname(__file__), '..', 'local')) + '/' + template_filename) as json_file:
        #     json_data = json.load(json_file)

        splunk_account_conf_payload = self.simple_request_eai(params['splunk_account_link_alternate'], 'list', 'GET')
        splunk_hec_endpoint = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_endpoint']
        splunk_hec_ack_token = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_ack_token']
        splunk_hec_no_ack_token = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_no_ack_token']

        # json_data = json.dumps(json_data)

        grand_central_gcp_account_eai_response_payload = self.simple_request_eai(
            params['grand_central_gcp_account_link_alternate'], 'list', 'GET')
        gcp_json_key_link_alternate = grand_central_gcp_account_eai_response_payload['entry'][0]['content'][
            'gcp_json_key_link_alternate']
        gcp_project_id = grand_central_gcp_account_eai_response_payload['entry'][0]['content']['gcp_project_id']
        gcp_region = params['gcp_region']

        passwords_conf_payload = self.simple_request_eai(gcp_json_key_link_alternate, 'list', 'GET')
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

        apply_vars = {
            'hec_token': splunk_hec_no_ack_token,
            'hec_url': splunk_hec_endpoint.replace('https://', ''),
            'logging_filter': 'logName:"/logs/cloudaudit.googleapis.com" OR resource.type:gce OR resource.type=gcs_bucket OR resource.type=bigquery_resource',
            'project_id': gcp_project_id,
        }

        #t = Terraform()
        #return_code, stdout, stderr = t.apply(var=apply_vars, capture_output=False, auto_approve=IsFlagged)


        post_args = {
            'terraform_stack_name': params['terraform_stack_name'],
            'gcp_region': params['gcp_region'],
            'splunk_account_link_alternate': params['splunk_account_link_alternate'],
            'grand_central_gcp_account_link_alternate': params['grand_central_gcp_account_link_alternate'],
            'terraform_template_link_alternate': params['terraform_template_link_alternate'],
            'terraform_stack_id': 'asdf', #TODO
            'data_collection_deployed': '0',
            'data_collection_deployment_success': '0',
            #'data_selections': params['data_selections'],
        }

        deployed_terraform_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'edit', 'POST', post_args)

        deployed_terraform_templates_rest_path = '/servicesNS/%s/%s/deployed_terraform_templates/%s' % (
            'nobody', self.appName, conf_stanza)
        deployed_terraform_templates_eai_response_payload = self.simple_request_eai(deployed_terraform_templates_rest_path, 'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, deployed_terraform_templates_eai_response_payload)


    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'remove' action. Removes the requested stanza from inputs.conf (scripted input),
        removes the requested stanza from deployed_terraform_templates.conf, and removes all related credentials

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Deployed Terraform template removal requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)

        deployed_terraform_templates_rest_path = '/servicesNS/%s/%s/deployed_terraform_templates/%s' % (
            'nobody', self.appName, urllib.quote_plus(name))
        deployed_terraform_templates_eai_response_payload = self.simple_request_eai(deployed_terraform_templates_rest_path,
                                                                                'read', 'GET')

        terraform_stack_name = deployed_terraform_templates_eai_response_payload['entry'][0]['content']['terraform_stack_name']
        gcp_region = deployed_terraform_templates_eai_response_payload['entry'][0]['content']['gcp_region']
        splunk_account_link_alternate = deployed_terraform_templates_eai_response_payload['entry'][0]['content']['splunk_account_link_alternate']

        splunk_account_conf_payload = self.simple_request_eai(splunk_account_link_alternate, 'list', 'GET')
        splunk_hec_endpoint = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_endpoint']
        splunk_hec_ack_token = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_ack_token']
        splunk_hec_no_ack_token = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_no_ack_token']

        grand_central_gcp_account_link_alternate = deployed_terraform_templates_eai_response_payload['entry'][0]['content']['grand_central_gcp_account_link_alternate']

        grand_central_gcp_account_eai_response_payload = self.simple_request_eai(grand_central_gcp_account_link_alternate, 'read', 'GET')
        gcp_project_id= grand_central_gcp_account_eai_response_payload['entry'][0]['content']['gcp_project_id']

        gcp_json_key_link_alternate = grand_central_gcp_account_eai_response_payload['entry'][0]['content']['gcp_json_key_link_alternate']

        passwords_conf_payload = self.simple_request_eai(gcp_json_key_link_alternate, 'list', 'GET')
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

        apply_vars = {
            'hec_token': splunk_hec_no_ack_token,
            'hec_url': splunk_hec_endpoint.replace('https://', ''),
            'logging_filter': 'logName:"/logs/cloudaudit.googleapis.com" OR resource.type:gce OR resource.type=gcs_bucket OR resource.type=bigquery_resource',
            'project_id': gcp_project_id,
        }

        #t = Terraform()
        #return_code, stdout, stderr = t.destroy(var=apply_vars, capture_output=False, auto_approve=IsFlagged)


        # Delete deployed_terraform_templates.conf stanza
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('deployed_terraform_templates'), conf_stanza)
        deployed_terraform_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'remove', 'DELETE')
        self.set_conf_info_from_eai_payload(confInfo, deployed_terraform_templates_eai_response_payload)


    def validate_deployed_terraform_templates_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=deployed_terraform_templates_schema, filter=deployed_terraform_templates_schema.DEPLOYED_TERRAFORM_TEMPLATES_FIELDS)
        return self.validate_params(deployed_terraform_templates_schema.deployed_terraform_templates_schema, params)


admin.init(DeployedTerraformTemplatesEAIHandler, admin.CONTEXT_NONE)
