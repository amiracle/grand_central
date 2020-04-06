from schema import Schema, And, Optional

deployed_terraform_templates_schema = Schema({
    'name': And(str, len, error='Invalid name value'),
    'terraform_stack_name': And(str, len, error='Invalid label value'),
    'gcp_region': And(str, len, error='Invalid region value'),
    'splunk_account_link_alternate': And(str, len, error='Invalid Splunk Account link alternate value'),
    'terraform_template_link_alternate': And(str, len, error='Invalid Terraform template link alternate value'),
    'grand_central_gcp_account_link_alternate': And(str, len, error='Invalid GCP account link alternate value'),
    'custom_terraform_template': And(str, len, error='Invalid custom Terraform template value'),
    #'data_selections': And(str, len, error='Invalid data_selections value'),
})

DEPLOYED_TERRAFORM_TEMPLATES_FIELDS = ['name', 'terraform_stack_name', 'gcp_region', 'splunk_account_link_alternate', 'terraform_template_link_alternate', 'grand_central_gcp_account_link_alternate', 'custom_terraform_template']

# Supported POST request arguments
ALL_FIELDS = list(set(DEPLOYED_TERRAFORM_TEMPLATES_FIELDS) - set(['name']))
