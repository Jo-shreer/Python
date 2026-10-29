# AWS IAM — Complete Notes with Terraform Examples

## 1. What is IAM?

IAM stands for Identity and Access Management.

It controls:
- Who can access AWS resources.
- What actions they can perform.
- Which resources they can access.
- Under what conditions access is allowed.

Examples of AWS resources: EC2, S3, Lambda, RDS.

---

## 2. What is an IAM Role?

An IAM role is an identity with permissions that an authorized entity can assume to obtain temporary security credentials.

Example: An EC2 application needs to read files from an S3 bucket. Instead of storing AWS access keys in application code, we attach an IAM role to the EC2 instance.

A role has two important components:

1. Trust policy — WHO can assume the role?
2. Permissions policy — WHAT can the role do?

### Terraform: Create an IAM Role

```hcl
resource "aws_iam_role" "ec2_s3_role" {
  name = "EC2S3Role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "ec2.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })
}
```

Explanation:

- `aws_iam_role` — Terraform resource type that creates an IAM role.
- `ec2_s3_role` — Terraform resource label.
- `name` — Actual role name in AWS.
- `assume_role_policy` — The role's trust policy.
- `Principal` — Who is trusted to assume the role.
- `Service = "ec2.amazonaws.com"` — Trusts the EC2 service.
- `Action = "sts:AssumeRole"` — Allows the trusted principal to assume the role, subject to applicable authorization rules.
- `jsonencode()` — Converts the Terraform object into JSON.

Important: This creates the role and its trust policy. It does not automatically grant S3 permissions.

---

## 3. What Is a Trust Policy?

A trust policy specifies which principals can assume an IAM role.

It answers: WHO is allowed to assume this role?

Example:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Service": "ec2.amazonaws.com"
    },
    "Action": "sts:AssumeRole"
  }]
}
```

Explanation:

- `Principal` — Identifies the trusted entity.
- `Service` — Specifies an AWS service.
- `sts:AssumeRole` — The role-assumption action.
- `Effect: Allow` — Allows the specified action, subject to any conditions and other applicable rules.

Other principal examples:

```json
"Principal": {
  "Service": "lambda.amazonaws.com"
}
```

This trusts the Lambda service to assume the role.

```json
"Principal": {
  "AWS": "arn:aws:iam::123456789012:root"
}
```

This identifies the specified AWS account as a trusted principal. It does not automatically authorize every identity in that account; the trust policy and applicable permissions still determine whether a particular caller can assume the role.

Important distinction:

- Role = the identity.
- Trust policy = who can assume that identity.
- Permissions policy = what the assumed role can do.

In Terraform, the trust policy is configured inside the IAM role's `assume_role_policy` argument. It is not a separate IAM role resource.

---

## 4. What Is an IAM Policy?

An IAM policy is a JSON document that defines permissions.

A policy statement commonly contains:

- `Effect` — Allow or Deny.
- `Action` — The AWS operation.
- `Resource` — The resource the operation applies to.
- `Condition` — Additional requirements, when needed.
- `Principal` — Used in resource-based policies and role trust policies, not ordinary identity-based permissions statements.

### Example: Allow Reading S3 Objects

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::company-reports/*"
  }]
}
```

Explanation:

- `s3:GetObject` — Allows reading objects.
- `company-reports/*` — Applies to objects inside the bucket.
- This does not grant permission to upload or delete objects.

---

## 5. What Is an ARN?

ARN stands for Amazon Resource Name.

It identifies an AWS resource.

Example:

```text
arn:aws:iam::123456789012:policy/CompanyReportsReadPolicy
```

Parts:

- `arn` — Identifies the string as an ARN.
- `aws` — AWS partition.
- `iam` — AWS service.
- `123456789012` — Example AWS account ID.
- `policy/CompanyReportsReadPolicy` — Policy resource and name.

### How Terraform Gets an ARN

```hcl
resource "aws_iam_policy" "s3_read_policy" {
  name = "CompanyReportsReadPolicy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = ["arn:aws:s3:::company-reports/*"]
    }]
  })
}
```

Although we do not define the IAM policy's own ARN, AWS generates it when the policy is created. The Terraform AWS provider exposes it as an attribute.

We can reference it using:

```hcl
aws_iam_policy.s3_read_policy.arn
```

Terraform reference format:

```text
resource_type.resource_label.attribute
```

