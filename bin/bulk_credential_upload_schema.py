from schema import Schema, And, Optional

bulk_credential_upload_schema = Schema({
    'name': And(str, len, error='Invalid name value'),
    'credential_file': And(str, len, error='Invalid credential file'),
})

BULK_CREDENTIAL_UPLOAD_FIELDS = ['name', 'credential_file']

# Supported POST request arguments
ALL_FIELDS = list(set(BULK_CREDENTIAL_UPLOAD_FIELDS) - set(['name']))
