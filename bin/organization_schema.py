from schema import Schema, And, Optional

organization_schema = Schema({
    'name': And(str, len, error='Invalid name value'),
    'account_id': And(str, len, error='Invalid Account ID value'),
})

ORGANIZATION_FIELDS = ['name', 'account_id']

# Supported POST request arguments
ALL_FIELDS = list(set(ORGANIZATION_FIELDS) - set(['name']))
