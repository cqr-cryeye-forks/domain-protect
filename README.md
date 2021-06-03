# domain-protect
scans Amazon Route53 across an AWS Organization for domain records vulnerable to takeover

### receive alerts by Slack or email

![Alt text](slack-ns.png?raw=true "Slack notification")

### scan your entire AWS Organization

![Alt text](multi-account.png?raw=true "Multi account setup")

### deploy to security audit account

![Alt text](domain-protect.png?raw=true "Domain Protect architecture")

## subdomain detection functionality
* scans Amazon Route53 for ElasticBeanstalk Alias records vulnerable to takeover
* scans Amazon Route53 for ElasticBeanstalk CNAMES vulnerable to takeover
* scans Amazon Route53 for S3 Alias records vulnerable to takeover
* scans Amazon Route53 for S3 CNAMES vulnerable to takeover
* scans Amazon Route53 for subdomain NS delegations vulnerable to takeover

## options
1. scheduled lambda functions with email and Slack alerts, across an AWS Organization, deployed using Terraform
2. [manual scans](manual-scans/README.md) run from your laptop or CloudShell, in a single AWS account

## notifications
* Slack channel notification per vulnerability type, listing account names and vulnerable domains
* Email notification in JSON format with account names, account IDs and vulnerable domains by subscribing to SNS topic

## requirements
* Security audit account within AWS Organizations
* Security audit read-only role with an identical name in every AWS account of the Organization
* Storage bucket for Terraform state file
* Terraform 15.x

## usage
* replace the Terraform state S3 bucket fields in the command below as appropriate
* alternatively, update backend.tf following backend.tf.example
* duplicate terraform.tfvars.example, rename without the .example suffix
* enter details appropriate to your organization and save
* alternatively enter these Terraform variables within your CI/CD pipeline

```
terraform init -backend-config=bucket=TERRAFORM_STATE_BUCKET -backend-config=key=TERRAFORM_STATE_KEY -backend-config=region=TERRAFORM_STATE_REGION
terraform workspace new dev
terraform plan
terraform apply
```

## AWS IAM policies
For least privilege access control, example AWS IAM policies are provided:
* [domain-protect audit policy](aws-iam-policies/domain-protect-audit.json) - attach to domain-protect audit role in every AWS account
* [domain-protect deploy policy](aws-iam-policies/domain-protect-deploy.json) - attach to IAM group or role assumed by CI/CD pipeline

## adding new checks
* create a new subdirectory within the terraform-modules/lambda/code directory
* add Python code file with same name as the subdirectory
* add the name of the file without extension to ```var.lambdas``` in [variables.tf](variables.tf)
* add a subdirectory within the terraform-modules/lambda/build directory, following the existing naming pattern
* add a .gitkeep file into the new directory
* update the .gitignore file following the pattern of existing directories  
* apply Terraform

## adding notifications to extra Slack channels
* update ```var.slack_channels``` with an additional list element
* update ```var.slack_webhook_urls``` with an additional list element
* apply Terraform

## testing
* use multiple Terraform workspace environments, e.g. dev, prd
* configure your dev Terraform variables to notify to a test Slack channel
* for new subdomain takeover categories, create correctly configured and vulnerable domain names in Route53
* minimise the risk of malicious takeover by using a test domain, with domain names which are hard to enumerate
* remove any vulnerable domains as soon as possible

## ci/cd
* infrastructure has been deployed using CircleCI
* environment variables to be entered in CircleCI project settings:

| ENVIRONMENT VARIABLE            | EXAMPLE VALUE / COMMENT                      |
| ------------------------------- | ---------------------------------------------|
| AWS_ACCESS_KEY_ID               | using [domain-protect deploy policy](aws-iam-policies/domain-protect-deploy.json)|
| AWS_SECRET_ACCESS_KEY           | -                                            |
| SLACK_CHANNEL                   | security-alerts                              |
| SLACK_CHANNEL_DEV               | security-alerts-dev                          |
| SLACK_WEBHOOK_URL               | https://hooks.slack.com/services/XXX/XXX/XXX | 
| TERRAFORM_STATE_BUCKET          | tfstate48903                                 |
| TERRAFORM_STATE_KEY             | domain-protect                               |
| TERRAFORM_STATE_REGION          | us-east-1                                    |  
| TF_VAR_org_primary_account      | 012345678901                                 | 
| TF_VAR_security_audit_role_name | security-audit                               |
| TF_VAR_external_id              | only required if External ID is configured   |

* to validate an updated CircleCI configuration:
```
docker run -v `pwd`:/whatever circleci/circleci-cli circleci config validate /whatever/.circleci/config.yml
```

## limitations
* this tool cannot guarantee 100% protection against subdomain takeover
* it currently only scans Amazon Route53, and only checks a limited number of takeover types