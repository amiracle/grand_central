from schema import Schema, And, Optional

deployed_stacksets_schema = Schema({
    'name': And(str, len, error='Invalid name value'),
    'stackset_name': And(str, len, error='Invalid label value'),
    'aws_regions': And(str, len, error='Invalid regions value'),
    'splunk_account_link_alternate': And(str, len, error='Invalid Splunk Account link alternate value'),
    'cloudformation_template_link_alternate': And(str, len, error='Invalid CloudFormation template link alternate value'),
    'grand_central_aws_account_link_alternate': And(str, len, error='Invalid AWS account link alternates value'),
    'custom_cloudformation_template': And(str, len, error='Invalid custom CloudFormation template value'),
    'data_selections': And(str, len, error='Invalid data_selections value'),
    'organization_master_account_link_alternate': And(str, len, error='Invalid organization_master_account_link_alternate value'),
    'aws_organization_unit': And(str, len, error='Invalid organization_units value'),
})

DEPLOYED_STACKSETS_FIELDS = ['name', 'stackset_name', 'aws_regions', 'splunk_account_link_alternate', 'cloudformation_template_link_alternate', 'grand_central_aws_account_link_alternate', 'custom_cloudformation_template', 'data_selections', 'organization_master_account_link_alternate', 'aws_organization_unit', 'delete_instances']

# Supported POST request arguments
ALL_FIELDS = list(set(DEPLOYED_STACKSETS_FIELDS) - set(['name']))
