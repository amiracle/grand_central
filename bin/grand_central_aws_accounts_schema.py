from schema import Schema, And, Optional
import re

def tags_validator(tags):
    if tags:
        tags = tags.replace(', ', ',').split(',')
        tag_pattern = re.compile('^[A-Za-z0-9\-\_]+$')
        for tag in tags:
            if not tag_pattern.match(tag):
                return False
        return True
    return False

def name_validator(name):
    if name:
        name_pattern = re.compile('^[A-Za-z0-9\-\'\s]+$')
        if not name_pattern.match(name):
            return False
        return True
    return False

server_schema = Schema({
    'name': And(str, len, name_validator, error='Invalid name value'),
    'display_name': And(str, len, error='Invalid display name value'),
    'aws_account_id': And(str, len, error='Invalid AWS Account ID'),
    'aws_access_key': And(str, len, error='Invalid AWS Access Key'),
    Optional('aws_account_arn'): And(str, len, error='Invalid AWS Account ARN'),
    Optional('aws_account_email'): And(str, len, error='Invalid AWS Account email'),
    Optional('aws_account_status'): And(str, len, lambda val: val in ('ACTIVE', 'SUSPENDED'), error='Invalid AWS Account Status'),
    Optional('aws_account_joined_method'): And(str, len, lambda val: val in ('INVITED', 'CREATED'), error='Invalid AWS Account joined method'),
    Optional('aws_account_joined_timestamp'): And(str, len, error='Invalid AWS Account joined timestamp'),
    Optional('organization_master_account', default='0'): And(str, len, lambda val: val in ('0', '1'), error='Invalid organization_account value'),
    Optional('tags', default=''): And(str, len, tags_validator, error='Invalid tags value'),
    Optional('template_link_alternate', default=''): And(str, len, error='Invalid template_link_alternate value'),
    Optional('cloudformation_template_action'): And(str, len, lambda val: val in ('apply', 'remove'), error='Invalid cloudformation_template_action'),
    Optional('splunk_account_link_alternate', default=''): And(str, len, error='Invalid splunk_account_link_alternate'),
    Optional('parent_aws_account_id', default=''): And(str, len, error='Invalid parent AWS Account ID'),
})

SERVER_FIELDS = ['name', 'aws_access_key', 'organization_master_account', 'aws_account_id', 'aws_account_arn', 'aws_account_email', 'aws_account_status', 'aws_account_joined_method', 'aws_account_joined_timestamp', 'display_name', 'tags', 'template_link_alternate', 'cloudformation_template_action', 'splunk_account_link_alternate', 'parent_aws_account_id', 'enable_ou']

auth_schema = Schema({
    'aws_secret_key': And(str, len, error='Invalid AWS Secret Key'),
})

AUTH_FIELDS = ['aws_secret_key']

# Supported POST request arguments
ALL_FIELDS = list(set(SERVER_FIELDS + AUTH_FIELDS) - set(['name']))
