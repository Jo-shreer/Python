# AWS IAM — Complete Configuration Reference

## 1. What Is IAM?

IAM (Identity and Access Management) controls authentication and authorization in AWS.

- Authentication — verifies who or what is making a request.
- Authorization — determines which actions are allowed.
- Principal — the identity making a request, such as an IAM user, role, or AWS service.
- Resource — the AWS object being accessed, such as an S3 bucket or DynamoDB table.
- Policy — a document defining permissions.
- Credentials — information used to authenticate, such as access keys or temporary security credentials.
- Session — a temporary authenticated identity context.
- ARN — Amazon Resource Name identifying an AWS resource or IAM identity.

Example: A Lambda function assumes an IAM role that permits reading objects from one specific S3 bucket.

## 2. IAM Identity Types

### IAM User
- Represents a persistent IAM identity.
- Can have a console password, access keys, or both, depending on configuration.
- Avoid creating IAM users and long-lived access keys for application workloads.
- Use federation or IAM Identity Center for workforce access where appropriate.

### IAM Group
- Groups IAM users for easier permission management.
- Policies attached to a group apply to its users.
- Groups cannot be assumed as roles.
- Groups cannot contain other groups.

### IAM Role
- Provides permissions to an assumed identity session.
- Can be assumed by AWS services, users, or other authorized principals.
- Uses temporary credentials through AWS STS.
- Recommended for EC2, Lambda, ECS, EKS, and cross-account access.

### IAM Service-Linked Role
- A role linked to a specific AWS service.
- The service defines its trust relationship and may control its permissions.
- Created automatically or manually as required by the service.
- Do not modify or delete it without understanding the service dependency.

### IAM Service Role
- A role an AWS service assumes to perform actions on your behalf.
- Its trust policy identifies the service principal.
- Its permissions policy determines the allowed actions.

## 3. IAM Policies

A policy is a JSON document that defines permissions.

### Main Policy Types

- Identity-based policy — attached to a user, group, or role.
- Resource-based policy — attached to supported resources, such as S3 buckets, SQS queues, and KMS keys.
- Trust policy — attached to a role; defines who can assume it.
- Permissions boundary — limits the maximum permissions an identity-based policy can grant to a user or role.
- Service Control Policy (SCP) — sets maximum available permissions for accounts or organizational units in AWS Organizations.
- Resource Control Policy (RCP) — sets maximum available permissions on supported resources in an organization.
- Session policy — can restrict permissions for an assumed role session.
- Managed policy — reusable policy maintained by AWS or your organization.
- Inline policy — policy embedded directly in an identity.

Important:
- An Allow statement does not override an applicable explicit Deny.
- A permissions boundary does not grant permissions by itself.
- An SCP does not grant permissions by itself.
- A trust policy grants permission to assume a role; it does not define what the role can do after assumption.
- Resource-based policies and identity-based policies interact differently depending on the principal and account context.

## 4. IAM Policy JSON Attributes

Common policy document fields:

- `Version` — policy language version; normally `2012-10-17`.
- `Id` — optional identifier for the policy document.
- `Statement` — one or more permission statements.
- `Sid` — optional statement identifier.
- `Effect` — `Allow` or `Deny`.
- `Principal` — identity to which a resource-based statement applies.
- `NotPrincipal` — matches principals other than those specified; use carefully.
- `Action` — API actions to allow or deny.
- `NotAction` — matches actions other than those listed; can unintentionally grant broad access when combined with Allow.
- `Resource` — resources to which the statement applies.
- `NotResource` — matches resources other than those listed; use carefully.
- `Condition` — additional requirements that must be satisfied for a statement to apply.

### Common Condition Operators and Keys

