  
# 'Arn': 'arn:aws:wellarchitected:us-west-2:158540654927:workload/8ae0f2a5baf254fc90aae33135eae088',
#  'Id': '8ae0f2a5baf254fc90aae33135eae088',
#  'ImprovementStatus': 'NOT_APPLICABLE',
#  'Name': 'Retail Website - North America',
#  'Owner': '158540654927',
#  'RiskCounts': {'HIGH': 11, 'MEDIUM': 16, 'NONE': 18, 'UNANSWERED': 1}

from schema import Schema, And

# The schema validation is provided by the Schema library documented here: https://pypi.org/project/schema/
example_schema = Schema({
    'name': And(str, len, error='Invalid name value'),
    'organization_master_account_link_alternate': And(str, len, error='Invalid org_master_account_link_alt value'),
    'workload_name': And(str, len, error='Invalid workload_name value'),
    'description': And(str, len, error='Invalid description value'),
    'environment': And(str, len, error='Invalid environment value'),
    'regions': And(str, len, error='invalid regions value'),
    'pillar_priorities': And(str, len, error='Invalid pillar priorities value'),
    'lenses': And(str, len, error='invalid lenses'),
    'review_owner': And(str, len, error='invalid review owner'),
    # 'workload_id': And(str, len, error='Invalid workload_id value'),
    # 'workload_owner': And(str, len, error='Invalid workload_owner value'),
    # 'workload_arn': And(str, len, error='Invalid arn value'),
    # 'improvement_status': And(str, len, error='Invalid improvement_status value'),
    # 'risk_counts': And(str, len, error='Invalid risk_counts value'),
})

CONF_FIELDS = [
    'name', 
    'organization_master_account_link_alternate',
    'workload_name', 
    'description',
    'environment',
    'regions',
    'pillar_priorities',
    'lenses',
    'review_owner'
    # 'workload_id', 
    # 'workload_owner', 
    # 'workload_arn', 
    # 'improvement_status', 
    # 'risk_counts'
]

# Supported POST request arguments -- removes name for Splunk API expectations
ALL_FIELDS = list(set(CONF_FIELDS) - set(['name']))