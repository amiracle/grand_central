aws_account_id = <numeric account id>
* The AWS Account ID of the account
aws_access_key = <key string>
* The AWS Access Key of the account
aws_secret_key_link_alternate = <key string>
* The link alternate to the encrypted AWS Secret Key of the account
aws_account_arn = <ARN string>
* The AWS ARN of the account
aws_account_email = <email string>
* The email attached the the account
aws_account_joined_method = <INVITED | CREATED>
* The join method of the AWS account in the organization
aws_account_joined_timestamp = <timestamp string>
* The time the account joined the organization
aws_account_status = <ACTIVE | SUSPENDED>
* The status of the account
cloudformation_template_action = <apply | remove>
* CRUD action to perform on the account template
display_name = <meaningful string>
* A display name describing the account
organization_master_account = <1 | 0>
* If this is an organization master account or not
tags = <comma separated alphanumeric strings (underscores and dashes supported)>
* Tags associated with the AWS account
template_link_alternate = <link alternate>
* Link alternate of template to apply to account
splunk_account_link_alternate = <link alternates>
* Link alternate of the Splunk account this AWS account sends data to
parent_aws_account_id = <numeric account id>
* The AWS Account ID of the parent account
