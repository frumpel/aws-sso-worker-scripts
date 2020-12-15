# Scripts to automate boto3 with SSO

A collection of utility scripts to use AWS SSO to log in and then iterate a boto3 based function across multiple accounts and regions.

These are for personal use and come with no warranties whatsoever. Please also note that automating across multiple accounts is a very good way to get very bad results so please test this with really constrained settings before running anything that could be destructive ...

## Get / set account password policies

AWS supports account password policies and has API bindings to for get/set but as of this writing does not have support for automation via CloudFormation, ControlTower, or Organizations. 

These two scripts will use your SSO login to obtain temporary credentials to all accounts assocated with your role and get existing settings or set _hardcoded_ new settings. Make sure you like those hardcoded settings ... 

For `SSO_URL` use the same url you would use for the AWS SSO login page. For `SSO_REGION` use the region in which SSO is configured. If you are using ControlTower this should likely be the same region.

```
export SSO_URL=https://ACCOUNT_NUMBER.awsapps.com/start
export SSO_REGION=us-west-2
python3 get_password_policy.py
```

Similar for set_password_policy, but please make sure to edit the file to suit your needs first!