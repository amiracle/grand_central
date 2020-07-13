from schema import Schema, And, Optional

organization_unit_schema = Schema({
    'name': And(str, len, error='Invalid name value'),
    'aws_account_id': And(str, len, error='Invalid Account ID value'),
})

ORGANIZATION_UNIT_FIELDS = ['name', 'aws_account_id']

# Supported POST request arguments
ALL_FIELDS = list(set(ORGANIZATION_UNIT_FIELDS) - set(['name']))
