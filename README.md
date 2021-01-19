# Grand Central App for Splunk
## Manage and Monitor your Cloud Data Providers in Splunk from one centralized data platform.
> This Splunk based app relies on the work done by Project Trumpet and the AWS Organizational model.
### Grand Central User's Guide :
* Version 3.0.1
#### Getting Started

**Requirements**
Grand Central works with the **AWS Organizations framework** and does not require either Landing Zone or Control Tower to work. By having the organization setup with multiple accounts, Grand Central will be able to discover the accounts and add into management within Splunk.
Please refer to the Amazon Web Services documentation on [how to get started with Organizations](https://aws.amazon.com/premiumsupport/knowledge-center/get-started-organizations/).

#### Architecture
![architecture](https://grandcentraldeployments.s3.amazonaws.com/architecture/Control+Tower+Marketplace+offering+-+Account+Vend+_+OU+Placement.png)

#### Before Deploying Grand Central
You will need to be able to create an IAM User in the Master Account and the sub accounts that will be added into management under Splunk. By default there will be two IAM policies created, one to list all the accounts in the Organization and the second will be a deployment policy.

IAM Role Creation Shortcut (Simplified)
1. Log into your Master AWS Account [AWS Account](https://console.aws.amazon.com):
![aws_console](https://grandcentraldeployments.s3.amazonaws.com/screenshots/aws_console.png)

2. Click on [Grand Central Create](https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/quickcreate?templateUrl=https%3A%2F%2Fgrandcentraldeployments.s3.amazonaws.com%2FGC_StackSet_UserCreate_CFTemplate.json&stackName=GrandCentralMasterIAMUserCreate) 
![iam_create_cf](https://grandcentraldeployments.s3.amazonaws.com/screenshots/IAM_Create_CF.png) 


3. Copy the Access Key / Secret Key from CloudFormation Output :
![copy_ak_sk](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gcuser01.png)

4. Download [grand_central_300.spl](https://grandcentraldeployments.s3.amazonaws.com/grand_central_300.spl) file from S3 bucket and install on your Splunk instance. Splunk Cloud customers request to have the app installed. 
![install_gc](https://grandcentraldeployments.s3.amazonaws.com/screenshots/install_gc.png)

#### Cloudformation Template for IAM User Creation
Here is the Cloudformation template used for this IAM Role Creation : https://github.com/amiracle/grand_central/blob/master/aws_artifacts/cf_templates/GC_StackSet_UserCreate_CFTemplateRev2.json

Here is the policy which it will deploy for reference: 


**IAM Policy - GCPolicy_Rev2.json**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CFTemplateSSInstance",
            "Effect": "Allow",
            "Action": [
                "cloudformation:CreateStackInstances",
                "cloudformation:DeleteStackInstances"
            ],
            "Resource": [
                "arn:aws:cloudformation:*:*:stackset-target/grandcentral*",
                "arn:aws:cloudformation:*:*:stackset/grandcentral*",
                "arn:aws:cloudformation:*::type/resource/AWS-IAM-Role",
                "arn:aws:cloudformation:*::type/resource/AWS-S3-Bucket",
                "arn:aws:cloudformation:*::type/resource/AWS-Lambda-Function",
                "arn:aws:cloudformation:*::type/resource/AWS-KinesisFirehose-DeliveryStream",
                "arn:aws:cloudformation:*::type/resource/AWS-IAM-Policy",
                "arn:aws:cloudformation:*::type/resource/AWS-Events-Rule"
            ]
        },
        {
            "Sid": "CFTemplateCreateStackSet",
            "Effect": "Allow",
            "Action": [
                "cloudformation:CreateStackSet",
                "cloudformation:DeleteStackSet"
            ],
            "Resource": [
                "arn:aws:cloudformation:*:*:stackset/grandcentral*",
                "arn:aws:cloudformation:*::type/resource/AWS-IAM-Role",
                "arn:aws:cloudformation:*::type/resource/AWS-S3-Bucket",
                "arn:aws:cloudformation:*::type/resource/AWS-Lambda-Function",
                "arn:aws:cloudformation:*::type/resource/AWS-KinesisFirehose-DeliveryStream",
                "arn:aws:cloudformation:*::type/resource/AWS-IAM-Policy",
                "arn:aws:cloudformation:*::type/resource/AWS-Events-Rule"
            ]
        },
        {
            "Sid": "OrganizationList",
            "Effect": "Allow",
            "Action": [
                "organizations:List*",
                "organizations:DescribeOrganization",
                "organizations:DescribeOrganizationalUnit",
                "organizations:EnableAWSServiceAccess"
            ],
            "Resource": "*",
            "Condition": {
                "ForAllValues:StringLike": {
                    "organizations:ServicePrincipal": [
                        "cloudformation.*.amazonaws.com",
                        "cloudformation-fips.*.amazonaws.com",
                        "cloudtrail.*.amazonaws.com",
                        "cloudtrail-fips.*.amazonaws.com",
                        "config.*.amazonaws.com",
                        "config-fips.*.amazonaws.com",
                        "events.*.amazonaws.com",
                        "events-fips.*.amazonaws.com",
                        "logs.*.amazonaws.com",
                        "logs-fips.*.amazonaws.com",
                        "s3.amazonaws.com",
                        "s3.*.amazonaws.com",
                        "organizations.*.amazonaws.com"
                    ]
                }
            }
        }
    ]
}
```
**IAM Policy - Grand_Central_IAM_Policy.json**
Grand Central Policy for Master Account : 
- [GCPolicy_Rev2.json] https://github.com/amiracle/grand_central/blob/master/aws_artifacts/IAM_Policy/GCPolicy_Rev2.json
Use this policy to setup and deploy Grand Central in a Control Tower / AWS Organization deployment. This will use StackSets to deploy configuraiton changes to sub accounts in AWS. 

Individual Account IAM Policy (Optional)
> If you are going to use individual accounts and policies in each account, use this IAM policy. 
> Grand Central Policy for Individual AWS Accounts :
> [Grand_Central_IAM_Policy.json](https://github.com/amiracle/grand_central/blob/master/aws_artifacts/IAM_Policy/Grand_Central_IAM_Policy.json)

### Setting up Grand Central

**Adding Master Account**
Log into the Grand Central App and navigate to the Accounts Section (Configure Data Sources -> Amazon Web Services -> Grand Central Accounts).
> https://yoursplunk.com:8000/en-US/app/grand_central/grand_central_accounts

Click on the “New Organization Master Account” button:

![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_01.png)

Add the Master Account ID (must be a number) access key / secret key to Splunk:

![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_02.png)

The Master Account should now show up in Splunk:

![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_03.png)

Once the Master Account has been added, now you should be able to view the accounts in the organization. Under Actions, navigate to the List All Accounts in the dropdown:
![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_04.png)

List of all the accounts:
![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_07.png)

In order to add the discovered accounts into Splunk, select "**Add Accounts in Organization to Grand Central**" in the Actions dropdown:
![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_05.png)

Click on the Add Button:

![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_06.png)

All the accounts should now show up under management in Splunk:
![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_08.png)

**Splunk Endpoints**
Now, add the destination where you will be sending your data. This is typically a Firehose endpoint on your Splunk Cloud Deployment.
Here is an example of how you should fill out the fields:
Note that if you are using Splunk Cloud the URL for your firehose endpoint should look like this:
```md
https://http-inputs-firehose-mystack.splunkcloud.com:443
```
![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_ec.png)

BYOL Cloud Deployments
```md
https://mystack.com:8088
```
![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_by.png)

**AWS Stacksets**
Define your AWS Stackset here in Splunk. What will happen is as new accounts are vended into Organizational Units (OU's), they will automatically have these configurations sent to the newly AWS Accounts. Addiontally, if an existing account is moved into an OU, it will be configured with these settings.

Example : Account 987654321 is in the Core OU after being provisioned, then gets moved into the DevOps OU, the AWS Stackset "grandcentralCloudTrail" will deploy in that account and setup the CloudTrail data collection.

***Deploy an AWS Stackset***

![aws_stack_set](https://grandcentraldeployments.s3.amazonaws.com/screenshots/aws_stackset.png)

Your Splunk Accounts should look like this when you're done:
![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_10.png)
> ### **Pro Tip :** For now, create a Splunk HEC token for each sourcetype. E.g. `aws:cloudtrail` for CloudTrail, `aws:config` for Config, and `aws:cloudwatchlogs:vpcflow` for VPCFlow Logs

The legacy Bulk Data Deployment system still works if you do not want to use AWS Stacksets and would rather use Access Key / Secret Keys for each of your accounts. Just follow the steps for the Bulk Credential Upload or set up each account individually. Now you can deploy data collection to all these accounts, click on the Bulk Deployment button and select your accounts, regions, destination and data source:
![master_account]( https://grandcentraldeployments.s3.amazonaws.com/screenshots/13_gc.png)
Click Deploy.
Splunk will communicate with AWS and begin deploying the CloudFormation templates in all the accounts and regions you've selected:
In the Observation Deck dashboard you will see the successfully deployed Accounts and Regions:
![master_account](https://grandcentraldeployments.s3.amazonaws.com/screenshots/gc2_09.png)
    # Binary File Declaration
    ## Terraform
    - Binary and Checksum: https://releases.hashicorp.com/terraform/0.12.19/
    - Source Code: https://github.com/hashicorp/terraform
    
#### Alternative deployments

Under the hood, Grand Central is simply storing account configurations and deploying Stacksets/CloudFormation templates to those accounts, however the state and persistence of the Stackset/Cloudformation stack itself is stored within the AWS services. It is therefore possible to deploy the same architecture deployed by Grand Central using the native Stacket/Cloudformation consoles and CLI tools to better match any existing IaaS workflows you may already be using. 

This section will briefly describe how to manually deploy the same architecture as Grand Central. This is especially relevant for users with concerns about long term storage of account credentials. Note that this section will be describing how to manually deploy to an AWS Organization using Stacksets, rather than individual accounts using Cloudformation. To deploy customized data collection Cloudformation templates to individual AWS accounts without Grand Central, please see [Project Trumpet](https://github.com/splunk/splunk-aws-project-trumpet).

There are two main options for deploying the data collection infrastructure set up by Grand Central without relying on the Grand Central app for management of the stacks. 

* Follow all the same steps as deploying Grand Central to an AWS Organization (Create and provide a Master Account credential, add accounts in the organization to Grand Central, then deploy one or more Stacksets to the relevant Organizational Units (OUs) and regions). 
    * Once this is complete, you can safely remove the Master Account from Grand Central, delete the Master Account user/credential, and even uninstall the Grand Central app. The data collection deployment created by Grand Central will still exist after the app is uninstalled or the Master account credential is deleted. 
    * Be sure to note the name of the Stackset deployment. 
    * To edit or roll back the deployment, you will need to interact with the Stackset in the AWS console. 
    * In this approach, Grand Central is used as a quickstart for deployment, and long term management/maintenance is done within native AWS services.

* Instead of deploying the Stackset through Grand Central, you can instead manually deploy the same Stackset within the AWS Console or through the AWS CLI. This is a straightforward process, which will be described in more detail here. 
	* The first step will be to create a template using Project Trumpet, this template should be deployable to all accounts and regions that you plan to deploy to, meaning that if CloudWatch Log or VPC Flow log groups are provided, they must exist (have the same name) in each account/region that the Stackset will deploy the template to. Services like CloudTrail exist in all regions/accounts and can be included. 

	* The next step is to deploy the template using AWS Stacksets in the Master Account with trusted access enabled, from here, you can select which Organization Units (OUs) you would like the template to apply to, as well as regions.

	* Note that Grand Central deploys using the assumption that the Master Account has trusted access enabled, this allows the master account to deploy the Stackset to accounts within the organization without having to configure trust policies for each account. See more about this approach [here](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-orgs-enable-trusted-access.html).
