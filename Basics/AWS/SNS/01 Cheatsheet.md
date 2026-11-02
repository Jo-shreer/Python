# AWS SNS (Simple Notification Service) – Complete Cheatsheet

## 1. What is SNS?

Amazon SNS is a fully managed pub/sub (publish-subscribe) messaging service.

It allows one application to publish a message to an SNS Topic. SNS then delivers that message to all subscribed endpoints.

### Example

Imagine an e-commerce application.

When a customer places an order, several things need to happen:

- Send an order confirmation email.
- Update inventory.
- Notify the shipping application.
- Send an event to an analytics system.

Without SNS, the order application would need to communicate with each system separately.

With SNS:

1. The order application publishes an `OrderCreated` event to SNS.
2. SNS distributes the event to its subscribers.
3. Each subscriber receives and processes the event independently.

**SNS acts as a central message distributor.**

## 2. SNS architecture

```text
                  Order Application
                         |
                         | Publish message
                         v
                    SNS Topic
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
       SQS Queue       Lambda         Email
          |              |              |
          v              v              v
    Inventory App   Notification     Customer
                       Service
```

Important components:

| Component | Meaning |
|---|---|
| Publisher | Application that sends messages |
| Topic | Logical communication channel |
| Subscriber | Endpoint receiving messages |
| Subscription | Connection between topic and endpoint |
| Message | Data published to the topic |
| Filter policy | Controls which messages a subscriber receives |
| Delivery policy | Controls retry behavior for supported endpoints |
| DLQ | Stores messages that could not be delivered successfully |

## 3. SNS topic types

SNS supports two main topic types.

### A. Standard Topic

Characteristics:

- High throughput.
- Supports many subscribers.
- At-least-once delivery.
- Messages can occasionally arrive more than once.
- Message ordering is not guaranteed.

Use cases:

- Application notifications.
- Order events.
- Monitoring alerts.
- Event distribution.

### B. FIFO Topic

FIFO means First-In, First-Out.

Characteristics:

- Preserves message ordering within a message group.
- Supports deduplication.
- Supports FIFO SQS queues as subscribers.
- Requires a message group ID.
- Supports limited throughput compared with Standard topics.

Use cases:

- Financial transaction events.
- Order processing where ordering matters.
- Sequential business workflows.

Important:

A FIFO SNS topic requires FIFO SQS queues for SQS subscriptions. You cannot subscribe a Standard SQS queue to a FIFO SNS topic.

## 4. SNS vs SQS

This is one of the most important AWS interview topics.

| Feature | SNS | SQS |
|---|---|---|
| Purpose | Message distribution | Message queuing |
| Communication | Pub/Sub | Queue-based |
| Message delivery | Push to subscribers | Consumer polls queue |
| Multiple consumers | Yes, through subscriptions | Consumers compete for messages |
| Message storage | Not a durable message backlog | Stores messages until consumed or expired |
| Ordering | Standard: no guarantee; FIFO: supported | Standard: best-effort; FIFO: supported |
| Retry | Delivery retries for supported endpoints | Consumer retries by not deleting message |
| DLQ | Subscription delivery failures | Messages repeatedly failing processing |
| Typical use | Fanout | Asynchronous processing |

### Important difference

Suppose one order event needs to be processed by three applications.

With SNS alone:

```text
             SNS Topic
           /     |      \
       Lambda   Email   HTTP
```

With SQS alone:

```text
             SQS Queue
                 |
          Consumer Applications
```

With SNS + SQS:

```text
                 SNS Topic
                /    |    \
               /     |     \
              v      v      v
           SQS-1   SQS-2   SQS-3
             |       |       |
             v       v       v
         Inventory Shipping Analytics
```

Each application gets its own copy of the event.

This is called the **SNS fanout pattern**.

## 5. How SNS works step by step

1. Create an SNS Topic.
2. Create subscribers.
3. Subscribe endpoints to the topic.
4. Publisher sends a message to the topic.
5. SNS identifies the topic's subscriptions.
6. SNS applies subscription filter policies, if configured.
7. SNS attempts to deliver the message to eligible subscribers.
8. If delivery fails, SNS retries according to the endpoint's delivery policy.
9. If configured, failed deliveries can eventually go to a subscription DLQ.