For example:

- `aws_iam_policy` — Resource type.
- `s3_read_policy` — Terraform label.
- `arn` — Resource attribute returned by the provider.

Common attributes include `.arn`, `.id`, and `.name`, depending on the resource type.

---

## 6. Inline Policy vs Managed Policy

There are two common ways to give permissions to an IAM role.

### A. Inline Policy

An inline policy is embedded directly in one IAM identity, such as a role.

Terraform resource:

`aws_iam_role_policy`

Example:

```hcl
resource "aws_iam_role_policy" "cleanup_s3" {
  name = "CleanupTempFiles"
  role = aws_iam_role.ec2_s3_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:DeleteObject"]
      Resource = ["arn:aws:s3:::company-data/temp/*"]
    }]
  })
}
```

Explanation:

- `aws_iam_role_policy` — Creates an inline policy.
- `role` — Identifies the role to which it belongs.
- `policy` — Defines the permissions directly.

The policy is associated with that one role. You cannot reuse the same inline policy as a shared policy across multiple roles.

Production use case:

A cleanup Lambda needs permission to delete temporary files from one specific S3 prefix. If this permission is unique to the cleanup role, an inline policy may be appropriate.

### B. Customer-Managed Policy

A customer-managed policy is created separately and can be attached to multiple IAM roles, users, or groups.

Terraform resource:

`aws_iam_policy`

Create the policy:

```hcl
resource "aws_iam_policy" "s3_read_policy" {
  name = "CompanyReportsReadPolicy"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = ["arn:aws:s3:::company-reports/*"]
    }]
  })
}
```

Attach it to a role:

```hcl
resource "aws_iam_role_policy_attachment" "attach_s3_read" {
  role       = aws_iam_role.ec2_s3_role.name
  policy_arn = aws_iam_policy.s3_read_policy.arn
}
```

Explanation:

- `aws_iam_policy` — Creates a separate customer-managed policy.
- `aws_iam_role_policy_attachment` — Attaches the existing policy to a role.
- `.arn` — References the generated policy ARN.
- The same managed policy can be attached to multiple roles.

Production use case:

Several Lambda roles need the same read permissions for a shared S3 bucket. Create one customer-managed policy and attach it to all roles that genuinely need those permissions.

If the applications require different access, use separate least-privilege policies instead of sharing overly broad permissions.

### C. AWS-Managed Policy

AWS creates and maintains these policies.

Example:

```hcl
resource "aws_iam_role_policy_attachment" "s3_read" {
  role       = aws_iam_role.ec2_s3_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}
```

Explanation:

- `AmazonS3ReadOnlyAccess` is an AWS-managed policy.
- We do not define its permissions in this Terraform block.
- We attach the existing policy using its ARN.
- Review its scope because it may provide broader access than a particular application needs.

### Comparison

| Feature | Inline policy | Customer-managed policy | AWS-managed policy |
|---|---|---|---|
| Terraform resource | `aws_iam_role_policy` | `aws_iam_policy` | Attach using `aws_iam_role_policy_attachment` |
| Created by | You | You | AWS |
| Reusable across roles | No | Yes | Yes |
| Permissions defined by | You | You | AWS |
| Typical use | Unique role-specific permissions | Shared, centrally managed permissions | Standard AWS permission sets |

Important:

The difference is not simply whether a `role` argument appears in the code. The Terraform resource type determines what is being created.

- `aws_iam_role_policy` creates an inline policy.
- `aws_iam_policy` creates a separate customer-managed policy.
- `aws_iam_role_policy_attachment` attaches an existing managed policy.

---

## 7. Why Does an Inline Policy Specify a Role?

Example:

```hcl
resource "aws_iam_role_policy" "s3_read" {
  name = "S3ReadPolicy"
  role = aws_iam_role.ec2_s3_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = ["arn:aws:s3:::company-reports/*"]
    }]
  })
}
```

This is inline because `aws_iam_role_policy` is the resource type for an inline role policy.

The `role` argument tells Terraform which role receives the inline policy.

Compare this with a managed policy:

```hcl
resource "aws_iam_policy" "s3_read" {
  name = "S3ReadPolicy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = ["arn:aws:s3:::company-reports/*"]
    }]
  })
}
```

Here, no role is specified because the policy is created separately. The role is specified when attaching the policy.

---

## 8. What Is a Principal?

