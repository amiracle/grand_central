from schema import Schema, And, Optional

splunk_accounts_schema = Schema({
    'name': And(str, len, error='Invalid name value'),
    'label': And(str, len, error='Invalid label value'),
    'splunk_hec_endpoint': And(str, len, error='Invalid Splunk HEC endpoint value'),
    'splunk_hec_ack_token': And(str, len, error='Invalid ack HEC token value'),
    'splunk_hec_no_ack_token': And(str, len, error='Invalid no-ack HEC token value'),
})

SPLUNK_ACCOUNTS_FIELDS = ['name', 'label', 'splunk_hec_endpoint', 'splunk_hec_ack_token', 'splunk_hec_no_ack_token']

# Supported POST request arguments
ALL_FIELDS = list(set(SPLUNK_ACCOUNTS_FIELDS) - set(['name']))