Example:

```bash
aws sns create-topic \
  --name order-events
```

Publish a message:

```bash
aws sns publish \
  --topic-arn arn:aws:sns:eu-west-1:123456789012:order-events \
  --message "New order created"
```

## 6. SNS subscribers

SNS supports several subscription endpoint types.

| Protocol | Subscriber |
|---|---|
| SQS | SQS queue |
| Lambda | Lambda function |
| Email | Email address |
| Email-JSON | Email in JSON format |
| HTTPS | Web application endpoint |
| HTTP | Web application endpoint |
| SMS | Mobile phone number |
| Application | Mobile push notifications |

For production event-driven applications, SNS + SQS is a common architecture.

Email subscriptions generally require confirmation before messages are delivered.

## 7. SNS message filtering

Filtering lets each subscriber receive only relevant messages.

Example: Your SNS topic receives different order events.

```json
{
  "eventType": "OrderCreated",
  "department": "Electronics",
  "orderId": "ORD-1001"
}
```

Suppose you have two subscribers:

- Inventory queue.
- Shipping queue.

You can configure filters:

Inventory subscription:

```json
{
  "department": ["Electronics", "Furniture"]
}
```

Shipping subscription:

```json
{
  "eventType": ["OrderCreated", "OrderShipped"]
}
```

SNS evaluates the message attributes against each subscription's filter policy.

Important:

By default, filter policies evaluate message attributes. You can also configure filtering against the message body.

For message-attribute filtering, the publisher must provide the relevant message attributes.

## 8. SNS delivery retries and DLQ

SNS attempts to deliver messages to subscribers.

Delivery behavior depends on the endpoint protocol.

For supported delivery protocols, SNS retries failed deliveries according to the configured delivery policy.

For example:

```text
             SNS Topic
                 |
                 v
             Subscriber
                 |
          Delivery Failure
                 |
              Retries
                 |
          +------+------+
          |             |
       Success       Failure
                        |
                        v
                      DLQ
```

### What is an SNS DLQ?

A Dead Letter Queue stores messages that SNS could not successfully deliver to a subscription after its retry policy is exhausted.

Important distinction:

- SNS DLQ handles delivery failures from SNS to the subscriber.
- SQS DLQ handles messages that a consumer repeatedly fails to process.

These solve different problems.

## 9. SNS security

### A. IAM permissions

IAM controls which users and applications can:

- Create topics.
- Publish messages.
- Subscribe endpoints.
- Unsubscribe endpoints.
- Delete topics.
- Modify topic policies.

Example IAM permission for publishing:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:eu-west-1:123456789012:order-events"
    }
  ]
}
```

Follow least privilege: allow only the required SNS actions on the required topic.

### B. SNS topic policy

A topic policy controls access to the topic.

For example, you can allow a specific AWS account or service to publish messages.

### C. Encryption

SNS supports encryption at rest using AWS KMS.

Example Terraform setting:

```hcl
kms_master_key_id = "alias/aws/sns"
```

For customer-managed KMS keys, configure the KMS key policy and IAM permissions appropriately.

### D. HTTPS delivery

Use HTTPS endpoints instead of HTTP for web subscribers.

You can also enforce secure transport through a topic policy.

## 10. SNS VPC Endpoint

SNS supports an Interface VPC Endpoint.

It allows resources inside a VPC to communicate with SNS privately without requiring internet or NAT access for that SNS traffic.

Example:

```text
                 AWS SNS
                    |
                    |
             Interface Endpoint
                    |
                    |
             Private Subnet
                    |
                    v
                   EC2
```

Endpoint service name:

```text
com.amazonaws.eu-west-1.sns
```

Replace the region with your AWS region.

Important configuration:

- Select the SNS Interface Endpoint.
- Select your VPC.
- Select private subnets.
- Enable Private DNS.
- Attach an endpoint security group.
- Allow inbound TCP 443 from the application security group.
- Ensure the application can make outbound TCP 443 connections.

Unlike an S3 Gateway Endpoint, SNS uses an Interface Endpoint.

## 11. SNS integration with other AWS services

| Integration | Purpose |
|---|---|
| SNS + SQS | Fanout to independent queues |
| SNS + Lambda | Trigger serverless functions |
| SNS + Email | Send notifications |
| SNS + CloudWatch | Send alarm notifications |
| SNS + EventBridge | Event-driven integrations |
| SNS + HTTP/HTTPS | Notify external applications |

### SNS + CloudWatch example

```text
CloudWatch Alarm
       |
       v
    SNS Topic
       |
       v
 Email Subscription
       |
       v
 Operations Team