`Principal` identifies WHO is allowed to access a resource or assume a role, depending on the policy.

Example in a role trust policy:

```json
"Principal": {
  "Service": "ec2.amazonaws.com"
}
```

This identifies the EC2 service as the trusted principal.

Remember:

- `Principal` — Who?
- `Action` — What operation?
- `Resource` — Which resource?
- `Condition` — Under what additional requirements?

In an ordinary identity-based permissions policy, you generally do not specify `Principal`, because the policy is attached to the identity whose permissions it defines.

---

## 9. What Is a Condition in an IAM Policy?

A condition adds extra requirements to a policy statement.

Conditions can appear in trust policies, identity-based policies, and resource-based policies where supported.

### A. Source IP Condition

Use case: Allow S3 listing only from a particular public IP.

```json
"Condition": {
  "IpAddress": {
    "aws:SourceIp": "203.0.113.10/32"
  }
}
```

Explanation:

- `IpAddress` — Checks the request's IP address.
- `aws:SourceIp` — The AWS condition key.
- `/32` — Specifies one IPv4 address.

The IP shown is a documentation example, not a real office address.

### B. MFA Condition

Use case: Require MFA for certain sensitive actions.

```json
"Condition": {
  "Bool": {
    "aws:MultiFactorAuthPresent": "true"
  }
}
```

Explanation:

- `Bool` checks a Boolean value.
- `aws:MultiFactorAuthPresent` indicates whether MFA was used for the request.

This key is useful for certain MFA-backed temporary credentials. It does not universally enforce MFA for all federated users or role sessions; those scenarios may require trust-policy or identity-provider controls.

### C. Region Condition

Use case: Limit a policy statement to requests targeting the Ireland region.

```json
"Condition": {
  "StringEquals": {
    "aws:RequestedRegion": "eu-west-1"
  }
}
```

Explanation:

- `StringEquals` checks an exact string match.
- `aws:RequestedRegion` identifies the target region.

This restricts the applicable requests but does not necessarily prevent every cross-region effect of an operation.

### D. Resource Tag Condition

Use case: Allow an EC2 operation only on instances tagged for Development.

```json
"Condition": {
  "StringEquals": {
    "ec2:ResourceTag/Environment": "Development"
  }
}
```

Explanation:

- `ec2:ResourceTag/Environment` checks the resource's Environment tag.
- `StringEquals` requires the value to be exactly `Development`.

This works only for actions that support the relevant resource-tag condition key.

### E. External ID Condition in a Trust Policy

Use case: A third-party service assumes a role in your account.

```hcl
resource "aws_iam_role" "third_party_role" {
  name = "ThirdPartyRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        AWS = "arn:aws:iam::123456789012:root"
      }

      Action = "sts:AssumeRole"

      Condition = {
        StringEquals = {
          "sts:ExternalId" = "unique-example-id"
        }
      }
    }]
  })
}
```

Explanation:

- `Principal` identifies the trusted AWS account.
- `sts:AssumeRole` specifies the role-assumption action.
- `sts:ExternalId` requires the caller to supply the matching external ID.

Use the actual account ID and external ID for the integration. An external ID helps address the confused-deputy problem in third-party access; it is not a password or a substitute for other security controls.

### Common Condition Operators

| Operator | Meaning |
|---|---|
| `StringEquals` | Exact string match |
| `StringLike` | Pattern-based string match |
| `NumericLessThan` | Number must be less than a specified value |
| `Bool` | Boolean comparison |
| `IpAddress` | IP address or CIDR match |
| `NotIpAddress` | IP address must not match the specified range |
| `DateGreaterThan` | Date must be later than a specified date |
| `ArnEquals` | Exact ARN match |

Important: A condition does not grant permission on its own. It adds a requirement to a policy statement. If the condition fails, that statement does not grant access. Other applicable policies and explicit denies still affect the final authorization decision.

---

## 10. EC2 + IAM Role + S3: Complete Relationship

For an EC2 application to read objects from S3:

1. Create an IAM role.
2. Add a trust policy allowing EC2 to assume the role.
3. Create or choose a permissions policy allowing the required S3 actions.
4. Attach the permissions policy to the role, or define an inline policy.
5. Create an instance profile and associate it with the EC2 instance.
6. The application obtains temporary credentials through the EC2 instance metadata service.
7. AWS evaluates applicable permissions when the application requests S3 access.

