from schema import Schema, And, Optional

terraform_template_schema = Schema({
    'name': And(str, len, error='Invalid name value'),
    Optional('label', default=''): And(str, len, error='Invalid label'),
    Optional('description', default=''): And(str, len, error='Invalid description'),
    Optional('filename', default=''): And(str, len, error='Invalid filename'),
    Optional('template', default=''): And(str, len, error='Invalid template'),
})

TERRAFORM_TEMPLATE_FIELDS = ['name', 'label', 'description', 'filename', 'template']

# Supported POST request arguments
ALL_FIELDS = list(set(TERRAFORM_TEMPLATE_FIELDS) - set(['name']))