```

When an alarm enters its configured alarm state, CloudWatch can publish a notification to SNS.

## 12. SNS monitoring

Use CloudWatch metrics to monitor SNS.

Important metrics:

| Metric | Meaning |
|---|---|
| NumberOfMessagesPublished | Messages published |
| NumberOfNotificationsDelivered | Messages successfully delivered |
| NumberOfNotificationsFailed | Failed deliveries |
| NumberOfNotificationsFilteredOut | Messages excluded by filters |
| NumberOfNotificationsRedrivenToDlq | Messages sent to subscription DLQs |

You can configure CloudWatch alarms for delivery failures and other relevant metrics.

## 13. SNS pricing

SNS pricing depends on:

- Number of published messages.
- Number of delivered messages.
- Delivery protocol.
- Region.
- Optional features such as FIFO topics and SMS.

SMS delivery has separate pricing and varies by destination.

Remember that SNS-to-SQS fanout creates a separate delivery to each subscribed queue. SQS requests and storage can also incur charges.

Check AWS pricing for your region before estimating production costs.

---

# 14. Production Terraform Example – SNS + SQS Fanout

Let's create a practical architecture.

### Architecture

An application publishes order events to SNS.

SNS distributes each event to an SQS queue.

The inventory application consumes messages from that queue.

A separate DLQ captures messages that SNS cannot deliver to the SQS subscription.

```text
              EC2 Application
                    |
                    | Publish
                    v
                SNS Topic
                    |
                    | Subscribe
                    v
                SQS Queue
                    |
                    v
             Inventory Worker

          SNS Delivery Failure
                    |
                    v
               SNS DLQ
```

### Step 1: Define variables

```hcl
variable "aws_region" {
  default = "eu-west-1"
}

variable "environment" {
  default = "prod"
}
```

### Step 2: Configure AWS provider

```hcl
provider "aws" {
  region = var.aws_region
}
```

### Step 3: Create SNS topic

```hcl
resource "aws_sns_topic" "order_events" {
  name = "${var.environment}-order-events"

  kms_master_key_id = "alias/aws/sns"

  tags = {
    Environment = var.environment
    Application = "orders"
  }
}
```

This creates an encrypted SNS topic.

### Step 4: Create SQS queue

```hcl
resource "aws_sqs_queue" "inventory_queue" {
  name = "${var.environment}-inventory-queue"

  visibility_timeout_seconds = 120

  message_retention_seconds = 345600

  receive_wait_time_seconds = 20

  sqs_managed_sse_enabled = true

  tags = {
    Environment = var.environment
    Application = "inventory"
  }
}
```

Configuration:

- Visibility timeout: 120 seconds.
- Message retention: 4 days.
- Long polling: 20 seconds.
- Encryption: SQS-managed encryption.

### Step 5: Create SNS delivery DLQ

```hcl
resource "aws_sqs_queue" "sns_delivery_dlq" {
  name = "${var.environment}-sns-delivery-dlq"

  message_retention_seconds = 1209600

  sqs_managed_sse_enabled = true

  tags = {
    Environment = var.environment
    Purpose     = "sns-delivery-failures"
  }
}
```

This queue stores messages SNS could not deliver to the inventory queue after exhausting its delivery retries.

### Step 6: Allow SNS to send messages to SQS

SNS needs permission to send messages to the SQS queue.

```hcl
data "aws_iam_policy_document" "inventory_queue_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    actions = [
      "sqs:SendMessage"
    ]

    resources = [
      aws_sqs_queue.inventory_queue.arn
    ]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"

      values = [
        aws_sns_topic.order_events.arn
      ]
    }
  }
}

