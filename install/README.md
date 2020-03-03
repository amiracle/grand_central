# Grand Central AWS setup steps

1. Install Splunk and Grand Central on an AWS instance
2. Create an IAM role and attach it to the AWS instance ([IAM Roles for EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)) on which you are running Grand Central. Take note of the IAM Instance Role ARN e.g. arn:aws:iam::123456789:role/SplunkInstanceProfileRole)
3. In the AWS Organisation Master account, create the "SplunkOrgListerCrossAccountRole" Cloudformation stack (using template: SplunkOrgListerCrossAccountRoleCF.yaml) and enter the Instance Role ARN as a stack input.
4. In the AWS target accounts, create the "SplunkDataCollectionCrossAccountRole" Cloudformation stack (using template: SplunkGrandCentralDataCollectionCF.yaml) and enter the Instance Role ARN as a stack input.
5. In Grand Central, setup your AWS Organization Master Account. For the AWS Access Key and Secret Key, just enter "ABC123" or any other text. Then List/Add accounts in the Organisation to Grand Central
6. Setup each of the AWS Accounts by editing the account and entering "ABC123" or similar into the AWS Access Key and Secret Key fields
7. Deploy Cloudformation templates to the accounts
