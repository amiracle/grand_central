from schema import Schema, And, Optional

deployed_cloudformation_templates_schema = Schema({
    'name': And(str, len, error='Invalid name value'),
    'cloudformation_stack_name': And(str, len, error='Invalid label value'),
    'aws_region': And(str, len, error='Invalid region value'),
    'splunk_account_link_alternate': And(str, len, error='Invalid Splunk Account link alternate value'),
    'cloudformation_template_link_alternate': And(str, len, error='Invalid CloudFormation template link alternate value'),
    'grand_central_aws_account_link_alternate': And(str, len, error='Invalid AWS account link alternate value'),
    'custom_cloudformation_template': And(str, len, error='Invalid custom CloudFormation template value'),
    'data_selections': And(str, len, error='Invalid data_selections value'),
})

DEPLOYED_CLOUDFORMATION_TEMPLATES_FIELDS = ['name', 'cloudformation_stack_name', 'aws_region', 'splunk_account_link_alternate', 'cloudformation_template_link_alternate', 'grand_central_aws_account_link_alternate', 'custom_cloudformation_template', 'data_selections']

# Supported POST request arguments
ALL_FIELDS = list(set(DEPLOYED_CLOUDFORMATION_TEMPLATES_FIELDS) - set(['name']))