resource "aws_sqs_queue_policy" "inventory_queue_policy" {
  queue_url = aws_sqs_queue.inventory_queue.id

  policy = data.aws_iam_policy_document.inventory_queue_policy.json
}
```

Important:

The `aws:SourceArn` condition ensures that only the specified SNS topic can send messages to this queue through this permission.

### Step 7: Subscribe SQS to SNS

```hcl
resource "aws_sns_topic_subscription" "inventory_subscription" {
  topic_arn = aws_sns_topic.order_events.arn

  protocol = "sqs"

  endpoint = aws_sqs_queue.inventory_queue.arn

  raw_message_delivery = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.sns_delivery_dlq.arn
  })

  depends_on = [
    aws_sqs_queue_policy.inventory_queue_policy
  ]
}
```

Important settings:

- `protocol = "sqs"` connects the SQS queue to SNS.
- `endpoint` specifies the destination queue.
- `raw_message_delivery = true` delivers the original message without the SNS JSON envelope.
- `redrive_policy` configures the SNS subscription DLQ.

### Step 8: Allow SNS to send messages to the delivery DLQ

```hcl
data "aws_iam_policy_document" "sns_dlq_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    actions = [
      "sqs:SendMessage"
    ]

    resources = [
      aws_sqs_queue.sns_delivery_dlq.arn
    ]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"

      values = [
        aws_sns_topic.order_events.arn
      ]
    }
  }
}

resource "aws_sqs_queue_policy" "sns_dlq_policy" {
  queue_url = aws_sqs_queue.sns_delivery_dlq.id

  policy = data.aws_iam_policy_document.sns_dlq_policy.json
}
```

This grants SNS permission to write failed subscription deliveries into the DLQ.

### Step 9: Create SNS topic policy to enforce HTTPS

```hcl
data "aws_iam_policy_document" "sns_topic_policy" {
  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "SNS:Publish",
      "SNS:Subscribe"
    ]

    resources = [
      aws_sns_topic.order_events.arn
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"

      values = ["false"]
    }
  }
}

resource "aws_sns_topic_policy" "order_events_policy" {
  arn = aws_sns_topic.order_events.arn

  policy = data.aws_iam_policy_document.sns_topic_policy.json
}
```

This denies the specified actions when the request does not use secure transport.

### Step 10: Create CloudWatch alarm for the SNS DLQ

```hcl
resource "aws_cloudwatch_metric_alarm" "sns_dlq_alarm" {
  alarm_name = "${var.environment}-sns-delivery-dlq-not-empty"

  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 1

  metric_name = "ApproximateNumberOfMessagesVisible"

  namespace = "AWS/SQS"

  period = 60

  statistic = "Average"

  threshold = 0

  dimensions = {
    QueueName = aws_sqs_queue.sns_delivery_dlq.name
  }

  alarm_description = "SNS delivery failures detected in DLQ"
}
```

This alarm detects messages accumulating in the SNS delivery DLQ.

For actual notifications, configure an SNS topic as the CloudWatch alarm's `alarm_actions` destination.

### Step 11: Create outputs

```hcl
output "sns_topic_arn" {
  value = aws_sns_topic.order_events.arn
}

output "inventory_queue_url" {
  value = aws_sqs_queue.inventory_queue.url
}

output "inventory_queue_arn" {
  value = aws_sqs_queue.inventory_queue.arn

  sensitive = true
}

output "sns_delivery_dlq_url" {
  value = aws_sqs_queue.sns_delivery_dlq.url
}
```

### Step 12: Deploy Terraform

```bash
terraform init
```

```bash
terraform validate
```

```bash
terraform plan
```

```bash
terraform apply
```

### Step 13: Publish a test message

```bash
aws sns publish \
  --topic-arn <SNS_TOPIC_ARN> \
  --message '{"orderId":"ORD-1001","eventType":"OrderCreated"}' \
  --region eu-west-1
```

### Step 14: Read the message from SQS

```bash
aws sqs receive-message \
  --queue-url <SQS_QUEUE_URL> \
  --max-number-of-messages 10 \
  --wait-time-seconds 20 \
  --region eu-west-1
```

You should see the published order event in the SQS queue.

After successful processing, the consumer must delete the message:

```bash
aws sqs delete-message \
  --queue-url <SQS_QUEUE_URL> \
  --receipt-handle <RECEIPT_HANDLE> \
  --region eu-west-1
