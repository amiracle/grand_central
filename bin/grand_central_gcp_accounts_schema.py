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
    'gcp_project_id': And(str, len, error='Invalid GCP Project ID'),
    'gcp_json_key_name': And(str, len, error='Invalid GCP JSON Key Name'),
    Optional('template_link_alternate', default=''): And(str, len, error='Invalid template_link_alternate value'),
    Optional('terraform_template_action'): And(str, len, lambda val: val in ('apply', 'remove'), error='Invalid terraform_template_action'),
    Optional('tags', default=''): And(str, len, tags_validator, error='Invalid tags value'),
    Optional('splunk_account_link_alternate', default=''): And(str, len, error='Invalid splunk_account_link_alternate'),
})

SERVER_FIELDS = ['name', 'gcp_project_id', 'gcp_json_key_name', 'display_name', 'tags', 'template_link_alternate', 'terraform_template_action', 'splunk_account_link_alternate']

auth_schema = Schema({
    'gcp_json_key': And(str, len, error='Invalid GCP JSON Key'),
})

AUTH_FIELDS = ['gcp_json_key']

# Supported POST request arguments
ALL_FIELDS = list(set(SERVER_FIELDS + AUTH_FIELDS) - set(['name']))