### Terraform Instance Profile

```hcl
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "EC2S3Profile"
  role = aws_iam_role.ec2_s3_role.name
}
```

### Attach the Profile to EC2

```hcl
resource "aws_instance" "app" {
  ami                  = "ami-REPLACE_WITH_VALID_AMI_ID"
  instance_type        = "t3.micro"
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name
}
```

Replace the AMI placeholder with a valid image ID for the chosen region.

---

## 11. Important IAM Rules to Remember

- Authentication answers: Who are you?
- Authorization answers: What are you allowed to do?
- A role's trust policy determines who can assume it.
- A role's permissions policies determine what it can do.
- An explicit Deny overrides an Allow.
- Access is generally denied when no applicable permission allows the action.
- A role can have multiple permissions policies.
- A managed policy can be shared by multiple identities.
- An inline policy is associated with one identity.
- A resource-based policy can grant access directly to a resource, subject to AWS authorization rules.
- IAM roles commonly provide temporary credentials instead of requiring long-term access keys.
- Use least privilege in production and review policy scope carefully.


# AWS IAM + Terraform Notes

## 1. What is IAM?

IAM (Identity and Access Management) controls **who can access AWS and what they can do**.

- **User:** An identity for a person or application.
- **Group:** A collection of IAM users.
- **Role:** An identity that can be assumed temporarily by a trusted entity.
- **Policy:** A document defining permissions.
- **Trust policy:** Defines who can assume a role.
- **Permissions policy:** Defines what actions are allowed or denied.

## 2. What is an IAM role?

An IAM role provides temporary permissions to an AWS service, user, or external account.

**Production example:** An EC2 instance needs to read files from S3. Instead of storing AWS access keys on the EC2 instance, attach a role that grants the required S3 access.

```hcl
resource "aws_iam_role" "ec2_role" {
  name = "ec2-s3-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}
```

`assume_role_policy` is the role's **trust policy**. It tells AWS that EC2 is trusted to assume this role.

## 3. Trust policy vs permissions policy

### Trust policy

Controls **who can assume the role**.

Example: Allow EC2 to assume a role.

```json
{
  "Effect": "Allow",
  "Principal": {
    "Service": "ec2.amazonaws.com"
  },
  "Action": "sts:AssumeRole"
}
```

### Permissions policy

Controls **what the assumed role can do**.

Example: Allow reading objects from an S3 bucket.

```json
{
  "Effect": "Allow",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::my-app-bucket/*"
}
```

Remember: trusting EC2 to assume a role does not automatically give the role S3 access. The role also needs appropriate permissions.

## 4. What is Principal?

`Principal` identifies **who or what is allowed to assume a role** in its trust policy.

Examples:

```json
"Principal": {
  "Service": "ec2.amazonaws.com"
}
```

An AWS service such as EC2.

```json
"Principal": {
  "AWS": "arn:aws:iam::123456789012:root"
}
```

An AWS account principal. This generally delegates trust to that account; the account's own permissions and applicable controls determine who can use it.

## 5. What are Action, Resource, and Condition?

- `Action`: What operation is allowed or denied.
- `Resource`: Which AWS resource the statement applies to.
- `Condition`: The circumstances under which the statement applies.

Example:

```json
{
  "Effect": "Allow",
  "Action": "s3:DeleteObject",
  "Resource": "arn:aws:s3:::my-app-bucket/temp/*",
  "Condition": {
    "IpAddress": {
      "aws:SourceIp": "203.0.113.10/32"
    }
  }
}
```

This statement allows deleting objects under the `temp/` prefix when the request comes from the specified IP address, subject to other applicable AWS authorization controls.

## 6. Where can we add Conditions: role, policy, or both?

**Conditions can be added to both the role's trust policy and its permissions policies.** They serve different purposes.

| Location | What the condition controls | Example |
|---|---|---|
| Role trust policy (`assume_role_policy`) | Who can assume the role and under what circumstances | Require an external ID for a third-party role |
| Permissions policy | When an action is permitted on a resource | Allow deleting S3 objects only from a specific IP |
| Both | Two layers of access control | Restrict role assumption and restrict what the role can do afterward |

A role's trust policy is defined using `assume_role_policy`. Conditions in the permissions policy belong inside the policy's `Statement`.

### A. Conditions in a role's trust policy