```

The receipt handle comes from the `receive-message` response.

---

# 15. Important production considerations

1. **Idempotency:** SNS Standard delivery can result in duplicate messages. Consumers should handle duplicate events safely.

2. **Message ordering:** Use FIFO topics and FIFO queues when ordering is required.

3. **Filtering:** Use subscription filter policies to avoid sending irrelevant messages to subscribers.

4. **DLQ monitoring:** Monitor SNS subscription DLQs and SQS consumer DLQs separately.

5. **IAM:** Restrict publishing and subscription permissions to the required applications and topics.

6. **Encryption:** Use KMS where required and configure key permissions correctly.

7. **Retries:** Understand the delivery retry policy for each subscription protocol.

8. **Fanout:** Use one SQS queue per independent application when each application needs its own copy of every event.

9. **Message size:** SNS supports messages up to 256 KB by default. Large payloads should generally be stored in S3, with an S3 object reference published in the message.

10. **Monitoring:** Monitor published, delivered, failed, filtered and redriven messages.

---

# 16. Common SNS interview questions

**Q1. What is SNS?**

SNS is a managed pub/sub messaging service used to distribute messages to multiple subscribers.

**Q2. What is an SNS Topic?**

A logical channel where publishers send messages and subscribers receive them.

**Q3. What is the difference between SNS and SQS?**

SNS pushes messages to subscribers. SQS stores messages until consumers retrieve and process them.

**Q4. What is SNS fanout?**

One SNS message is delivered to multiple subscribers, commonly multiple SQS queues.

**Q5. Can SNS send messages to SQS?**

Yes. An SQS queue can subscribe to an SNS topic.

**Q6. Why do we need an SQS queue policy for SNS?**

It grants SNS permission to send messages to the queue.

**Q7. What is an SNS filter policy?**

It filters messages so a subscription receives only messages matching configured attributes or message-body conditions.

**Q8. What is the difference between SNS DLQ and SQS DLQ?**

SNS DLQ stores failed deliveries from SNS to subscribers. SQS DLQ stores messages that consumers repeatedly fail to process.

**Q9. What is the difference between Standard and FIFO SNS topics?**

Standard topics prioritize throughput and support at-least-once delivery without ordering guarantees. FIFO topics support ordering within message groups and deduplication.

**Q10. Can SNS invoke Lambda?**

Yes. Lambda can subscribe directly to an SNS topic.

**Q11. Can SNS send email notifications?**

Yes. Email addresses can subscribe to SNS topics, subject to subscription confirmation.

**Q12. How can EC2 privately access SNS?**

Use an SNS Interface VPC Endpoint with Private DNS and suitable security group rules.

**Q13. What happens if a subscriber is unavailable?**

SNS retries delivery according to the applicable endpoint delivery policy. A configured subscription DLQ can capture messages that exhaust retries.

**Q14. Does SNS guarantee exactly-once delivery?**

Standard SNS does not. FIFO SNS supports deduplication, but consumers should still be designed to handle duplicate processing safely.

---

# 17. Quick revision summary

| AWS concept | Remember |
|---|---|
| SNS | Publish-subscribe messaging |
| Topic | Message distribution channel |
| Publisher | Sends messages |
| Subscriber | Receives messages |
| Subscription | Connects subscriber to topic |
| Fanout | One message to multiple subscribers |
| Filter policy | Controls which messages a subscriber receives |
| Standard topic | High throughput, no ordering guarantee |
| FIFO topic | Ordering and deduplication |
| SNS DLQ | Failed subscriber deliveries |
| SNS + SQS | Independent copies for multiple consumers |
| SNS VPC Endpoint | Private connectivity through Interface Endpoint |
| KMS | Encryption at rest |
| CloudWatch | Monitoring and alarms |

**Most important architecture to remember:**

```text
             Application
                  |
                  v
               SNS Topic
              /    |    \
             v     v     v
          SQS-1  SQS-2  SQS-3
            |      |      |
            v      v      v
        App-1   App-2   App-3
```

SNS distributes the event. Each SQS queue stores its own copy. Each application processes its messages independently.
