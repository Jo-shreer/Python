====================================================
TERRAFORM – BASICS + VARIABLES
====================================================

WHAT IS TERRAFORM?
------------------
Terraform is an Infrastructure as Code (IaC) tool.

It allows us to create, modify, and manage infrastructure
using configuration files instead of manually creating
resources from the AWS Console.

Example:
Instead of manually creating an AWS S3 bucket from the
console, we can define it in Terraform:

resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-app-bucket"
}

Terraform then creates the bucket in AWS.

Terraform is developed by HashiCorp.


WHY USE TERRAFORM?
------------------
1. Infrastructure can be created using code.
2. Infrastructure changes can be version controlled using Git.
3. Same infrastructure can be recreated easily.
4. Reduces manual configuration.
5. Supports multiple cloud providers.
6. Provides a plan before making changes.


BASIC TERRAFORM WORKFLOW
------------------------

terraform init
    ↓
terraform plan
    ↓
terraform apply
    ↓
Infrastructure created


terraform init
--------------
Initializes the Terraform project and downloads required
providers/modules.


terraform plan
--------------
Shows what Terraform is going to create, modify, or delete.

It does NOT make changes.


terraform apply
---------------
Actually creates/modifies/deletes the infrastructure.


terraform destroy
-----------------
Deletes infrastructure managed by Terraform.


====================================================
TERRAFORM VARIABLES
====================================================

Variables allow us to make Terraform configuration
dynamic and reusable.

Instead of hardcoding:

resource "aws_instance" "server" {
  instance_type = "t3.micro"
}

We can use:

resource "aws_instance" "server" {
  instance_type = var.instance_type
}


VARIABLE DEFINITION
-------------------

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

Then use:

var.instance_type


====================================================
1. STRING
====================================================

String is text.

Example:

variable "environment" {
  type    = string
  default = "dev"
}

Use:

var.environment

Value:

"dev"


Another example:

variable "region" {
  type    = string
  default = "us-east-1"
}


====================================================
2. NUMBER
====================================================

Number represents a numeric value.

Example:

variable "instance_count" {
  type    = number
  default = 3
}

Use:

var.instance_count

Value:

3


Another example:

variable "port" {
  type    = number
  default = 8080
}


====================================================
3. BOOL / BOOLEAN
====================================================

Boolean has only two values:

true
false

Example:

variable "enable_monitoring" {
  type    = bool
  default = true
}

Use:

var.enable_monitoring


Example:

variable "create_bucket" {
  type    = bool
  default = false
}


====================================================
4. LIST
====================================================

List stores multiple values in an ordered collection.

Example:

variable "availability_zones" {
  type = list(string)

  default = [
    "us-east-1a",
    "us-east-1b",
    "us-east-1c"
  ]
}

Use:

var.availability_zones


Access individual values using index:

var.availability_zones[0]

Result:

"us-east-1a"


Important:
List is ORDERED.

Example:

[
  "A",
  "B",
  "C"
]

Index:

0 → A
1 → B
2 → C


====================================================
5. MAP
====================================================

Map stores KEY → VALUE pairs.

Think of it like a Python dictionary.

Example:

variable "instance_types" {
  type = map(string)

  default = {
    dev  = "t3.micro"
    test = "t3.small"
    prod = "t3.medium"
  }
}

Use:

var.instance_types["dev"]

Result:

"t3.micro"


Another example:

variable "tags" {
  type = map(string)

  default = {
    Environment = "dev"
    Team        = "backend"
    Project     = "payment"
  }
}


====================================================
LIST vs MAP
====================================================

LIST:

[
  "dev",
  "test",
  "prod"
]

Access using INDEX:

var.environments[0]

Result:

"dev"


MAP:

{
  dev  = "t3.micro"
  prod = "t3.medium"
}

Access using KEY:

var.instance_types["dev"]

Result:

"t3.micro"


Easy way to remember:

LIST = INDEX

MAP = KEY → VALUE


====================================================
VARIABLE TYPES CHEAT SHEET
====================================================

STRING
------
Text

type = string

Example:
"dev"


NUMBER
------
Number

type = number

Example:
3


BOOL
----
True / False

type = bool

Example:
true


LIST
----
Multiple ordered values

type = list(string)

Example:
["dev", "test", "prod"]


MAP
---
Key-value pairs

type = map(string)

Example:
{
  dev  = "t3.micro"
  prod = "t3.medium"
}


====================================================
EXAMPLE: COMPLETE VARIABLES
====================================================

variable "environment" {
  type    = string
  default = "dev"
}

variable "instance_count" {
  type    = number
  default = 2
}

variable "enable_monitoring" {
  type    = bool
  default = true
}

variable "availability_zones" {
  type = list(string)

  default = [
    "us-east-1a",
    "us-east-1b"
  ]
}

variable "instance_types" {
  type = map(string)

  default = {
    dev  = "t3.micro"
    prod = "t3.medium"
  }
}


USE VARIABLES
-------------

var.environment

var.instance_count

var.enable_monitoring

var.availability_zones

var.instance_types["dev"]


====================================================
INTERVIEW ONE-LINERS
====================================================

Terraform:
"Terraform is an Infrastructure as Code tool used to
provision and manage infrastructure using configuration
files."

Variable:
"A Terraform variable is used to make configuration
dynamic and reusable."

String:
"Stores text."

Number:
"Stores numeric values."

Bool:
"Stores true or false."

List:
"Stores multiple ordered values and uses indexes."

Map:
"Stores key-value pairs and uses keys to access values."


MEMORY TRICK
------------

STRING → Text

NUMBER → Number

BOOL → true / false

LIST → Ordered values → INDEX

MAP → Key/value → KEY
====================================================