**Production use case:** A third-party vendor needs to assume a role in your AWS account. Require a specific external ID to reduce the risk of the confused deputy problem.

```hcl
resource "aws_iam_role" "vendor_role" {
  name = "vendor-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"

      Principal = {
        AWS = "arn:aws:iam::111122223333:root"
      }

      Action = "sts:AssumeRole"

      Condition = {
        StringEquals = {
          "sts:ExternalId" = "company-unique-external-id"
        }
      }
    }]
  })
}
```

Here:
- `Principal` identifies the trusted AWS account.
- `Action` allows the `sts:AssumeRole` operation.
- `Condition` requires the caller to supply the matching external ID.

Use a real, unique external ID agreed with the vendor; the example value is a placeholder.

### B. Conditions in a permissions policy

**Production use case:** A cleanup Lambda can delete temporary files, but only from a specific S3 prefix.

```hcl
resource "aws_iam_role_policy" "cleanup_policy" {
  name = "cleanup-temp-files"
  role = aws_iam_role.cleanup_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"

      Action = [
        "s3:DeleteObject"
      ]

      Resource = "arn:aws:s3:::my-app-bucket/temp/*"

      Condition = {
        StringEquals = {
          "aws:ResourceAccount" = "123456789012"
        }
      }
    }]
  })
}
```

Here:
- The role's trust policy decides which service or identity can assume the role.
- This permissions policy restricts deletion to objects under `temp/` in the named bucket.
- The condition further requires the resource account to match.

Replace the account ID and bucket name with your actual values.

### C. Conditions in both policies

**Production use case:** A vendor assumes a role to manage a narrowly scoped set of resources.

1. Trust policy: only the approved vendor principal, with the correct external ID, can assume the role.
2. Permissions policy: the role can perform only the approved actions on specified resources, potentially with additional conditions.

The trust condition does not replace the permissions policy, and the permissions condition does not replace the trust policy.

## 7. Common IAM condition keys and operators

| Condition | Common use case |
|---|---|
| `aws:SourceIp` | Restrict requests to specified IP addresses or CIDR ranges |
| `aws:MultiFactorAuthPresent` | Require MFA for supported requests |
| `aws:RequestedRegion` | Restrict supported actions to specified AWS Regions |
| `aws:ResourceTag/Environment` | Restrict access based on a resource's tag |
| `aws:PrincipalArn` | Match the ARN of the calling principal, where the key is supported |
| `sts:ExternalId` | External ID requirement for supported role-assumption scenarios |
| `StringEquals` | Require an exact string match |
| `StringLike` | Match strings using supported wildcard patterns |
| `ArnEquals` | Require an ARN match |
| `IpAddress` | Match an IP address against an IP range |
| `Bool` | Check a Boolean-valued condition key |
| `DateGreaterThan` / `DateLessThan` | Restrict access to a time window when supported |

The available condition keys depend on the AWS service and API action. Verify the relevant AWS documentation before relying on a condition in production.

### Example: require MFA in a permissions policy

```json
{
  "Effect": "Allow",
  "Action": "ec2:StopInstances",
  "Resource": "*",
  "Condition": {
    "Bool": {
      "aws:MultiFactorAuthPresent": "true"
    }
  }
}
```

This illustrates an MFA condition for supported requests. It does not automatically apply to every kind of role session or AWS service request.

### Example: restrict by AWS Region

```json
{
  "Effect": "Deny",
  "Action": "ec2:*",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {
      "aws:RequestedRegion": [
        "eu-west-1"
      ]
    }
  }
}
```

This illustrates denying matching EC2 actions when the requested Region is not `eu-west-1`. Carefully assess exceptions and service-specific behavior before deploying a broad explicit deny.

### Example: restrict by resource tag

```json
{
  "Effect": "Allow",
  "Action": "ec2:StopInstances",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "aws:ResourceTag/Environment": "dev"
    }
  }
}
```

This illustrates allowing the action only when the relevant resource has the `Environment=dev` tag, where the action supports that resource-level authorization and condition key.

## 8. Inline policy vs managed policy

### Inline policy

An inline policy is defined directly for one IAM user, group, or role. It has a one-to-one relationship with that identity.

Terraform example:

```hcl
resource "aws_iam_role_policy" "cleanup_policy" {
  name = "cleanup-temp-files"
  role = aws_iam_role.cleanup_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "s3:DeleteObject"
      Resource = "arn:aws:s3:::my-app-bucket/temp/*"
    }]
  })
}
```

