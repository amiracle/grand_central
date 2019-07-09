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
        name_pattern = re.compile('^[A-Za-z0-9\-]+$')
        if not name_pattern.match(name):
            return False
        return True
    return False

server_schema = Schema({
    'name': And(str, len, name_validator, error='Invalid name value'),
    Optional('aws_account_id', default=''): And(str, len, error='Invalid AWS Account ID'),
    'aws_access_key': And(str, len, error='Invalid AWS Access Key'),
    Optional('tags', default=''): And(str, len, tags_validator, error='Invalid tags value'),
    Optional('template_link_alternate', default=''): And(str, len, error='Invalid template_link_alternate value'),
    Optional('cloudformation_template_action'): And(str, len, lambda val: val in ('apply', 'remove', 'update'), error='Invalid cloudformation_template_action'),
})

SERVER_FIELDS = ['name', 'aws_account_id', 'aws_access_key', 'tags', 'template_link_alternate', 'cloudformation_template_action']

auth_schema = Schema({
    'aws_secret_key': And(str, len, error='Invalid AWS Secret Key'),
})

AUTH_FIELDS = ['aws_secret_key']

# Supported POST request arguments
ALL_FIELDS = list(set(SERVER_FIELDS + AUTH_FIELDS) - set(['name']))