- `StringEquals` — exact string comparison.
- `StringLike` — wildcard string comparison.
- `ArnEquals` — ARN comparison.
- `ArnLike` — ARN comparison with wildcard support.
- `Bool` — Boolean comparison.
- `IpAddress` — IP address or CIDR range match.
- `NotIpAddress` — does not match the specified IP range.
- `DateGreaterThan` — timestamp must be later than the specified date.
- `DateLessThan` — timestamp must be earlier than the specified date.
- `NumericLessThan` — numeric comparison.
- `Null` — checks whether a context key is present.
- `aws:PrincipalArn` — identifies the principal ARN in supported request contexts.
- `aws:PrincipalOrgID` — identifies the AWS Organization of the principal, where available.
- `aws:SourceAccount` — source account context for supported service-to-service requests.
- `aws:SourceArn` — source resource ARN for supported service-to-service requests.
- `aws:RequestedRegion` — requested AWS Region.
- `aws:SecureTransport` — indicates whether the request uses secure transport.
- `aws:MultiFactorAuthPresent` — MFA context for supported requests.
- `aws:TagKeys` — tag keys included in a request, where supported.
- `aws:ResourceTag/TagKey` — resource-tag condition key where supported.
- `aws:PrincipalTag/TagKey` — principal-tag condition key where supported.

Condition keys are not available in every request context. Check the documentation for the specific AWS service and action.

## 5. IAM Policy Example

