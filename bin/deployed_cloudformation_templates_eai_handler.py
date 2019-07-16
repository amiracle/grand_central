import logging
import os
import sys
import splunk.admin as admin
import deployed_cloudformation_templates_schema
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
logger = log_helper.setup(logging.INFO, 'DeployedCloudFormationTemplatesEAIHandler', 'deployed_cloudformation_templates_handler.log')

class DeployedCloudFormationTemplatesEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in deployed_cloudformation_templates_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Deployed CloudFormation templates list requested.')

        # Fetch from deployed cloudformation templates conf handler
        conf_handler_path = self.get_conf_handler_path_name('deployed_cloudformation_templates', 'nobody')
        deployed_cloudformation_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET')

        for deployed_cloudformation_template in deployed_cloudformation_templates_eai_response_payload['entry']:

            if deployed_cloudformation_template['content'].get('cloudformation_stack_id', '') != '':
                deployed_cloudformation_template['content']['data_collection_deployed'] = '1'

                cloudformation_stack_name = deployed_cloudformation_template['content']['cloudformation_stack_name']
                aws_region = deployed_cloudformation_template['content']['aws_region']
                grand_central_aws_account_link_alternate = deployed_cloudformation_template['content']['grand_central_aws_account_link_alternate']

                grand_central_aws_account_eai_response_payload = self.simple_request_eai(grand_central_aws_account_link_alternate, 'read', 'GET')
                aws_access_key = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_access_key']

                aws_secret_key_link_alternate = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_secret_key_link_alternate']

                passwords_conf_payload = self.simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET')
                SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

                try:
                    client = boto3.client('cloudformation', region_name=aws_region, aws_access_key_id=aws_access_key,
                                          aws_secret_access_key=SECRET_KEY)
                    response = client.describe_stacks(
                        StackName=cloudformation_stack_name,
                    )
                except Exception, e:
                    logger.info(str(e))
                    deployed_cloudformation_template['content']['data_collection_deployed'] = '0'
                    deployed_cloudformation_template['content']['data_collection_deployment_success'] = '0'

                    # Remove stack_id from the Grand Central AWS Account conf entry
                    deployed_cloudformation_template['content']['cloudformation_stack_id'] = str(e)
                    continue

                data_collection_deployment_success = '0'

                for stack in response['Stacks']:
                    if stack['StackName'] == cloudformation_stack_name:
                        if stack['StackStatus'] == 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS':
                            data_collection_deployment_success = '5'
                        if stack['StackStatus'] == 'UPDATE_COMPLETE':
                            data_collection_deployment_success = '5'
                        if stack['StackStatus'] == 'UPDATE_IN_PROGRESS':
                            data_collection_deployment_success = '4'
                        if stack['StackStatus'] == 'DELETE_IN_PROGRESS':
                            data_collection_deployment_success = '3'
                            deployed_cloudformation_template['content']['data_collection_deployed'] = '2'
                        if stack['StackStatus'] == 'CREATE_IN_PROGRESS':
                            data_collection_deployment_success = '2'
                        if stack['StackStatus'] == 'CREATE_COMPLETE':
                            data_collection_deployment_success = '1'

                deployed_cloudformation_template['content']['data_collection_deployment_success'] = data_collection_deployment_success

            else:
                deployed_cloudformation_template['content']['data_collection_deployed'] = '0'

        self.set_conf_info_from_eai_payload(confInfo, deployed_cloudformation_templates_eai_response_payload)

    def handleCreate(self, confInfo):
        """
        Called when user invokes the "create" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('CloudFormation template deployment requested.')

        # Validate and extract correct POST params
        params = self.validate_deployed_cloudformation_templates_schema_params()

        # Get CloudFormation template from params or from template link alternate
        if 'custom_cloudformation_template' in params and params['custom_cloudformation_template'] != '0' and params['custom_cloudformation_template'] != '':
            json_data = json.loads(params['custom_cloudformation_template'])
        else:
            cloudformation_templates_conf_payload = self.simple_request_eai(params['cloudformation_template_link_alternate'], 'list',
                                                                            'GET')
            template_filename = cloudformation_templates_conf_payload['entry'][0]['content']['filename']

            with open(os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'local')) + '/' + template_filename) as json_file:
                json_data = json.load(json_file)

        # Get Splunk account details
        splunk_account_conf_payload = self.simple_request_eai(params['splunk_account_link_alternate'], 'list', 'GET')
        splunk_hec_endpoint = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_endpoint']
        splunk_hec_ack_token = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_ack_token']
        splunk_hec_no_ack_token = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_no_ack_token']

        # Update the CloudFormation template with the account information collected above
        if "VPCFirehoseDeliveryStream" in json_data["Resources"]:
            json_data["Resources"]["VPCFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECEndpoint"] = splunk_hec_endpoint
            json_data["Resources"]["VPCFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECToken"] = splunk_hec_ack_token

        if "CWLFirehoseDeliveryStream" in json_data["Resources"]:
            json_data["Resources"]["CWLFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECEndpoint"] = splunk_hec_endpoint
            json_data["Resources"]["CWLFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECToken"] = splunk_hec_ack_token

        if "CWEFirehoseDeliveryStream" in json_data["Resources"]:
            json_data["Resources"]["CWEFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECEndpoint"] = splunk_hec_endpoint
            json_data["Resources"]["CWEFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECToken"] = splunk_hec_ack_token

        if "BackingLambdaConfigLogProcessor" in json_data["Resources"]:
            json_data["Resources"]["BackingLambdaConfigLogProcessor"]["Properties"]["Environment"]["Variables"][
                "SPLUNK_HEC_URL"] = splunk_hec_endpoint
            json_data["Resources"]["BackingLambdaConfigLogProcessor"]["Properties"]["Environment"]["Variables"][
                "SPLUNK_HEC_TOKEN"] = splunk_hec_no_ack_token

        json_data = json.dumps(json_data)

        grand_central_aws_account_eai_response_payload = self.simple_request_eai(params['grand_central_aws_account_link_alternate'], 'list', 'GET')
        aws_secret_key_link_alternate = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_secret_key_link_alternate']
        aws_access_key = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_access_key']

        passwords_conf_payload = self.simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET')
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

        try:
            client = boto3.client('cloudformation', region_name=params['aws_region'], aws_access_key_id=aws_access_key,
                                  aws_secret_access_key=SECRET_KEY)
            response = client.create_stack(
                StackName=params['cloudformation_stack_name'],
                TemplateBody=json_data,
                Capabilities=[
                    'CAPABILITY_IAM'
                ]
            )
        except Exception, e:
            logger.error(e)
            raise admin.InternalException('Error connecting to AWS or deploying CloudFormation template %s' % e)

        post_args = {
            'name': params['name'],
            'cloudformation_stack_name': params['cloudformation_stack_name'],
            'aws_region': params['aws_region'],
            'splunk_account_link_alternate': params['splunk_account_link_alternate'],
            'grand_central_aws_account_link_alternate': params['grand_central_aws_account_link_alternate'],
            'cloudformation_template_link_alternate': params['cloudformation_template_link_alternate'],
            'cloudformation_stack_id': response['StackId'],
            'data_collection_deployed': '0',
            'data_collection_deployment_success': '0',
        }

        deployed_cloudformation_templates_eai_response_payload = self.simple_request_eai(self.get_conf_handler_path_name('deployed_cloudformation_templates'),
            'create', 'POST', post_args)

        deployed_cloudformation_templates_rest_path = '/servicesNS/%s/%s/deployed_cloudformation_templates/%s' % (
            'nobody', self.appName, urllib.quote_plus(params['name']))
        deployed_cloudformation_templates_eai_response_payload = self.simple_request_eai(deployed_cloudformation_templates_rest_path,
                                                                                'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, deployed_cloudformation_templates_eai_response_payload)


    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action. Index modification is not supported through this endpoint. Both the
        scripted input and the deployed_cloudformation_templates.conf stanza will be overwritten on ANY call to this endpoint.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Deployed CloudFormation template edit requested.')

        name = self.callerArgs.id
        params = self.validate_deployed_cloudformation_templates_schema_params()
        conf_stanza = urllib.quote_plus(name)
        conf_handler_path = '%s/%s' % (
        self.get_conf_handler_path_name('deployed_cloudformation_templates', 'nobody'), conf_stanza)

        cloudformation_templates_conf_payload = self.simple_request_eai(
            params['cloudformation_template_link_alternate'], 'list',
            'GET')
        template_filename = cloudformation_templates_conf_payload['entry'][0]['content']['filename']

        with open(os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'local')) + '/' + template_filename) as json_file:
            json_data = json.load(json_file)

        splunk_account_conf_payload = self.simple_request_eai(params['splunk_account_link_alternate'], 'list', 'GET')
        splunk_hec_endpoint = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_endpoint']
        splunk_hec_ack_token = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_ack_token']
        splunk_hec_no_ack_token = splunk_account_conf_payload['entry'][0]['content']['splunk_hec_no_ack_token']

        # Update the CloudFormation template with the account information collected above
        if "VPCFirehoseDeliveryStream" in json_data["Resources"]:
            json_data["Resources"]["VPCFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECEndpoint"] = splunk_hec_endpoint
            json_data["Resources"]["VPCFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECToken"] = splunk_hec_ack_token

        if "CWLFirehoseDeliveryStream" in json_data["Resources"]:
            json_data["Resources"]["CWLFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECEndpoint"] = splunk_hec_endpoint
            json_data["Resources"]["CWLFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECToken"] = splunk_hec_ack_token

        if "CWEFirehoseDeliveryStream" in json_data["Resources"]:
            json_data["Resources"]["CWEFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECEndpoint"] = splunk_hec_endpoint
            json_data["Resources"]["CWEFirehoseDeliveryStream"]["Properties"]["SplunkDestinationConfiguration"][
                "HECToken"] = splunk_hec_ack_token

        if "BackingLambdaConfigLogProcessor" in json_data["Resources"]:
            json_data["Resources"]["BackingLambdaConfigLogProcessor"]["Properties"]["Environment"]["Variables"][
                "SPLUNK_HEC_URL"] = splunk_hec_endpoint
            json_data["Resources"]["BackingLambdaConfigLogProcessor"]["Properties"]["Environment"]["Variables"][
                "SPLUNK_HEC_TOKEN"] = splunk_hec_no_ack_token

        json_data = json.dumps(json_data)

        grand_central_aws_account_eai_response_payload = self.simple_request_eai(
            params['grand_central_aws_account_link_alternate'], 'list', 'GET')
        aws_secret_key_link_alternate = grand_central_aws_account_eai_response_payload['entry'][0]['content'][
            'aws_secret_key_link_alternate']
        aws_access_key = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_access_key']

        passwords_conf_payload = self.simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET')
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

        try:
            client = boto3.client('cloudformation', region_name=params['aws_region'], aws_access_key_id=aws_access_key,
                                  aws_secret_access_key=SECRET_KEY)
            response = client.update_stack(
                StackName=params['cloudformation_stack_name'],
                TemplateBody=json_data,
                Capabilities=[
                    'CAPABILITY_IAM'
                ]
            )
        except Exception, e:
            logger.error(e)
            raise admin.InternalException('Error connecting to AWS or deploying CloudFormation template %s' % e)

        post_args = {
            'cloudformation_stack_name': params['cloudformation_stack_name'],
            'aws_region': params['aws_region'],
            'splunk_account_link_alternate': params['splunk_account_link_alternate'],
            'grand_central_aws_account_link_alternate': params['grand_central_aws_account_link_alternate'],
            'cloudformation_template_link_alternate': params['cloudformation_template_link_alternate'],
            'cloudformation_stack_id': response['StackId'],
            'data_collection_deployed': '0',
            'data_collection_deployment_success': '0',
        }

        deployed_cloudformation_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'edit', 'POST', post_args)

        deployed_cloudformation_templates_rest_path = '/servicesNS/%s/%s/deployed_cloudformation_templates/%s' % (
            'nobody', self.appName, conf_stanza)
        deployed_cloudformation_templates_eai_response_payload = self.simple_request_eai(deployed_cloudformation_templates_rest_path, 'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, deployed_cloudformation_templates_eai_response_payload)


    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'remove' action. Removes the requested stanza from inputs.conf (scripted input),
        removes the requested stanza from deployed_cloudformation_templates.conf, and removes all related credentials

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Deployed CloudFormation template removal requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)

        deployed_cloudformation_templates_rest_path = '/servicesNS/%s/%s/deployed_cloudformation_templates/%s' % (
            'nobody', self.appName, urllib.quote_plus(name))
        deployed_cloudformation_templates_eai_response_payload = self.simple_request_eai(deployed_cloudformation_templates_rest_path,
                                                                                'read', 'GET')

        cloudformation_stack_name = deployed_cloudformation_templates_eai_response_payload['entry'][0]['content']['cloudformation_stack_name']
        aws_region = deployed_cloudformation_templates_eai_response_payload['entry'][0]['content']['aws_region']
        grand_central_aws_account_link_alternate = deployed_cloudformation_templates_eai_response_payload['entry'][0]['content']['grand_central_aws_account_link_alternate']

        grand_central_aws_account_eai_response_payload = self.simple_request_eai(grand_central_aws_account_link_alternate, 'read', 'GET')
        aws_access_key = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_access_key']

        aws_secret_key_link_alternate = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_secret_key_link_alternate']

        passwords_conf_payload = self.simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET')
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

        try:
            client = boto3.client('cloudformation', region_name=aws_region, aws_access_key_id=aws_access_key,
                                  aws_secret_access_key=SECRET_KEY)
            response = client.delete_stack(
                StackName=cloudformation_stack_name
            )
        except Exception, e:
            logger.error(e)
            raise admin.InternalException('Error connecting to AWS or deleting CloudFormation template %s' % e)

        # Delete deployed_cloudformation_templates.conf stanza
        conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('deployed_cloudformation_templates'), conf_stanza)
        deployed_cloudformation_templates_eai_response_payload = self.simple_request_eai(conf_handler_path, 'remove', 'DELETE')
        self.set_conf_info_from_eai_payload(confInfo, deployed_cloudformation_templates_eai_response_payload)


    def validate_deployed_cloudformation_templates_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=deployed_cloudformation_templates_schema, filter=deployed_cloudformation_templates_schema.DEPLOYED_CLOUDFORMATION_TEMPLATES_FIELDS)
        return self.validate_params(deployed_cloudformation_templates_schema.deployed_cloudformation_templates_schema, params)


admin.init(DeployedCloudFormationTemplatesEAIHandler, admin.CONTEXT_NONE)
