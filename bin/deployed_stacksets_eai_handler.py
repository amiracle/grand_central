import logging
import os
import sys
import splunk.admin as admin
import deployed_stacksets_schema
import urllib
import base_eai_handler
import log_helper
import json

libpath = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(libpath, '3rdparty')]
import boto3
from botocore.exceptions import WaiterError
from botocore.waiter import WaiterModel
from botocore.waiter import create_waiter_with_client


if sys.platform == 'win32':
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup the handler
logger = log_helper.setup(logging.INFO, 'DeployedStacksetsEAIHandler', 'deployed_stacksets_handler.log')

class StackSetInstancesDeleteComplete:
    def __init__(self, access_key, secret_key, stack_set_name, operation_id):
        self.stack_set_name = stack_set_name
        self.operation_id = operation_id
        self.client = boto3.client(
            service_name='cloudformation',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.waiter_name = 'StackSetInstancesDeleteComplete'
        self.waiter_config = {
            'version': 2,
            'waiters': {
                'StackSetInstancesDeleteComplete': {
                    'operation': 'DescribeStackSetOperation',
                    'delay': 5,
                    'maxAttempts': 100,
                    'acceptors': [
                        {
                            'matcher': 'path',
                            'expected': 'SUCCEEDED',
                            'argument': 'StackSetOperation.Status',
                            'state': 'success'
                        },
                        {
                            'matcher': 'path',
                            'expected': 'RUNNING',
                            'argument': 'StackSetOperation.Status',
                            'state': 'retry'
                        },
                        {
                            'matcher': 'path',
                            'expected': 'QUEUED',
                            'argument': 'StackSetOperation.Status',
                            'state': 'retry'
                        },
                        {
                            'matcher': 'path',
                            'expected': 'FAILED',
                            'argument': 'StackSetOperation.Status',
                            'state': 'failure'
                        },
                        {
                            'matcher': 'path',
                            'expected': 'STOPPED',
                            'argument': 'StackSetOperation.Status',
                            'state': 'failure'
                        },
                        {
                            'matcher': 'path',
                            'expected': 'FAILED',
                            'argument': 'StackSetOperation.Status',
                            'state': 'failure'
                        }
                    ]
                }
            }
        }
        self.waiter_model = WaiterModel(self.waiter_config)
        self.custom_waiter = create_waiter_with_client(
            self.waiter_name,
            self.waiter_model,
            self.client
        )

    def wait(self):
        try:
            self.custom_waiter.wait(
                StackSetName=self.stack_set_name,
                OperationId=self.operation_id
            )
        except WaiterError as e:
            raise e

class DeployedStacksetsEAIHandler(base_eai_handler.BaseEAIHandler):
    def setup(self):
        # Add our supported args
        for arg in deployed_stacksets_schema.ALL_FIELDS:
            self.supportedArgs.addOptArg(arg)

    def handleList(self, confInfo):
        """
        Called when user invokes the "list" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Deployed Stackset templates list requested.')


        # Fetch from deployed cloudformation templates conf handler
        conf_handler_path = self.get_conf_handler_path_name('deployed_stacksets', 'nobody')
        deployed_stacksets_eai_response_payload = self.simple_request_eai(conf_handler_path, 'list', 'GET', get_args={'count': -1})

        # for deployed_stackset in deployed_stacksets_eai_response_payload['entry']:
        #
        #     if deployed_stackset['content'].get('stackset_id', '') != '':
        #         deployed_stackset['content']['data_collection_deployed'] = '1'
        #
        #         stackset_name = deployed_stackset['content']['stackset_name']
        #         aws_regions = deployed_stackset['content']['aws_regions']
        #         grand_central_aws_account_link_alternate = deployed_stackset['content']['grand_central_aws_account_link_alternate']
        #
        #         grand_central_aws_account_eai_response_payload = self.simple_request_eai(grand_central_aws_account_link_alternate, 'read', 'GET')
        #         aws_access_key = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_access_key']
        #
        #         aws_secret_key_link_alternate = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_secret_key_link_alternate']
        #
        #         passwords_conf_payload = self.simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET')
        #         SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']
        #
        #         try:
        #             client = boto3.client('cloudformation', region_name=aws_region, aws_access_key_id=aws_access_key,
        #                                   aws_secret_access_key=SECRET_KEY)
        #             response = client.describe_stacks(
        #                 StackName=cloudformation_stack_name,
        #             )
        #         except Exception, e:
        #             logger.info(str(e))
        #             deployed_cloudformation_template['content']['data_collection_deployed'] = '0'
        #             deployed_cloudformation_template['content']['data_collection_deployment_success'] = '0'
        #
        #             # Remove stack_id from the Grand Central AWS Account conf entry
        #             deployed_cloudformation_template['content']['cloudformation_stack_id'] = str(e)
        #             continue
        #
        #         data_collection_deployment_success = '0'
        #
        #         for stack in response['Stacks']:
        #             if stack['StackName'] == cloudformation_stack_name:
        #                 if stack['StackStatus'] == 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS':
        #                     data_collection_deployment_success = '5'
        #                 if stack['StackStatus'] == 'UPDATE_COMPLETE':
        #                     data_collection_deployment_success = '5'
        #                 if stack['StackStatus'] == 'UPDATE_IN_PROGRESS':
        #                     data_collection_deployment_success = '4'
        #                 if stack['StackStatus'] == 'DELETE_IN_PROGRESS':
        #                     data_collection_deployment_success = '3'
        #                     deployed_cloudformation_template['content']['data_collection_deployed'] = '2'
        #                 if stack['StackStatus'] == 'CREATE_IN_PROGRESS':
        #                     data_collection_deployment_success = '2'
        #                 if stack['StackStatus'] == 'CREATE_COMPLETE':
        #                     data_collection_deployment_success = '1'
        #
        #         deployed_cloudformation_template['content']['data_collection_deployment_success'] = data_collection_deployment_success
        #
        #     else:
        #         deployed_cloudformation_template['content']['data_collection_deployed'] = '0'

        self.set_conf_info_from_eai_payload(confInfo, deployed_stacksets_eai_response_payload)

    def handleCreate(self, confInfo):
        """
        Called when user invokes the "create" action.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Stackset template deployment requested.')

        # Validate and extract correct POST params
        params = self.validate_deployed_stacksets_schema_params()

        # Get CloudFormation template from params or from template link alternate
        if 'custom_cloudformation_template' in params and params['custom_cloudformation_template'] != '0' and params['custom_cloudformation_template'] != '':
            json_data = json.loads(params['custom_cloudformation_template'])
        else:
            cloudformation_templates_conf_payload = self.simple_request_eai(params['cloudformation_template_link_alternate'], 'list',
                                                                            'GET', get_args={'count': -1})
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

        # get list of organizational units for deployment
        aws_ou_ids = params['aws_organization_unit'].replace(' ', '').split(',')
        # raise admin.InternalException('HERE {}'.format(aws_ou_ids))

        # get access key and secret key info for master account
        grand_central_aws_account_eai_response_payload = self.simple_request_eai(params['organization_master_account_link_alternate'], 'list', 'GET')
        aws_access_key = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_access_key']
        aws_secret_key_link_alternate = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_secret_key_link_alternate']

        # get list of regions for stackset deployment
        aws_regions = params['aws_regions'].replace(' ', '').split(',')

        passwords_conf_payload = self.simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET')
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

        try:
            client = boto3.client(
                'cloudformation', 
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=SECRET_KEY,
                region_name=aws_regions[0]
            )

            stackset_response = client.create_stack_set(
                StackSetName=params['stackset_name'],
                TemplateBody=json_data,
                Capabilities=['CAPABILITY_IAM'],
                PermissionModel='SERVICE_MANAGED',
                AutoDeployment={
                    'Enabled': True,
                    'RetainStacksOnAccountRemoval': False
                }
            )

        except Exception, e:
            logger.error(e)
            raise admin.InternalException('Error connecting to AWS or deploying Stackset %s' % e)

        try:
            client = boto3.client(
                'cloudformation', 
                aws_access_key_id=aws_access_key,                  
                aws_secret_access_key=SECRET_KEY,
                region_name=aws_regions[0]
            )

            # create stack instances
            stackset_instance_response = client.create_stack_instances(
                StackSetName=params['stackset_name'],
                OperationPreferences={
                    'MaxConcurrentPercentage':100,
                    'FailureTolerancePercentage':50
                },
                DeploymentTargets={
                    'OrganizationalUnitIds': aws_ou_ids
                },
                # Accounts=['ou-2yiy-osccbfgm'],
                Regions=aws_regions
            )
        except Exception as e:
            raise admin.InternalException('Error connecting to AWS or deploying Stack instances {}'.format(e))

        post_args = {
            'name': params['name'],
            'stackset_name': params['stackset_name'],
            'aws_regions': params['aws_regions'],
            'splunk_account_link_alternate': params['splunk_account_link_alternate'],
            'grand_central_aws_account_link_alternate': params['grand_central_aws_account_link_alternate'],
            'cloudformation_template_link_alternate': params['cloudformation_template_link_alternate'],
            'stackset_id': stackset_response['StackSetId'],
            'data_collection_deployed': '0',
            'data_collection_deployment_success': '0',
            'data_selections': params['data_selections'],
            'organization_master_account_link_alternate': params['organization_master_account_link_alternate'],
            'aws_organization_unit': params['aws_organization_unit']
        }

        deployed_stacksets_eai_response_payload = self.simple_request_eai(self.get_conf_handler_path_name('deployed_stacksets'),
            'create', 'POST', post_args)

        deployed_stacksets_rest_path = '/servicesNS/%s/%s/deployed_stacksets/%s' % (
            'nobody', self.appName, urllib.quote_plus(params['name']))
        deployed_stacksets_eai_response_payload = self.simple_request_eai(deployed_stacksets_rest_path,
                                                                                'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, deployed_stacksets_eai_response_payload)


    def handleEdit(self, confInfo):
        """
        Called when user invokes the 'edit' action. Index modification is not supported through this endpoint. Both the
        scripted input and the deployed_cloudformation_templates.conf stanza will be overwritten on ANY call to this endpoint.

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Deployed CloudFormation template edit requested.')

        name = self.callerArgs.id
        params = self.validate_deployed_stacksets_schema_params()
        conf_stanza = urllib.quote_plus(name)
        conf_handler_path = '%s/%s' % (
        self.get_conf_handler_path_name('deployed_stacksets', 'nobody'), conf_stanza)

        deployed_stacksets_rest_path = '/servicesNS/%s/%s/deployed_stacksets/%s' % (
            'nobody', self.appName, conf_stanza)
        deployed_stacksets_eai_response_payload = self.simple_request_eai(deployed_stacksets_rest_path, 'read', 'GET')

        params['stackset_id'] = deployed_stacksets_eai_response_payload['entry'][0]['content']['stackset_id']

        if 'custom_cloudformation_template' in params and params['custom_cloudformation_template'] != '0' and params['custom_cloudformation_template'] != '':
            json_data = json.loads(params['custom_cloudformation_template'])
        else:
            cloudformation_templates_conf_payload = self.simple_request_eai(params['cloudformation_template_link_alternate'], 'list',
                                                                            'GET', get_args={'count': -1})
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
            params['grand_central_aws_account_link_alternate'], 'list', 'GET', get_args={'count': -1})
        aws_secret_key_link_alternate = grand_central_aws_account_eai_response_payload['entry'][0]['content'][
            'aws_secret_key_link_alternate']
        aws_access_key = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_access_key']

        passwords_conf_payload = self.simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET')
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

        try:
            client = boto3.client(
                'cloudformation', 
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=SECRET_KEY,
                region_name=aws_regions[0]
            )
            response = client.update_stack_set(
                StackSetName=params['stackset_name'],
                TemplateBody=json_data,
                Capabilities=[
                    'CAPABILITY_IAM'
                ]
            )
        except Exception, e:
            logger.error(e)
            raise admin.InternalException('Error connecting to AWS or deploying Stackset %s' % e)

        post_args = {
            'stackset_name': params['stackset_name'],
            'aws_regions': params['aws_regions'],
            'splunk_account_link_alternate': params['splunk_account_link_alternate'],
            'grand_central_aws_account_link_alternate': params['grand_central_aws_account_link_alternate'],
            'cloudformation_template_link_alternate': params['cloudformation_template_link_alternate'],
            'stackset_id': params['stackset_id'],
            'data_collection_deployed': '0',
            'data_collection_deployment_success': '0',
            'data_selections': params['data_selections'],
        }

        deployed_stacksets_eai_response_payload = self.simple_request_eai(conf_handler_path, 'edit', 'POST', post_args)

        deployed_stacksets_rest_path = '/servicesNS/%s/%s/deployed_stacksets/%s' % (
            'nobody', self.appName, conf_stanza)
        deployed_stacksets_eai_response_payload = self.simple_request_eai(deployed_stacksets_rest_path, 'read', 'GET')

        self.set_conf_info_from_eai_payload(confInfo, deployed_stacksets_eai_response_payload)


    def handleRemove(self, confInfo):
        """
        Called when user invokes the 'remove' action. Removes the requested stanza from inputs.conf (scripted input),
        removes the requested stanza from deployed_cloudformation_templates.conf, and removes all related credentials

        Arguments
        confInfo -- The object containing the information about what is being requested.
        """
        logger.info('Deployed Stackset template removal requested.')

        name = self.callerArgs.id
        conf_stanza = urllib.quote_plus(name)

        deployed_stacksets_rest_path = '/servicesNS/%s/%s/deployed_stacksets/%s' % (
            'nobody', self.appName, urllib.quote_plus(name))
        deployed_stacksets_eai_response_payload = self.simple_request_eai(deployed_stacksets_rest_path,
                                                                                'read', 'GET')

        delete_instances = self.get_param('delete_instances', default='false')

        stackset_name = deployed_stacksets_eai_response_payload['entry'][0]['content']['stackset_name']
        # raise admin.InternalException('THIISSS {}'.format(deployed_stacksets_eai_response_payload))
        # try:
        aws_regions = deployed_stacksets_eai_response_payload['entry'][0]['content']['aws_regions'].replace(' ', '').split(',')
        aws_regions = list(map(lambda x: str(x), aws_regions))

        # grand_central_aws_account_link_alternate = deployed_stacksets_eai_response_payload['entry'][0]['content']['grand_central_aws_account_link_alternate']
        grand_central_aws_account_link_alternate = deployed_stacksets_eai_response_payload['entry'][0]['content']['organization_master_account_link_alternate']

        # raise admin.InternalException('THIISSS {}'.format(grand_central_aws_account_link_alternate))

        grand_central_aws_account_eai_response_payload = self.simple_request_eai(grand_central_aws_account_link_alternate, 'read', 'GET')
        aws_account_id = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_account_id']
        aws_access_key = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_access_key']

        aws_secret_key_link_alternate = grand_central_aws_account_eai_response_payload['entry'][0]['content']['aws_secret_key_link_alternate']

        aws_ou_ids = deployed_stacksets_eai_response_payload['entry'][0]['content']['aws_organization_unit'].replace(' ', '').split(',')

        passwords_conf_payload = self.simple_request_eai(aws_secret_key_link_alternate, 'list', 'GET')
        SECRET_KEY = passwords_conf_payload['entry'][0]['content']['clear_password']

        # raise admin.InternalException('access key : {} -- secret key : {}'.format(aws_access_key, SECRET_KEY))
        if delete_instances == 'true':
            try:
                client = boto3.client(
                    'cloudformation', 
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=SECRET_KEY,
                    region_name=aws_regions[0]
                )
                response = client.delete_stack_instances(
                    StackSetName=stackset_name,
                    # Accounts=[aws_account_id],
                    DeploymentTargets={
                        'OrganizationalUnitIds': aws_ou_ids
                    },
                    Regions=aws_regions,
                    OperationPreferences={
                        'MaxConcurrentPercentage':100,
                        'FailureTolerancePercentage':50
                    },
                    RetainStacks=False
                )
                # op_id = response['OperationId']
                # waiter = StackSetInstancesDeleteComplete(aws_access_key, SECRET_KEY, stackset_name, op_id)
                # waiter.wait()
            except Exception, e:
                logger.error(e)
                raise admin.InternalException('Error connecting to AWS or deleting Stackset instances %s' % e)

            conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('deployed_stacksets'), conf_stanza)
            deployed_stacksets_eai_response_payload = self.simple_request_eai(conf_handler_path, 'read', 'GET')
            self.set_conf_info_from_eai_payload(confInfo, deployed_stacksets_eai_response_payload)
        # except Exception as e:
        #     raise admin.InternalException('Error in delete Stackset instances or waiter %s' % e)
        else:
            try:
                client = boto3.client(
                    'cloudformation', 
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=SECRET_KEY,
                    region_name=aws_regions[0]
                )
                response = client.delete_stack_set(
                    StackSetName=stackset_name
                )
            except Exception, e:
                logger.error(e)
                raise admin.InternalException('Error connecting to AWS or deleting Stackset %s' % e)

        # Delete deployed_stacksets.conf stanza

            conf_handler_path = '%s/%s' % (self.get_conf_handler_path_name('deployed_stacksets'), conf_stanza)
            deployed_stacksets_eai_response_payload = self.simple_request_eai(conf_handler_path, 'remove', 'DELETE')
            self.set_conf_info_from_eai_payload(confInfo, deployed_stacksets_eai_response_payload)


    def validate_deployed_stacksets_schema_params(self):
        """
        Validates raw request params against the server schema
        """
        params = self.get_params(schema=deployed_stacksets_schema, filter=deployed_stacksets_schema.DEPLOYED_STACKSETS_FIELDS)
        return self.validate_params(deployed_stacksets_schema.deployed_stacksets_schema, params)


admin.init(DeployedStacksetsEAIHandler, admin.CONTEXT_NONE)