**Production use case:** A cleanup Lambda needs a small, role-specific permission to delete temporary files from one S3 prefix.

### Managed policy

A managed policy is a separate policy resource that can be attached to multiple identities.

Create a customer-managed policy:

```hcl
resource "aws_iam_policy" "s3_read_policy" {
  name = "s3-read-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:ListBucket"
      ]
      Resource = [
        "arn:aws:s3:::my-app-bucket",
        "arn:aws:s3:::my-app-bucket/*"
      ]
    }]
  })
}
```

Attach it to a role:

```hcl
resource "aws_iam_role_policy_attachment" "attach_s3_read" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.s3_read_policy.arn
}
```

**Production use case:** Several application roles need the same approved S3 read permissions. A customer-managed policy allows the permissions to be maintained in one place.

### AWS-managed policy

AWS creates and maintains the policy.

```hcl
resource "aws_iam_role_policy_attachment" "attach_aws_managed" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}
```

This attaches an AWS-managed policy; it is **not an inline policy**. AWS-managed policies can grant broader permissions than an application needs, so review the policy before using it in production.

## 9. Terraform IAM resources

| Terraform resource | Purpose |
|---|---|
| `aws_iam_role` | Creates an IAM role, including its trust policy |
| `aws_iam_role_policy` | Creates an inline policy for a role |
| `aws_iam_policy` | Creates a customer-managed policy |
| `aws_iam_role_policy_attachment` | Attaches a managed policy to a role |
| `aws_iam_instance_profile` | Makes a role available for an EC2 instance |

Example instance profile:

```hcl
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2-instance-profile"
  role = aws_iam_role.ec2_role.name
}
```

An EC2 instance uses the instance profile to obtain the role's temporary credentials.

## 10. What is an ARN?

ARN means **Amazon Resource Name**. It identifies an AWS resource.

Example:

```text
arn:aws:iam::123456789012:policy/s3-read-policy
```

General structure:

```text
arn:partition:service:region:account-id:resource
```

The exact fields vary by resource type. IAM ARNs commonly have an empty Region field.

Terraform can refer to a generated ARN instead of hardcoding it:

```hcl
policy_arn = aws_iam_policy.s3_read_policy.arn
```

Here, `aws_iam_policy.s3_read_policy` is the Terraform resource reference and `.arn` is its exported ARN attribute.

## 11. EC2 accessing S3: production flow

1. Create an IAM role.
2. Configure the trust policy to trust EC2.
3. Attach a permissions policy granting the required S3 actions on the required resources.
4. Create an instance profile for the role.
5. Attach the instance profile to the EC2 instance.
6. The application on EC2 obtains temporary credentials through the AWS SDK or CLI credential provider chain.
7. AWS evaluates the request against applicable policies and authorization controls.

**Best practice:** Grant least privilege. Avoid storing long-lived AWS access keys on EC2 instances.

## 12. Key rules to remember

- Trust policy = **who can assume the role**.
- Permissions policy = **what the role can do**.
- `Principal` identifies the trusted entity in a trust policy.
- `Action` specifies the API operations.
- `Resource` specifies the resources an action applies to.
- `Condition` adds circumstances or constraints to a policy statement.
- Conditions can appear in both trust policies and permissions policies.
- Inline policies are attached directly to one identity.
- Managed policies are separate policies that can be reused.
- `aws_iam_role_policy` creates an inline role policy.
- `aws_iam_policy` creates a customer-managed policy.
- `aws_iam_role_policy_attachment` attaches a managed policy.
- An AWS-managed policy ARN, such as `AmazonS3ReadOnlyAccess`, identifies a policy maintained by AWS.
- A trust policy alone does not grant S3, EC2, or other service permissions.
- Explicit `Deny` overrides an applicable `Allow`.
- A policy `Allow` does not guarantee access: other authorization controls, such as SCPs, permissions boundaries, resource policies, and service-specific rules, can affect the result.



### Final Memory Trick

**Role = Identity**

**Trust policy = Who can assume the role?**

**Permissions policy = What can the role do?**

**Principal = Who?**

**Action = What operation?**

**Resource = Which resource?**

**Condition = Under what extra requirements?**

**Inline policy = Policy associated with one identity**

**Managed policy = Separate reusable policy**

**ARN = AWS resource identifier**