Allow reading objects only from a specific application bucket prefix.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadApplicationReports",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::my-app-bucket/reports/*"
    }
  ]
}
```

Explanation:

- `Effect: Allow` — permits the specified action.
- `Action` — allows downloading or reading an object with `s3:GetObject`.
- `Resource` — limits access to objects under `reports/`.
- It does not grant bucket listing, object upload, or deletion.
- Other applicable policies and explicit Deny statements can still restrict access.

To list matching objects, the identity may also need `s3:ListBucket` on the bucket ARN, with an appropriate prefix condition.

## 6. IAM Role Trust Policy

A trust policy specifies who can assume a role.

Example: allow Lambda to assume a role.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Important:
- This trust policy allows Lambda to assume the role.
- It does not grant Lambda access to S3, DynamoDB, or other resources.
- Add permissions through separate identity-based policies.
- Cross-account roles should restrict trusted account principals and use appropriate conditions.
- For supported federation and role-assumption flows, use safeguards such as `sts:ExternalId`, source identity, or session tags where appropriate.

## 7. Authentication and Temporary Credentials

### Long-Lived Credentials
- IAM user password — console authentication.
- IAM user access key ID — identifies an access key.
- IAM user secret access key — signs programmatic requests.
- Avoid embedding long-lived credentials in source code, container images, or application configuration.

### Temporary Credentials
- Access key ID — temporary session identifier.
- Secret access key — temporary signing secret.
- Session token — additional credential required for temporary sessions.
- Expiration — time after which the credentials stop being valid.

### AWS STS Operations

- `AssumeRole` — assume an IAM role.
- `AssumeRoleWithWebIdentity` — assume a role using a supported web identity token.
- `AssumeRoleWithSAML` — assume a role using a SAML assertion.
- `GetSessionToken` — obtain temporary credentials for supported IAM user sessions.
- `GetCallerIdentity` — identify the AWS account and principal associated with the current credentials.

### Credential Delivery by Workload

- EC2 — instance profile associated with an IAM role.
- Lambda — execution role.
- ECS — task role for application code; task execution role for tasks that need AWS permissions for startup operations such as pulling images and sending logs.
- EKS — IAM roles for service accounts (IRSA) or EKS Pod Identity, depending on the architecture.
- CI/CD — prefer OIDC federation or an appropriately scoped role instead of stored long-lived AWS keys.
- Local development — prefer IAM Identity Center or another approved temporary-credential workflow.

## 8. Role Session Configuration

Common role-assumption and session parameters include:

- Role ARN — role being assumed.
- Role session name — identifies the session in logs and audit records.
- Duration seconds — requested session lifetime within the applicable service and role limits.
- External ID — optional shared identifier used in supported third-party cross-account access scenarios.
- Serial number — MFA device identifier where required.
- Token code — current MFA code where required.
- Policy — optional session policy that restricts permissions.
- Policy ARNs — managed session policies that further restrict permissions.
- Source identity — audit identity carried through supported role sessions.
- Session tags — key-value attributes attached to supported sessions.
- Transitive tag keys — session tags passed through supported role chaining.
- Provided contexts — context assertions for supported trusted identity propagation scenarios.

Important:
- The maximum session duration varies by role and service.
- Role chaining has a shorter maximum session duration than some direct role assumptions.
- A requested duration cannot exceed the applicable maximum.
- Session policies restrict permissions; they do not grant extra permissions.

## 9. IAM Identity Center and Federation

- IAM Identity Center — central workforce access to AWS accounts and applications.
- Permission set — defines the access configuration assigned to users or groups for AWS accounts.
- Identity source — Identity Center directory or supported external identity provider.
- SAML 2.0 — common federation protocol for workforce sign-in.
- OIDC — identity protocol used by supported applications and workload federation.
- External identity provider — provides authentication for federated users.
- SCIM — automates supported user and group provisioning.
- Account assignment — maps users or groups to an AWS account and permission set.

Production recommendation:
- Use IAM Identity Center for workforce access across multiple AWS accounts.
- Use federation rather than individual IAM users for most employees.
- Require MFA according to organizational security policy.
- Use separate accounts and permission sets for production and non-production access.

## 10. Cross-Account Access

Common use cases:
- A deployment account accesses a production account.
- A security account reads logs from other accounts.
- A central application accesses a resource in another account.
- A third-party service assumes a role in your account.

Required configuration depends on the access pattern:

- Trust policy — specifies the principal allowed to assume the target role.
- Caller permissions — allow the caller to perform the role-assumption operation when required.
- Role permissions — grant the actions needed in the target account.
- Resource policy — required where the target resource uses one for the chosen access model.
- KMS key policy — must permit the applicable cross-account cryptographic use.
- External ID — consider for third-party access to reduce confused-deputy risk.
- Organization conditions — restrict access to trusted accounts or organizations when appropriate.
- CloudTrail — audit role assumptions and subsequent API calls.

Do not use an entire account as a trusted principal unless that breadth is intentional and suitably constrained.

## 11. IAM Security Controls

- MFA — add an authentication factor for supported human access workflows.
- Least privilege — grant only required actions and resources.
- Access key rotation — replace long-lived keys when they must exist; prefer temporary credentials.
- Credential report — review IAM user credential status.
- Access Analyzer — identify supported unintended external access and validate policy findings.
- Service last accessed data — help identify unused permissions, where supported.
- Policy validation — check IAM policies for errors and security findings.
- CloudTrail — audit IAM changes, role assumptions, and supported API activity.
- Root user — avoid routine use; secure it with strong authentication and required safeguards.
- Root access keys — do not create them for routine workloads.
- Permissions boundaries — constrain permissions for delegated IAM administration.
- SCPs — limit maximum permissions across organization accounts.
- Break-glass access — maintain tightly controlled emergency access with monitoring.
- IAM Access Analyzer policy generation — can help draft policies from recorded activity, but review the output before deployment.
- Secrets Manager — store application secrets rather than hardcoding them.
- AWS Config — track supported IAM configuration and compliance.
- GuardDuty — detect supported suspicious account and credential activity.

## 12. Common AWS Permissions

### S3
- `s3:GetObject` — read an object.
- `s3:PutObject` — upload an object.
- `s3:DeleteObject` — delete an object or create a delete marker, depending on versioning.
- `s3:ListBucket` — list bucket objects.
- `s3:GetBucketLocation` — retrieve bucket Region information.

### DynamoDB
- `dynamodb:GetItem` — retrieve an item.
- `dynamodb:PutItem` — create or replace an item.
- `dynamodb:UpdateItem` — update an item.
- `dynamodb:DeleteItem` — delete an item.
- `dynamodb:Query` — query a table or index.
- `dynamodb:Scan` — scan a table or index.
- `dynamodb:DescribeTable` — retrieve table metadata.

### SQS
- `sqs:SendMessage` — send a message.
- `sqs:ReceiveMessage` — receive messages.
- `sqs:DeleteMessage` — delete received messages.
- `sqs:GetQueueAttributes` — retrieve queue attributes.

### KMS
- `kms:Encrypt` — encrypt data.
- `kms:Decrypt` — decrypt data.
- `kms:GenerateDataKey` — generate a data key.
- `kms:DescribeKey` — retrieve key metadata.

Important: KMS permissions can require both IAM authorization and a compatible KMS key policy. Some AWS service integrations also require service-specific permissions.

## 13. IAM Policy Evaluation Rules

When debugging access denied errors, check:

1. Is the caller authenticated with the expected credentials?
2. Is the role trust policy allowing the caller to assume the role?
3. Does the identity policy allow the requested action on the exact resource?
4. Is there an applicable explicit Deny?
5. Is a permissions boundary restricting the principal?
6. Is an SCP or RCP restricting the action or resource?
7. Does a resource-based policy allow or restrict access?
8. Are relevant session policies limiting the assumed role?
9. Are required KMS key policies and permissions correct?
10. Are condition keys, tags, IP ranges, Regions, and MFA requirements satisfied?
11. Is the request using the correct account, Region, ARN, and service endpoint?

The complete evaluation depends on the principal type, account boundary, resource type, and applicable policies. Do not assume that one Allow statement overrides every other restriction.

## 14. Common IAM Errors

- `AccessDenied` — missing permission, explicit Deny, failed condition, or another authorization restriction.
- `InvalidClientTokenId` — invalid, expired, or otherwise unusable credentials may be involved.
- `ExpiredToken` — temporary credentials have expired.
- `MalformedPolicyDocument` — policy JSON or policy structure is invalid.
- `NoSuchEntity` — requested IAM entity does not exist or cannot be found.
- `AssumeRole` denied — trust policy, caller permissions, external ID, MFA, or organization restrictions may be incorrect.
- S3 access denied — check identity policy, bucket policy, endpoint policy, ownership settings, and KMS permissions.
- KMS access denied — check IAM authorization and key policy.
- EKS workload access denied — check pod identity configuration, role trust, credential provider, and required permissions.
- ECS task access denied — check the task role versus the task execution role.
- EC2 access denied — check the instance profile and the role attached to the instance.

Use CloudTrail and the relevant service's diagnostic information to identify the actual cause.

## 15. Terraform Example — Lambda Execution Role

This example creates a role that Lambda can assume and permits reading objects only from a specific S3 prefix.

```hcl
resource "aws_iam_role" "app_lambda" {
  name = "app-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

resource "aws_iam_role_policy" "read_reports" {
  name = "read-app-reports"
  role = aws_iam_role.app_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject"
      ]
      Resource = "arn:aws:s3:::my-app-bucket/reports/*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role = aws_iam_role.app_lambda.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
```

Terraform notes:
- Replace `my-app-bucket` with your actual bucket name.
- The trust policy lets Lambda assume the role; the separate S3 policy grants application permissions.
- The AWS-managed logging policy grants standard CloudWatch Logs permissions needed by Lambda.
- Add only the extra permissions the function actually needs.
- If the bucket uses SSE-KMS with a customer-managed key, configure the necessary KMS permissions and key policy.
- If the function needs private VPC resources, configure its subnet and security group settings separately.
- Pin Terraform and AWS provider versions in production.
- Review the plan before applying changes.

## 16. Quick Decision Summary

- Need an AWS workload identity? Use an IAM role.
- Need permissions for employees across accounts? Use IAM Identity Center and permission sets.
- Need to authorize an action? Create a least-privilege policy.
- Need to allow a service to assume a role? Configure its trust policy.
- Need to restrict maximum permissions? Consider a permissions boundary and applicable organization policies.
- Need cross-account access? Configure trust, caller permissions, and target permissions for the chosen access pattern.
- Need application credentials? Prefer temporary role credentials over hardcoded access keys.
- Need to troubleshoot access denied? Check the caller identity, trust policy, identity policy, resource policy, explicit Deny, conditions, organization policies, and KMS permissions.
- Need auditability? Use CloudTrail and appropriate access-analysis and monitoring tools.

**Production rule:** Separate trust from permissions, use temporary credentials, avoid wildcard permissions when practical, and test policy changes before deploying them.

## 17. Official AWS Documentation

- IAM User Guide: https://docs.aws.amazon.com/IAM/latest/UserGuide/
- IAM policies and permissions: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html
- Policy evaluation logic: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html
- IAM roles: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html
- IAM best practices: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- IAM Identity Center: https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html
- AWS STS: https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html
- IAM Access Analyzer: https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html
