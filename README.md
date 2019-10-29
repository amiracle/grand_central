# Grand Central App for Splunk

## Manage and Monitor your Cloud Data Providers in Splunk from one centralized data platform.

### This Splunk based app relies on the work done by Project Trumpet and the AWS Organizational model.


Grand Central User's Guide :

Version 1.1



Getting Started

Amazon Web Services
Requirements
Grand Central works with the AWS Organizations framework and does not require either Landing Zone or Control Tower to work. By having the organization setup with multiple accounts, Grand Central will be able to discover the accounts and add into management within Splunk. 

Please refer to the Amazon Web Services documentation on how to get started with Organizations : https://aws.amazon.com/premiumsupport/knowledge-center/get-started-organizations/  
	
Before Deploying Grand Central

You will need to be able to create an IAM User in the Master Account and the sub accounts that will be added into management under Splunk. By default there will be two IAM policies created, one to list all the accounts in the Organization and the second will be a deployment policy. 

```
IAM Role Creation Shortcut (beta)

1. Open Cloudformation Template in target account and run https://grandcentraldeployment.s3.amazonaws.com/CFTemplates_GCDeployer_User.json 

2. Copy the Access Key / Secret Key from CloudFormation Output

3. Install grand_central.spl file from github
```
	
Setting up your Grand Central Environment

You will need to create an IAM User in your master account that has a policy with access to list organizations. Here is an example of the JSON Policy :

IAM Policy - Grand_Central_Lister_Policy

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "organizations:ListAccounts",
            "Resource": "*"
        }
    ]
}
```
Next, each AWS Account will need to have the following IAM User and Policy created in order to deploy the data collection capabilities for Splunk : 

```

IAM Policy - Grand_Central_Deployer_Policy :

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "lambda:CreateFunction",
                "iam:GetAccountPasswordPolicy",
                "kinesis:Get*",
                "iam:CreateRole",
                "s3:CreateBucket",
                "iam:AttachRolePolicy",
                "lambda:GetFunctionConfiguration",
                "iam:PutRolePolicy",
                "kinesis:ListStreams",
                "s3:GetObjectAcl",
                "iam:DetachRolePolicy",
                "logs:GetLogEvents",
                "events:RemoveTargets",
                "lambda:DeleteFunction",
                "events:PutEvents",
                "s3:GetBucketPolicyStatus",
                "iam:GetRole",
                "events:DescribeRule",
                "lambda:InvokeFunction",
                "iam:GetAccessKeyLastUsed",
                "firehose:CreateDeliveryStream",
                "cloudformation:*",
                "iam:DeleteRole",
                "firehose:DescribeDeliveryStream",
                "s3:GetObject",
                "sts:AssumeRole",
                "logs:PutSubscriptionFilter",
                "s3:GetLifecycleConfiguration",
                "s3:GetBucketTagging",
                "logs:DescribeLogStreams",
                "events:PutRule",
                "s3:GetBucketLogging",
                "s3:ListBucket",
                "s3:GetAccelerateConfiguration",
                "iam:CreateUser",
                "s3:GetBucketPolicy",
                "firehose:DeleteDeliveryStream",
                "iam:PassRole",
                "sns:Get*",
                "sns:Publish",
                "iam:DeleteRolePolicy",
                "s3:DeleteBucket",
                "s3:PutBucketVersioning",
                "iam:ListAccessKeys",
                "s3:GetBucketPublicAccessBlock",
                "logs:DescribeLogGroups",
                "kinesis:DescribeStream",
                "iam:DeleteUser",
                "sns:List*",
                "events:PutTargets",
                "events:DeleteRule",
                "lambda:AddPermission",
                "s3:ListAllMyBuckets",
                "s3:GetBucketCORS",
                "iam:ListUsers",
                "iam:GetUser",
                "s3:GetBucketLocation",
	      "lambda:RemovePermission"
            ],
            "Resource": "*"
        }
    ]
}
``` 
 
## Credential Smusher
Download the credentials files into a single directory for all the accounts. Once you have all the files (e.g. credentials.csv, credentials-1.csv) then run the credentials_smusher.py which will create all_account_credentials.json. 

Adding Master Account

Log into the Grand Central App and navigate to the Accounts Section.  

Click on the “New Organization Master Account” button: 
![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_1.png?)

The Master Account will now be added to your console: 


Next, validate this IAM user has access to list all the accounts in the organization: 

All the available accounts should show up in a Splunk Search window:  
![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_3.png?)

Now add the accounts into management:  
![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_4.png?)

Click the Add button: 

All the accounts in your organization will now show up in Splunk :  
![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_5.png?)

Now, add the destination where you will be sending your data. This is typically a Firehose endpoint on your Splunk Cloud Deployment. 
![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_6.png?)

Here is an example of how you should fill out the fields: 

Note that if you are using Splunk Cloud the URL for your firehose endpoint should look like this:
```
https://http-inputs-firehose-<customer_name>.splunkcloud.com:443
```

BYOL Cloud Deployments
```
https://<your-hec-url>:8088 
```

Where <customer_name> is your stack name. The port (:443) needs to be put in the URL in order for this system to work.
![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_6.png?)

Now let’s bulk upload your credentials file (all_accounts.json) that you created from all your credential.csv files: 
![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_11.png?)


Upload your file: 

Now, all your accounts should have their credentials added to your Splunk Deployment: 
![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_6a.png?)
![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_5a.png?)

Finally, now let’s deploy data collection to all these accounts: 

![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_7.png?)

Select the AWS accounts, regions and data source(s) you want to send into Splunk and click Deploy.

![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_8.png?)

Splunk will communicate with AWS and begin deploying the CloudFormation templates in all the accounts and regions you've selected:


In the Observation Deck dashboard you will see the succesfully deployed Accounts and Regions:
![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_10.png?)

Splunk will communicate with AWS and begin deploying the CloudFormation templates in all the accounts and regions you've selected:
![master_account]( https://grandcentraldeployment.s3.amazonaws.com/gc_9.png?)

