# Apache Airflow & AWS MWAA — Complete Terraform and Production Cheatsheet

**Topics covered:** Airflow architecture, all important DAG and task parameters, operators, sensors, XCom, scheduling, TaskFlow API, Terraform resource parameters, IAM, networking, production DAG, MWAA deployment, cost, security, policy as code and troubleshooting.

**AWS region example:** `eu-west-1` (Ireland).

**Version note:** The DAG code below uses the Airflow 2.x-compatible API style and is intended for an MWAA environment running a compatible Airflow 2.x release. Always select an Airflow version currently supported by MWAA in your region and use compatible Amazon provider packages. Airflow 3 has a newer public Task SDK interface.

---

# PART 1 — UNDERSTAND APACHE AIRFLOW

## 1. What is Apache Airflow?

Apache Airflow is an open-source workflow orchestration platform.

It helps you schedule, manage, monitor and coordinate tasks that need to run in a particular order.

Example: a daily data pipeline.

```text
              Daily Schedule
                     |
                     v
              Extract Data
                     |
                     v
              Check Data
                     |
                     v
              Transform Data
                     |
                     v
              Load Data
                     |
                     v
              Data Quality
                     |
                     v
              Send Notification
```

Airflow decides:

- When a workflow should run.
- Which task should run first.
- Which tasks can run simultaneously.
- What happens if a task fails.
- How many times a task should retry.
- Whether tasks should wait for external events.
- How to monitor execution.

**Important:** Airflow is an orchestrator, not a data-processing engine. For large transformations, use services such as AWS Glue, EMR, ECS, Spark or a data warehouse. Airflow coordinates these services.

## 2. Airflow architecture

```text
                   Developer
                       |
                       v
                  DAG Python Files
                       |
                       v
                 DAG Processor
                       |
                       v
                  DAG Metadata
                       |
                       v
                   Scheduler
                       |
                       v
                    Executor
                       |
              +--------+--------+
              |                 |
              v                 v
           Worker 1          Worker 2
              |                 |
              v                 v
          Run Task A        Run Task B
              |                 |
              +--------+--------+
                       |
                       v
                Metadata Database
                       |
                       v
                  Airflow UI
```

### Airflow components

| Component | Detailed explanation |
|---|---|
| DAG | Python definition of a workflow, its tasks and dependencies |
| DAG Processor | Parses DAG files and discovers workflows |
| Scheduler | Determines which task instances are ready to run |
| Executor | Controls how tasks are dispatched and executed |
| Worker | Executes the actual task code |
| Triggerer | Handles asynchronous deferred tasks |
| Metadata database | Stores DAG runs, task states, scheduling metadata and other operational information |
| Webserver / UI | Provides the interface for viewing and managing workflows |
| XCom | Passes small pieces of data between tasks |
| Log backend | Stores task execution logs |
| Provider packages | Add integrations for AWS, databases, APIs and other platforms |

### Airflow executors

| Executor | Explanation | Typical use |
|---|---|---|
| SequentialExecutor | Runs tasks sequentially | Basic development |
| LocalExecutor | Runs tasks as local processes | Small self-managed deployment |
| CeleryExecutor | Distributes tasks to worker processes | Distributed deployments |
| KubernetesExecutor | Runs tasks in Kubernetes pods | Kubernetes-based deployments |
| DebugExecutor | Helps with debugging | Development and testing |

MWAA manages the execution infrastructure for you. You do not normally configure a self-managed Celery cluster for MWAA.

---

# PART 2 — AIRFLOW TERMINOLOGY

## 3. Important Airflow concepts

| Term | Explanation | Example |
|---|---|---|
| DAG | Complete workflow definition | Daily sales ETL |
| DAG run | One execution of a DAG | Sales pipeline for 4 November |
| Task | One unit of work | Validate file |
| Task instance | Execution of a task for a particular DAG run | Validate the 4 November file |
| Operator | Class that implements a task | `PythonOperator` |
| Sensor | Waits for an external condition | Wait for an S3 file |
| Hook | Connects to an external service | `S3Hook` |
| XCom | Transfers small task results | S3 key or record count |
| Connection | Stores connection information | AWS connection |
| Variable | Stores Airflow configuration | Bucket name |
| Pool | Limits concurrency for a set of tasks | Maximum 5 database tasks |
| TaskGroup | Groups related tasks visually | Ingestion tasks |
| Executor | Controls task execution | CeleryExecutor |
| Triggerer | Handles deferred tasks | Deferrable sensor |
| Provider | Integration package | Amazon provider |
| Timetable | Controls scheduling intervals | Business-day schedule |
| Data interval | Period of data a scheduled run represents | Previous day's data |

---

# PART 3 — DAG PARAMETERS

## 4. What is a DAG?

DAG means Directed Acyclic Graph.

It defines:

- What tasks exist.
- Which task depends on another.
- When the workflow should run.
- What happens when tasks succeed or fail.

Example:

```python
from airflow import DAG
from airflow.operators.empty import EmptyOperator
import pendulum

with DAG(
    dag_id="daily_sales_etl",
    description="Daily sales ETL pipeline",
    schedule="0 2 * * *",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    max_active_tasks=10,
    tags=["sales", "etl", "production"],
) as dag:

    start = EmptyOperator(task_id="start")
    finish = EmptyOperator(task_id="finish")

    start >> finish
```

## 5. Complete list of important DAG arguments

| Parameter | Explanation | Example |
|---|---|---|
| `dag_id` | Unique DAG name. Used to identify the workflow. | `"daily_sales_etl"` |
| `description` | Human-readable explanation of the DAG. | `"Daily sales pipeline"` |
| `schedule` | Defines when the DAG runs. | `"0 2 * * *"` |
| `start_date` | First scheduling date. Use a fixed timezone-aware date. | `pendulum.datetime(2025,1,1,tz="UTC")` |
| `end_date` | Optional final scheduling date. | `pendulum.datetime(2026,12,31,tz="UTC")` |
| `catchup` | Controls whether missed historical intervals are created. | `False` |
| `max_active_runs` | Maximum concurrent DAG runs for this DAG. | `1` |
| `max_active_tasks` | Maximum concurrent task instances across active runs of this DAG. | `10` |
| `default_args` | Default task arguments inherited by tasks. | `{"retries": 3}` |
| `tags` | Labels used to organise and search DAGs. | `["finance","etl"]` |
| `params` | Runtime parameters supplied when a DAG is triggered. | `{"country":"IE"}` |
| `dagrun_timeout` | Maximum time allowed for a DAG run. | `timedelta(hours=3)` |
| `template_searchpath` | Additional directories for Jinja templates. | `["/usr/local/airflow/sql"]` |
| `user_defined_macros` | Custom variables or functions available in Jinja templates. | `{"schema":"sales"}` |
| `user_defined_filters` | Custom Jinja filters. | `{"format_date": my_filter}` |
| `render_template_as_native_obj` | Converts rendered template values to native Python types where possible. | `True` |
| `doc_md` | Markdown documentation shown in the Airflow UI. | `"## Sales pipeline"` |
| `default_view` | Default UI view for the DAG. | `"grid"` |
| `orientation` | Default graph orientation. | `"LR"` |
| `on_success_callback` | Callback when a DAG run succeeds. | `notify_success` |
| `on_failure_callback` | Callback when a DAG run fails. | `notify_failure` |
| `on_execute_callback` | Callback when DAG execution starts. | `notify_start` |
| `on_skipped_callback` | Callback for a skipped DAG run where supported. | `notify_skipped` |

Some advanced arguments vary by Airflow release. Check the API documentation for your installed version before using version-specific features.

## 6. Schedule parameter — detailed explanation

The `schedule` argument controls how frequently Airflow creates DAG runs.

### Common schedule values

```python
schedule="@once"
```

Run once.

```python
schedule="@hourly"
```

Run every hour.

```python
schedule="@daily"
```

Run daily.

```python
schedule="@weekly"
```

Run weekly.

```python
schedule="@monthly"
```

Run monthly.

```python
schedule="0 2 * * *"
```

Run every day at 02:00.

```python
schedule="0 6 * * 1"
```

Run every Monday at 06:00.

```python
schedule="*/15 * * * *"
```

Run every 15 minutes.

```python
schedule=None
```

No automatic schedule. Trigger the DAG manually or through an API/event integration.

### Cron format

```text
minute hour day-of-month month day-of-week
```

Example:

```text
0 2 * * *
| | | | |
| | | | +---- Every day of week
| | | +------ Every month
| | +-------- Every day of month
| +---------- 02:00
+------------ Minute 0
```

### Important: data intervals

Airflow scheduling is based on data intervals.

A daily DAG scheduled at 02:00 generally processes the previous completed daily interval, rather than assuming that the current calendar date is the data date.

Use:

```python
{{ data_interval_start }}
{{ data_interval_end }}
```

For example, a run scheduled on 5 November may process data from the interval 4 November to 5 November.

Do not build production ETL around the assumption that the execution date is always the current date.

## 7. Catchup parameter

```python
catchup=False
```

If a daily DAG was paused for five days, Airflow does not automatically create all five missed scheduled runs.

```python
catchup=True
```

Airflow creates runs for missed data intervals.

| Situation | Recommendation |
|---|---|
| Daily current-data pipeline | Usually `False` |
| Historical data backfill | `True` or explicit backfill |
| Financial reconciliation | Depends on interval and replay design |
| One-time pipeline | `@once` or manual trigger |

Only enable catchup if the tasks are designed to process historical intervals safely.

---

# PART 4 — TASK PARAMETERS

## 8. What is a task?

A task is an individual unit of work in a DAG.

Example:

```python
from airflow.operators.python import PythonOperator

def extract_data():
    print("Extracting data")

extract = PythonOperator(
    task_id="extract_data",
    python_callable=extract_data,
)
```

## 9. Complete list of common task arguments

These are common BaseOperator arguments inherited by many Airflow operators. Not every provider operator supports every argument in exactly the same way.

| Parameter | Detailed explanation |
|---|---|
| `task_id` | Unique identifier of the task within the DAG. |
| `owner` | Person or team responsible for the task. |
| `retries` | Number of retry attempts after failure. |
| `retry_delay` | Time to wait before retrying. |
| `retry_exponential_backoff` | Increases the wait time between retries. |
| `max_retry_delay` | Maximum retry delay when exponential backoff is enabled. |
| `execution_timeout` | Maximum duration allowed for one task execution attempt. |
| `depends_on_past` | Requires the previous scheduled instance of this task to succeed before the current one runs. |
| `wait_for_downstream` | Waits for downstream tasks from the previous run to complete. |
| `start_date` | Optional task-specific scheduling start date. Prefer a consistent DAG-level start date. |
| `end_date` | Optional task-specific end date. |
| `queue` | Selects a worker queue when supported by the executor. |
| `pool` | Assigns the task to a named Airflow pool. |
| `pool_slots` | Number of pool slots consumed by the task. |
| `priority_weight` | Relative task scheduling priority. |
| `weight_rule` | Determines how task priority weights are calculated. |
| `trigger_rule` | Controls when a task can run based on upstream task states. |
| `email` | Notification email recipients where email is configured. |
| `email_on_failure` | Legacy-style email notification on task failure. |
| `email_on_retry` | Legacy-style email notification on retry. |
| `do_xcom_push` | Controls whether an operator pushes its return value to XCom. |
| `executor_config` | Executor-specific configuration for a task. |
| `resources` | Resource hints for supported executors. |
| `run_as_user` | User identity for supported execution environments. |
| `max_active_tis_per_dag` | Maximum active task instances for this task across DAG runs. |
| `max_active_tis_per_dagrun` | Maximum active instances of this task within a DAG run. |
| `on_execute_callback` | Callback before task execution. |
| `on_success_callback` | Callback after successful task execution. |
| `on_failure_callback` | Callback after task failure. |
| `on_retry_callback` | Callback when the task is about to retry. |
| `on_skipped_callback` | Callback when a task is skipped, where supported. |
| `pre_execute` | Hook executed before the operator's main execution logic. |
| `post_execute` | Hook executed after the operator's main execution logic. |
| `doc_md` | Markdown documentation for the task. |
| `inlets` | Declares upstream data assets or lineage inputs. |
| `outlets` | Declares output data assets or lineage outputs. |

### Example: retries and timeout

```python
from datetime import timedelta

task_args = {
    "owner": "data-engineering",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "execution_timeout": timedelta(hours=1),
    "depends_on_past": False,
}
```

Explanation:

- `retries=3`: try again up to three times after the initial failure.
- `retry_delay=5 minutes`: initial wait before retrying.
- `retry_exponential_backoff=True`: increases the delay for subsequent attempts.
- `max_retry_delay=30 minutes`: caps the retry wait.
- `execution_timeout=1 hour`: stops a task attempt that runs too long.
- `depends_on_past=False`: does not require the previous scheduled instance to succeed.

Production tip: Retry temporary network failures, throttling and transient service errors. Do not repeatedly retry invalid input or other permanent business errors.

## 10. Trigger rules

A trigger rule decides when a task can execute based on upstream task results.

| Trigger rule | Explanation |
|---|---|
| `all_success` | All upstream tasks must succeed. Default behaviour. |
| `all_failed` | All upstream tasks must fail. |
| `all_done` | All upstream tasks must finish, regardless of their result. |
| `one_success` | At least one upstream task succeeds. |
| `one_failed` | At least one upstream task fails. |
| `none_failed` | No upstream task failed; skipped tasks may be allowed. |
| `none_failed_min_one_success` | No upstream task failed and at least one succeeded. |
| `none_skipped` | No upstream task was skipped. |
| `always` | Run regardless of upstream states. |

Example:

```python
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule

cleanup = EmptyOperator(
    task_id="cleanup",
    trigger_rule=TriggerRule.ALL_DONE,
)
```

This task can run after upstream tasks finish, even if some failed.

Use `all_done` for cleanup, resource release or status reporting. Do not use it for normal data loading unless you have explicitly handled failed upstream tasks.

---

# PART 5 — OPERATORS

## 11. What is an operator?

An operator defines what a task does.

### Important operator types

| Operator | Explanation | Example |
|---|---|---|
| `PythonOperator` | Executes a Python function | Validate data |
| `BashOperator` | Executes a shell command | Run a script |
| `EmptyOperator` | No-op task for workflow structure | Start/end |
| `BranchPythonOperator` | Selects a downstream branch | Choose processing path |
| `ShortCircuitOperator` | Skips downstream tasks when condition is false | Stop when no records |
| `EmailOperator` | Sends email | Pipeline notification |
| `TriggerDagRunOperator` | Starts another DAG | Trigger downstream DAG |
| `ExternalTaskSensor` | Waits for another DAG/task | Wait for upstream DAG |
| `S3CreateObjectOperator` | Creates an S3 object | Write a marker |
| `GlueJobOperator` | Starts an AWS Glue job | Run ETL |
| `EcsRunTaskOperator` | Runs an ECS task | Execute container |
| `EmrAddStepsOperator` | Submits steps to EMR | Spark job |
| `RedshiftSQLOperator` | Runs Redshift SQL | Load warehouse |
| `BashOperator` | Executes a shell command | Run a CLI |
| `SQLExecuteQueryOperator` | Runs SQL through a supported database connection | Query a database |

Many integrations are provided through provider packages, so install the appropriate provider and check its version compatibility.

## 12. PythonOperator example

```python
from airflow.operators.python import PythonOperator

def validate_data():
    print("Validating data")
    return "SUCCESS"

validate = PythonOperator(
    task_id="validate_data",
    python_callable=validate_data,
)
```

Important parameters:

| Parameter | Explanation |
|---|---|
| `python_callable` | Function that Airflow executes |
| `op_args` | Positional arguments passed to the function |
| `op_kwargs` | Keyword arguments passed to the function |
| `templates_dict` | Template values passed to the callable |
| `templates_exts` | File extensions to template |
| `show_return_value_in_logs` | Controls return-value logging |

Example:

```python
def add_numbers(a, b):
    return a + b

add = PythonOperator(
    task_id="add_numbers",
    python_callable=add_numbers,
    op_args=[10, 20],
)
```

## 13. BashOperator example

```python
from airflow.operators.bash import BashOperator

run_script = BashOperator(
    task_id="run_script",
    bash_command="python /usr/local/airflow/scripts/process.py",
)
```

Important parameters:

- `bash_command`: shell command to execute.
- `env`: environment variables passed to the process.
- `append_env`: whether to append the current environment.
- `cwd`: working directory.
- `output_encoding`: command output encoding.
- `skip_on_exit_code`: exit code that marks the task as skipped.
- `execution_timeout`: maximum allowed duration, inherited from BaseOperator.

Never place passwords or access keys directly in `bash_command`.

## 14. BranchPythonOperator example

```python
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator

def choose_branch():
    return "process_valid_data"

branch = BranchPythonOperator(
    task_id="choose_branch",
    python_callable=choose_branch,
)

valid = EmptyOperator(task_id="process_valid_data")
invalid = EmptyOperator(task_id="reject_invalid_data")

branch >> [valid, invalid]
```

The function returns the task ID of the branch to execute.

---

# PART 6 — SENSORS

## 15. What is a sensor?

A sensor waits for something to happen.

Example:

```text
Airflow starts
      |
      v
Wait for S3 file
      |
      v
File available?
   /       \
 No        Yes
 |          |
Wait      Continue
```

### Common sensors

| Sensor | Purpose |
|---|---|
| `S3KeySensor` | Waits for an S3 object |
| `S3KeysUnchangedSensor` | Waits until an S3 prefix stops changing |
| `FileSensor` | Waits for a local file |
| `ExternalTaskSensor` | Waits for another DAG task |
| `SqlSensor` | Waits for a SQL condition |
| `HttpSensor` | Waits for an HTTP endpoint |
| `TimeSensor` | Waits until a specified time |
| `DateTimeSensor` | Waits until a specified date/time |
| `PythonSensor` | Waits until a Python function returns true |

## 16. Sensor parameters

| Parameter | Explanation |
|---|---|
| `poke_interval` | Seconds between checks |
| `timeout` | Maximum time the sensor can wait |
| `mode` | `poke` or `reschedule` |
| `soft_fail` | Marks the task skipped rather than failed when it times out |
| `exponential_backoff` | Increases the time between checks |
| `max_wait` | Maximum wait between checks when exponential backoff is enabled |
| `deferrable` | For supported sensors, defers waiting to the Triggerer to free worker capacity |

### Poke mode

```python
mode="poke"
```

The sensor occupies a worker slot while waiting.

Use when the expected wait is short.

### Reschedule mode

```python
mode="reschedule"
```

The sensor releases its worker slot between checks.

Use when waiting for longer periods and a supported reschedule-mode sensor is available.

### Deferrable mode

```python
deferrable=True
```

For operators and sensors that implement deferral, Airflow moves the waiting work to the Triggerer.

This is often preferable for long-running waits.

### S3KeySensor example

```python
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

wait_for_file = S3KeySensor(
    task_id="wait_for_file",
    bucket_name="company-data-lake",
    bucket_key="raw/sales/sales.csv",
    aws_conn_id="aws_default",
    poke_interval=60,
    timeout=3600,
    mode="reschedule",
)
```

This waits for the file for up to one hour, checking every 60 seconds.

For wildcard keys, configure `wildcard_match=True` where supported by the provider version.

---

# PART 7 — TASKFLOW API, XCOM AND DEPENDENCIES

## 17. TaskFlow API

TaskFlow lets you write Python functions and convert them into Airflow tasks using decorators.

```python
from airflow.decorators import dag, task
import pendulum

@dag(
    dag_id="taskflow_example",
    schedule="@daily",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
)
def sales_pipeline():

    @task
    def extract():
        return {"sales": 100}

    @task
    def transform(data):
        return {
            "total_sales": data["sales"] * 2
        }

    @task
    def load(data):
        print(data)

    extracted = extract()
    transformed = transform(extracted)
    load(transformed)

sales_pipeline()
```

Benefits:

- Less boilerplate.
- Automatic task creation.
- Automatic dependency wiring.
- Automatic XCom handling for return values.
- Easier Python code organisation.

## 18. XCom

XCom means cross-communication.

It passes small values between tasks.

Example:

```python
@task
def extract():
    return {
        "s3_key": "raw/sales/file.csv",
        "record_count": 1000
    }

@task
def transform(data):
    print(data["s3_key"])
    print(data["record_count"])
```

Important:

- XCom is stored in Airflow's metadata system or a configured XCom backend.
- Do not pass large datasets through XCom.
- Pass S3 paths, object keys, identifiers and small metadata.
- Store large data in S3, databases or data warehouses.

Recommended pattern:

```text
Task A
  |
  v
Writes file to S3
  |
  v
Returns S3 object key through XCom
  |
  v
Task B
  |
  v
Reads file from S3
```

## 19. Task dependencies

Sequential:

```python
task_a >> task_b >> task_c
```

Equivalent:

```python
task_a.set_downstream(task_b)
task_b.set_downstream(task_c)
```

Parallel:

```python
task_a >> [task_b, task_c]
```

Join:

```python
[task_b, task_c] >> task_d
```

Combined:

```python
task_a >> [task_b, task_c] >> task_d
```

## 20. TaskGroup

TaskGroup organises related tasks visually.

```python
from airflow.utils.task_group import TaskGroup
from airflow.operators.empty import EmptyOperator

with TaskGroup("data_validation") as validation_group:
    check_schema = EmptyOperator(task_id="check_schema")
    check_quality = EmptyOperator(task_id="check_quality")

    check_schema >> check_quality
```

Useful for large DAGs with repeated stages.

## 21. Dynamic task mapping

Dynamic task mapping creates task instances based on runtime input.

```python
from airflow.decorators import task

@task
def get_files():
    return [
        "file1.csv",
        "file2.csv",
        "file3.csv"
    ]

@task
def process_file(file_name):
    print(f"Processing {file_name}")

files = get_files()
process_file.expand(file_name=files)
```

This dynamically creates a task instance for each file.

Use it for:

- Multiple S3 files.
- Multiple customer datasets.
- Multiple partitions.
- Parallel API calls.

Control concurrency using `max_active_tis_per_dag`, pools and DAG-level limits.

---

# PART 8 — PRODUCTION AIRFLOW DAG EXAMPLE

## 22. Production scenario: daily sales ETL on AWS

### Business requirement

Every day:

1. Wait for sales data to arrive in S3.
2. Run an AWS Glue ETL job.
3. Write curated data to S3.
4. Validate the output manifest.
5. Notify the operations team if the workflow fails.

### Architecture

```text
              Source System
                    |
                    v
               S3 Raw Bucket
                    |
                    v
              Airflow / MWAA
                    |
                    v
              S3KeySensor
                    |
                    v
              AWS Glue Job
                    |
                    v
             S3 Curated Data
                    |
                    v
             Output Validation
                    |
                    v
             Pipeline Complete
                    |
                    v
             CloudWatch Logs
```

### Project structure

```text
airflow-project/
│
├── dags/
│   └── daily_sales_etl.py
│
├── requirements.txt
│
├── terraform/
│   ├── versions.tf
│   ├── variables.tf
│   ├── main.tf
│   ├── iam.tf
│   ├── s3.tf
│   └── outputs.tf
│
└── policy/
    └── mwaa.rego
```

## 23. Production DAG code

File: `dags/daily_sales_etl.py`

This example assumes:

- An existing AWS Glue job called `sales-etl-prod`.
- An S3 raw bucket containing daily sales files.
- An S3 curated bucket or prefix used by the Glue job.
- The Glue job writes a `_SUCCESS` or manifest object after completing successfully.

```python
from datetime import timedelta

import pendulum

from airflow import DAG
from airflow.decorators import task

from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

AWS_CONN_ID = "aws_default"

RAW_BUCKET = "company-data-lake-prod"
CURATED_BUCKET = "company-data-curated-prod"

GLUE_JOB_NAME = "sales-etl-prod"


# --------------------------------------------------
# DEFAULT TASK ARGUMENTS
# --------------------------------------------------

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "execution_timeout": timedelta(hours=2),
}


# --------------------------------------------------
# DAG DEFINITION
# --------------------------------------------------

with DAG(
    dag_id="daily_sales_etl_prod",

    description="Production daily sales ETL pipeline",

    schedule="0 3 * * *",

    start_date=pendulum.datetime(
        2025, 1, 1, tz="UTC"
    ),

    catchup=False,

    max_active_runs=1,

    max_active_tasks=5,

    default_args=default_args,

    tags=[
        "production",
        "sales",
        "etl",
        "aws",
    ],

    doc_md="""
    # Daily Sales ETL

    1. Wait for raw sales files.
    2. Execute Glue ETL.
    3. Validate curated output.
    """,
) as dag:

    # ----------------------------------------------
    # TASK 1: WAIT FOR INPUT FILE
    # ----------------------------------------------

    wait_for_sales_file = S3KeySensor(
        task_id="wait_for_sales_file",

        bucket_name=RAW_BUCKET,

        bucket_key=(
            "sales/"
            "dt={{ data_interval_start.strftime('%Y-%m-%d') }}/"
            "*.parquet"
        ),

        wildcard_match=True,

        aws_conn_id=AWS_CONN_ID,

        poke_interval=300,

        timeout=60 * 60 * 6,

        mode="reschedule",

        soft_fail=False,
    )

    # ----------------------------------------------
    # TASK 2: RUN AWS GLUE
    # ----------------------------------------------

    run_sales_glue = GlueJobOperator(
        task_id="run_sales_glue",

        job_name=GLUE_JOB_NAME,

        aws_conn_id=AWS_CONN_ID,

        script_args={
            "--RUN_DATE": (
                "{{ data_interval_start.strftime('%Y-%m-%d') }}"
            ),

            "--SOURCE_BUCKET": RAW_BUCKET,

            "--TARGET_BUCKET": CURATED_BUCKET,

            "--INPUT_PREFIX": (
                "sales/"
                "dt={{ data_interval_start.strftime('%Y-%m-%d') }}/"
            ),

            "--OUTPUT_PREFIX": (
                "sales/"
                "dt={{ data_interval_start.strftime('%Y-%m-%d') }}/"
            ),
        },

        wait_for_completion=True,

        verbose=True,
    )

    # ----------------------------------------------
    # TASK 3: VALIDATE OUTPUT
    # ----------------------------------------------

    @task(
        retries=2,
        retry_delay=timedelta(minutes=2),
    )
    def validate_output():

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

        hook = S3Hook(
            aws_conn_id=AWS_CONN_ID
        )

        from airflow.operators.python import get_current_context

        context = get_current_context()

        run_date = context["data_interval_start"].strftime(
            "%Y-%m-%d"
        )

        output_key = (
            f"sales/dt={run_date}/_SUCCESS"
        )

        exists = hook.check_for_key(
            key=output_key,
            bucket_name=CURATED_BUCKET,
        )

        if not exists:
            raise ValueError(
                f"Expected output marker not found: {output_key}"
            )

        return {
            "status": "SUCCESS",
            "output_key": output_key,
        }

    validation = validate_output()

    # ----------------------------------------------
    # DEPENDENCIES
    # ----------------------------------------------

    wait_for_sales_file >> run_sales_glue >> validation
```

### Understand the production DAG

| Task | Responsibility |
|---|---|
| `wait_for_sales_file` | Waits for the expected daily S3 input |
| `run_sales_glue` | Starts the existing AWS Glue job and waits for completion |
| `validate_output` | Checks that the expected output marker exists |
| DAG settings | Limits concurrency and configures retries |

**Important production considerations:**

- The Glue job must create the `_SUCCESS` marker only after its output has been fully committed.
- The Glue job should be idempotent for a given `RUN_DATE`.
- A failed or partial Glue run must not leave a misleading success marker.
- The input sensor should match the actual source naming convention.
- Use the Airflow execution role for AWS access rather than hardcoded AWS credentials.
- For long-running Glue jobs, consider a supported deferrable operator to free worker capacity.
- Add a notification callback or separate failure-notification workflow for operational alerting.
- Ensure the Glue job has its own execution role and least-privilege permissions.

### Requirements file

`requirements.txt`

```text
apache-airflow-providers-amazon
```

In production, pin a provider version that is compatible with the exact MWAA Airflow version. Do not blindly install the newest provider release.

---

# PART 9 — AWS MWAA

## 24. What is MWAA?

MWAA means Amazon Managed Workflows for Apache Airflow.

It is AWS's managed service for running Apache Airflow.

Instead of maintaining the Airflow scheduler, webserver, workers and metadata database yourself, AWS manages the environment infrastructure.

### Self-managed Airflow vs MWAA

| Component | Self-managed Airflow | AWS MWAA |
|---|---|---|
| Scheduler | You manage | AWS manages |
| Workers | You manage | AWS manages |
| Webserver | You manage | AWS manages |
| Metadata database | You manage | AWS manages |
| Infrastructure scaling | You configure | MWAA manages supported scaling |
| Logging | You configure | CloudWatch integration |
| IAM | You configure | AWS IAM integration |
| Networking | You configure | VPC-based managed environment |
| DAG code | You deploy | Upload to S3 |
| Infrastructure provisioning | Terraform or other tools | Terraform or other tools |

### MWAA architecture

```text
                  Developer
                      |
                      v
                Git Repository
                      |
                      v
                 CI/CD Pipeline
                      |
                      v
                  S3 Bucket
                 /    |    \
                /     |     \
               v      v      v
             DAGs  Plugins  Requirements
                      |
                      v
                 AWS MWAA
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       Scheduler   Webserver   Workers
          |                       |
          |                       v
          |                   AWS Glue
          |                   Amazon S3
          |                   ECS / EMR
          |                   Redshift
          |
          v
     Metadata Database
          |
          v
     CloudWatch Logs
```

---

# PART 10 — TERRAFORM: COMPLETE MWAA RESOURCE PARAMETERS

## 25. Main Terraform resource

The principal Terraform resource is:

```hcl
resource "aws_mwaa_environment" "this" {
  name               = "sales-airflow-prod"
  airflow_version    = var.airflow_version
  environment_class  = "mw1.small"

  source_bucket_arn  = aws_s3_bucket.dags.arn
  dag_s3_path        = "dags"

  execution_role_arn = aws_iam_role.mwaa.arn

  network_configuration {
    subnet_ids = var.private_subnet_ids

    security_group_ids = [
      aws_security_group.mwaa.id
    ]
  }
}
```

## 26. Top-level MWAA parameters

| Parameter | Required? | Detailed explanation |
|---|---|---|
| `name` | Yes | Unique name of the MWAA environment. |
| `airflow_version` | Optional | Airflow version supported by MWAA. Pin an approved version rather than relying on an implicit default. |
| `environment_class` | Optional | Environment size, such as `mw1.small`, `mw1.medium`, `mw1.large`, and larger supported classes. |
| `execution_role_arn` | Yes | IAM role that MWAA assumes to access AWS services and execute workflows. |
| `source_bucket_arn` | Yes | ARN of the S3 bucket containing DAGs and supporting files. |
| `dag_s3_path` | Yes | Relative S3 path of the DAG folder. |
| `network_configuration` | Yes | Private subnet and security group configuration. |
| `airflow_configuration_options` | Optional | Airflow configuration overrides. |
| `kms_key` | Optional | Customer-managed KMS key for supported MWAA encryption. |
| `logging_configuration` | Optional | CloudWatch logging configuration. |
| `min_workers` | Optional | Minimum number of worker instances. |
| `max_workers` | Optional | Maximum number of worker instances for autoscaling. |
| `min_webservers` | Optional | Minimum webserver capacity, where supported. |
| `max_webservers` | Optional | Maximum webserver capacity, where supported. |
| `schedulers` | Optional | Number of scheduler instances, within the limits for the selected version and class. |
| `plugins_s3_path` | Optional | S3 location of the plugins ZIP file. |
| `plugins_s3_object_version` | Optional | S3 version ID of the plugins ZIP file. |
| `requirements_s3_path` | Optional | S3 location of `requirements.txt`. |
| `requirements_s3_object_version` | Optional | S3 version ID of the requirements file. |
| `startup_script_s3_path` | Optional | S3 path to a supported startup script. |
| `startup_script_s3_object_version` | Optional | S3 version ID of the startup script. |
| `webserver_access_mode` | Optional | Controls webserver access, such as private-only or public-only, depending on supported MWAA versions. |
| `endpoint_management` | Optional | Controls whether AWS or the customer manages MWAA VPC endpoints. |
| `worker_replacement_strategy` | Optional | Worker replacement behaviour, such as graceful or forced replacement where supported. |
| `weekly_maintenance_window_start` | Optional | Weekly maintenance window. |
| `region` | Optional | AWS region; otherwise uses the provider's configured region. |
| `tags` | Optional | Resource tags. |

**Provider note:** The exact availability of some parameters depends on the AWS provider version and MWAA version. Check the Terraform Registry for the version pinned in your lock file.

## 27. Explain each important MWAA parameter

### `name`

```hcl
name = "sales-airflow-prod"
```

The name of the MWAA environment.

Use a consistent naming convention:

```text
application-environment-purpose
sales-prod-airflow
sales-dev-airflow
```

### `airflow_version`

```hcl
airflow_version = var.airflow_version
```

Selects the Apache Airflow version.

Why important:

- Determines compatible DAG APIs.
- Determines supported provider packages.
- Affects Python compatibility.
- Affects available Airflow configuration.
- Influences upgrade planning.

Do not assume every Airflow version is available in every AWS region.

### `environment_class`

```hcl
environment_class = "mw1.small"
```

Determines the size of the managed environment.

Typical capacity examples from AWS documentation:

| Class | Approximate DAG capacity | Default concurrent task capacity |
|---|---:|---:|
| `mw1.micro` | Up to 25 | 3 |
| `mw1.small` | Up to 50 | 5 |
| `mw1.medium` | Up to 250 | 10 |
| `mw1.large` | Up to 1,000 | 20 |
| `mw1.xlarge` | Up to 2,000 | 40 |
| `mw1.2xlarge` | Up to 4,000 | 80 |

These are indicative capacity figures, not guaranteed throughput. Real capacity depends on DAG parsing, task complexity, worker size, database activity and concurrency settings.

### `source_bucket_arn`

```hcl
source_bucket_arn = aws_s3_bucket.dags.arn
```

Specifies the S3 bucket where MWAA obtains DAG files and supporting resources.

The bucket should:

- Be private.
- Have versioning enabled.
- Block public access.
- Use encryption.
- Have an appropriate bucket policy.
- Be accessible to the MWAA execution role.

### `dag_s3_path`

```hcl
dag_s3_path = "dags"
```

Relative location of the DAG folder in the source bucket.

Example:

```text
s3://company-airflow-prod/
    dags/
        daily_sales_etl.py
        customer_pipeline.py
```

### `execution_role_arn`

```hcl
execution_role_arn = aws_iam_role.mwaa.arn
```

IAM role used by MWAA.

It needs permissions for:

- Reading DAG files.
- Publishing logs.
- Publishing metrics.
- Accessing the required SQS queues.
- Accessing Glue, S3, Redshift or other services used by DAGs.
- Using KMS when customer-managed encryption is configured.

### `airflow_configuration_options`

```hcl
airflow_configuration_options = {
  "core.load_examples"              = "False"
  "scheduler.catchup_by_default"    = "False"
}
```

Overrides selected Airflow configuration options.

The left side is the Airflow configuration key. The right side is the configured value.

Examples of configuration areas include:

| Section | Purpose |
|---|---|
| `core` | Core Airflow behaviour |
| `scheduler` | Scheduler configuration |
| `webserver` | Webserver configuration |
| `logging` | Logging configuration |
| `celery` | Celery executor configuration where applicable |
| `secrets` | Secrets backend configuration |
| `metrics` | Metrics configuration |

Use only options supported by the selected MWAA Airflow version. AWS controls some configuration settings.

### `kms_key`

```hcl
kms_key = aws_kms_key.mwaa.arn
```

Selects a customer-managed KMS key for supported MWAA encryption.

Use this when you need:

- Customer-controlled encryption keys.
- Key rotation.
- Key access auditing.
- Separation of key administration and environment administration.

The KMS key policy must allow the required service operations.

### `logging_configuration`

Configures CloudWatch logs for MWAA.

### `min_workers`

```hcl
min_workers = 1
```

Minimum worker instances maintained by MWAA.

A higher minimum can reduce the time needed to respond to a task backlog, but increases cost.

### `max_workers`

```hcl
max_workers = 5
```

Maximum workers that MWAA can scale up to.

More workers allow greater parallel execution, subject to DAG concurrency, pools, executor and service limits.

### `schedulers`

```hcl
schedulers = 2
```

Number of Airflow schedulers.

Additional schedulers can improve scheduling capacity and availability where supported.

### `plugins_s3_path`

```hcl
plugins_s3_path = "plugins.zip"
```

S3 path for the Airflow plugins ZIP.

Plugins can add custom operators, hooks, sensors and other extensions. Only deploy reviewed and version-compatible plugins.

### `plugins_s3_object_version`

```hcl
plugins_s3_object_version = aws_s3_object.plugins.version_id
```

Pins the plugin ZIP to a specific S3 object version.

### `requirements_s3_path`

```hcl
requirements_s3_path = "requirements.txt"
```

S3 path of Python dependencies.

Example:

```text
apache-airflow-providers-amazon==<compatible-version>
```

Pin compatible dependencies and test them before uploading to production.

### `requirements_s3_object_version`

Pins the requirements file to a specific S3 object version.

This helps control deployments and rollbacks.

### `startup_script_s3_path`

```hcl
startup_script_s3_path = "scripts/startup.sh"
```

S3 path to a supported environment startup script.

Use only for supported environment customisation. It is not a substitute for a proper dependency and deployment process.

### `webserver_access_mode`

```hcl
webserver_access_mode = "PRIVATE_ONLY"
```

Controls whether the Airflow UI is accessible through a private or public access mode supported by the environment version.

Production recommendation: prefer private access when your organisation can provide secure internal access through VPN or another approved network path.

### `endpoint_management`

```hcl
endpoint_management = "SERVICE"
```

Controls who manages the required VPC endpoints.

- `SERVICE`: AWS manages the endpoints.
- `CUSTOMER`: you create and manage the required endpoints.

### `worker_replacement_strategy`

```hcl
worker_replacement_strategy = "GRACEFUL"
```

Controls supported worker replacement behaviour.

Use graceful replacement where available and appropriate to reduce disruption to running work.

---

# PART 11 — NESTED TERRAFORM PARAMETERS

## 28. Network configuration

```hcl
network_configuration {
  subnet_ids = [
    "subnet-11111111",
    "subnet-22222222"
  ]

  security_group_ids = [
    aws_security_group.mwaa.id
  ]
}
```

| Parameter | Explanation |
|---|---|
| `subnet_ids` | Private subnet IDs for the MWAA environment. Use two subnets in different Availability Zones. |
| `security_group_ids` | Security groups associated with the MWAA environment. |

The VPC must have the required connectivity for MWAA, AWS service integrations and any external systems used by your DAGs.

For private routing without internet access, create and configure the required VPC endpoints and endpoint policies.

## 29. Logging configuration

```hcl
logging_configuration {

  dag_processing_logs {
    enabled   = true
    log_level = "INFO"
  }

  scheduler_logs {
    enabled   = true
    log_level = "INFO"
  }

  task_logs {
    enabled   = true
    log_level = "INFO"
  }

  webserver_logs {
    enabled   = true
    log_level = "WARNING"
  }

  worker_logs {
    enabled   = true
    log_level = "INFO"
  }
}
```

| Log group | Explanation |
|---|---|
| `dag_processing_logs` | DAG file parsing and processing activity |
| `scheduler_logs` | Scheduler decisions and scheduling errors |
| `task_logs` | Task execution output |
| `webserver_logs` | Webserver events and errors |
| `worker_logs` | Worker activity |

Each log block supports:

| Parameter | Explanation |
|---|---|
| `enabled` | Enables or disables that log type |
| `log_level` | `CRITICAL`, `ERROR`, `WARNING`, `INFO` or `DEBUG` |

Production recommendation:

- Enable task and scheduler logs.
- Use `INFO` as a normal starting level.
- Use `DEBUG` temporarily for investigations.
- Set CloudWatch retention policies.
- Avoid logging credentials and sensitive customer information.

---

# PART 12 — PRODUCTION TERRAFORM IMPLEMENTATION

## 30. Architecture for production MWAA

This example provisions:

- S3 DAG source bucket.
- S3 versioning.
- S3 encryption.
- S3 public access protection.
- S3 bucket TLS policy.
- MWAA IAM execution role.
- MWAA IAM policy.
- MWAA security group.
- MWAA environment.
- CloudWatch logging.
- Worker autoscaling configuration.
- Private webserver access.

**Prerequisite:** The VPC and two private subnets already exist. Their IDs are passed into Terraform. This avoids creating or changing your organisation's core networking infrastructure inside the Airflow deployment.

### Terraform project structure

```text
mwaa-production/
│
├── versions.tf
├── variables.tf
├── s3.tf
├── iam.tf
├── security.tf
├── mwaa.tf
├── outputs.tf
│
└── dags/
    └── daily_sales_etl.py
```

## 31. versions.tf

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Application = "airflow"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "data-engineering"
    }
  }
}
```

Explanation:

- `required_version`: minimum Terraform version.
- `required_providers`: declares the AWS provider.
- `version`: constrains the provider to a compatible major release.
- `region`: selects the AWS deployment region.
- `default_tags`: automatically adds governance and cost-allocation tags.

Commit `.terraform.lock.hcl` to version control.

## 32. variables.tf

```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "mwaa_name" {
  description = "MWAA environment name"
  type        = string
  default     = "sales-airflow-prod"
}

variable "airflow_version" {
  description = "Airflow version supported by MWAA"
  type        = string
}

variable "vpc_id" {
  description = "Existing VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Two private subnet IDs in different AZs"
  type        = list(string)

  validation {
    condition     = length(var.private_subnet_ids) == 2
    error_message = "Provide exactly two private subnet IDs."
  }
}

variable "data_bucket_arn" {
  description = "S3 data lake bucket ARN used by DAG tasks"
  type        = string
}

variable "glue_job_name" {
  description = "Existing AWS Glue job name"
  type        = string
  default     = "sales-etl-prod"
}
```

## 33. s3.tf

```hcl
resource "aws_s3_bucket" "dags" {
  bucket = "company-sales-airflow-prod-123456"

  force_destroy = false

  tags = {
    Name = "sales-airflow-dags"
  }
}

resource "aws_s3_bucket_versioning" "dags" {
  bucket = aws_s3_bucket.dags.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "dags" {
  bucket = aws_s3_bucket.dags.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "dags" {
  bucket = aws_s3_bucket.dags.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

data "aws_iam_policy_document" "dags_bucket_policy" {

  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = ["s3:*"]

    resources = [
      aws_s3_bucket.dags.arn,
      "${aws_s3_bucket.dags.arn}/*"
    ]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "dags" {
  bucket = aws_s3_bucket.dags.id
  policy = data.aws_iam_policy_document.dags_bucket_policy.json

  depends_on = [
    aws_s3_bucket_public_access_block.dags
  ]
}
```

Explanation:

| Resource | Purpose |
|---|---|
| `aws_s3_bucket` | Creates the DAG source bucket |
| `aws_s3_bucket_versioning` | Preserves object versions |
| `aws_s3_bucket_server_side_encryption_configuration` | Enables encryption at rest |
| `aws_s3_bucket_public_access_block` | Blocks public access |
| `aws_s3_bucket_policy` | Denies insecure HTTP requests |

The bucket name must be globally unique. Replace the example with an approved name.

This example uses S3-managed encryption. If your organisation requires a customer-managed KMS key, configure it and its policy explicitly.

## 34. iam.tf

### Step 1: Account details

```hcl
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}
```

These data sources retrieve the AWS account ID and current region.

### Step 2: MWAA trust policy

```hcl
data "aws_iam_policy_document" "mwaa_assume_role" {

  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["airflow.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"

      values = [
        data.aws_caller_identity.current.account_id
      ]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"

      values = [
        "arn:aws:airflow:${var.aws_region}:${data.aws_caller_identity.current.account_id}:environment/${var.mwaa_name}"
      ]
    }
  }
}

resource "aws_iam_role" "mwaa" {
  name               = "${var.mwaa_name}-execution-role"
  assume_role_policy = data.aws_iam_policy_document.mwaa_assume_role.json
}
```

Explanation:

- `sts:AssumeRole`: permits the service to assume the role.
- `airflow.amazonaws.com`: MWAA service principal.
- `aws:SourceAccount`: limits which AWS account can use the role.
- `aws:SourceArn`: restricts the trust relationship to the intended MWAA environment.

Verify the trust policy requirements against the current AWS MWAA execution-role documentation for your chosen version and account.

### Step 3: MWAA execution policy

```hcl
data "aws_iam_policy_document" "mwaa_execution" {

  # Publish Airflow metrics

  statement {
    sid    = "PublishAirflowMetrics"
    effect = "Allow"

    actions = [
      "airflow:PublishMetrics"
    ]

    resources = [
      "arn:aws:airflow:${var.aws_region}:${data.aws_caller_identity.current.account_id}:environment/${var.mwaa_name}"
    ]
  }

  # Read DAG files

  statement {
    sid    = "ReadDagBucket"
    effect = "Allow"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.dags.arn
    ]
  }

  statement {
    sid    = "ReadDagObjects"
    effect = "Allow"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "${aws_s3_bucket.dags.arn}/*"
    ]
  }

  # Access the data lake

  statement {
    sid    = "AccessDataLake"
    effect = "Allow"

    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject"
    ]

    resources = [
      var.data_bucket_arn,
      "${var.data_bucket_arn}/*"
    ]
  }

  # Airflow task execution and logs

  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:GetLogEvents",
      "logs:GetLogRecord",
      "logs:GetLogGroupFields",
      "logs:GetQueryResults",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:FilterLogEvents"
    ]

    resources = ["*"]
  }

  # CloudWatch metrics

  statement {
    sid    = "CloudWatchMetrics"
    effect = "Allow"

    actions = [
      "cloudwatch:PutMetricData"
    ]

    resources = ["*"]
  }

  # MWAA Celery queue access

  statement {
    sid    = "SQSAccess"
    effect = "Allow"

    actions = [
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:ReceiveMessage",
      "sqs:SendMessage"
    ]

    resources = ["*"]
  }

  # Start and monitor the approved Glue job

  statement {
    sid    = "RunSalesGlueJob"
    effect = "Allow"

    actions = [
      "glue:StartJobRun",
      "glue:GetJob",
      "glue:GetJobRun",
      "glue:GetJobRuns",
      "glue:BatchStopJobRun"
    ]

    resources = [
      "arn:aws:glue:${var.aws_region}:${data.aws_caller_identity.current.account_id}:job/${var.glue_job_name}"
    ]
  }
}

resource "aws_iam_policy" "mwaa_execution" {
  name   = "${var.mwaa_name}-execution-policy"
  policy = data.aws_iam_policy_document.mwaa_execution.json
}

resource "aws_iam_role_policy_attachment" "mwaa_execution" {
  role       = aws_iam_role.mwaa.name
  policy_arn = aws_iam_policy.mwaa_execution.arn
}
```

**Important production IAM note:**

This is a teaching baseline, not a complete universal MWAA service-role policy. AWS MWAA requires certain service permissions for its own managed infrastructure, and the exact permissions can depend on configuration and version.

Before production:

- Compare against the current AWS MWAA execution-role policy guidance.
- Add permissions for the services your DAGs actually invoke.
- Scope CloudWatch Logs and SQS resources wherever supported.
- Review the SQS and CloudWatch permissions required by MWAA itself.
- Add KMS permissions if using a customer-managed key.
- Keep Glue execution-role permissions separate from MWAA's role.
- Do not grant the MWAA role broad access to all application resources without a clear requirement.

## 35. security.tf

```hcl
resource "aws_security_group" "mwaa" {

  name        = "${var.mwaa_name}-sg"
  description = "Security group for MWAA"
  vpc_id      = var.vpc_id

  tags = {
    Name = "${var.mwaa_name}-sg"
  }
}

# Required MWAA self-referencing communication rule

resource "aws_vpc_security_group_ingress_rule" "mwaa_self" {

  security_group_id = aws_security_group.mwaa.id

  referenced_security_group_id = aws_security_group.mwaa.id

  ip_protocol = "-1"

  description = "Allow MWAA components to communicate"
}

# Example outbound rule.
# Tighten egress where your architecture and required AWS endpoints allow it.

resource "aws_vpc_security_group_egress_rule" "mwaa_egress" {

  security_group_id = aws_security_group.mwaa.id

  cidr_ipv4 = "0.0.0.0/0"

  ip_protocol = "-1"

  description = "Outbound connectivity for MWAA"
}
```

Explanation:

- `vpc_id`: existing VPC where MWAA will run.
- Self-referencing ingress: permits communication between MWAA components.
- Egress: permits outbound communication.

AWS's networking guidance specifies the security group communication requirements. Do not remove required MWAA traffic rules without checking the official network documentation.

## 36. mwaa.tf

```hcl
resource "aws_mwaa_environment" "sales" {

  name = var.mwaa_name

  airflow_version = var.airflow_version

  environment_class = "mw1.small"

  source_bucket_arn = aws_s3_bucket.dags.arn

  dag_s3_path = "dags"

  execution_role_arn = aws_iam_role.mwaa.arn

  endpoint_management = "SERVICE"

  webserver_access_mode = "PRIVATE_ONLY"

  min_workers = 1

  max_workers = 5

  min_webservers = 2

  max_webservers = 2

  schedulers = 2

  worker_replacement_strategy = "GRACEFUL"

  airflow_configuration_options = {
    "core.load_examples"           = "False"
    "scheduler.catchup_by_default" = "False"
  }

  network_configuration {

    subnet_ids = var.private_subnet_ids

    security_group_ids = [
      aws_security_group.mwaa.id
    ]
  }

  logging_configuration {

    dag_processing_logs {
      enabled   = true
      log_level = "INFO"
    }

    scheduler_logs {
      enabled   = true
      log_level = "INFO"
    }

    task_logs {
      enabled   = true
      log_level = "INFO"
    }

    webserver_logs {
      enabled   = true
      log_level = "WARNING"
    }

    worker_logs {
      enabled   = true
      log_level = "INFO"
    }
  }

  tags = {
    Application = "sales-etl"
    Environment = var.environment
    Owner       = "data-engineering"
    CostCenter  = "engineering"
  }

  depends_on = [
    aws_iam_role_policy_attachment.mwaa_execution,
    aws_s3_bucket_public_access_block.dags,
    aws_s3_bucket_policy.dags
  ]

  lifecycle {
    prevent_destroy = true
  }
}
```

### Explain the production choices

| Setting | Why it is used |
|---|---|
| `mw1.small` | Starting size for a relatively small environment |
| `PRIVATE_ONLY` | Restricts UI access to approved private network paths |
| `min_workers=1` | Keeps baseline worker capacity |
| `max_workers=5` | Allows workers to scale with task demand |
| `min_webservers=2` | Maintains minimum webserver availability for supported classes |
| `max_webservers=2` | Avoids unnecessary webserver scaling |
| `schedulers=2` | Provides multiple schedulers where supported |
| `GRACEFUL` | Uses graceful worker replacement |
| CloudWatch logs | Provides operational visibility |
| `prevent_destroy` | Protects the environment from accidental Terraform destruction |

The selected class and worker settings are examples. Size the environment using measured DAG volume, task concurrency, memory usage and scheduling performance.

**Note:** `prevent_destroy` also prevents normal Terraform destruction. Remove it deliberately during an approved decommissioning process.

## 37. outputs.tf

```hcl
output "mwaa_arn" {
  description = "MWAA environment ARN"
  value       = aws_mwaa_environment.sales.arn
}

output "mwaa_webserver_url" {
  description = "MWAA webserver URL"
  value       = aws_mwaa_environment.sales.webserver_url
}

output "mwaa_status" {
  description = "MWAA environment status"
  value       = aws_mwaa_environment.sales.status
}

output "mwaa_execution_role_arn" {
  description = "MWAA execution role ARN"
  value       = aws_iam_role.mwaa.arn
}

output "dags_bucket" {
  description = "S3 DAG bucket"
  value       = aws_s3_bucket.dags.bucket
}
```

---

# PART 13 — DEPLOYMENT

## 38. Terraform deployment steps

### Step 1: Initialise

```bash
terraform init
```

Downloads provider plugins and initialises the Terraform project.

### Step 2: Format

```bash
terraform fmt -recursive
```

Formats the Terraform files.

### Step 3: Validate

```bash
terraform validate
```

Checks Terraform syntax and configuration consistency.

### Step 4: Plan

```bash
terraform plan -out=tfplan
```

Shows the infrastructure changes Terraform intends to make.

### Step 5: Apply

```bash
terraform apply tfplan
```

Creates the MWAA environment and supporting infrastructure.

MWAA environment creation can take a considerable amount of time. Terraform's provider documentation defines extended create/update timeouts.

### Step 6: Upload DAGs

After creating the environment, deploy the DAG files into the S3 DAG directory.

Example:

```bash
aws s3 sync ./dags \
  s3://company-sales-airflow-prod-123456/dags/
```

### Step 7: Upload requirements

```bash
aws s3 cp requirements.txt \
  s3://company-sales-airflow-prod-123456/requirements.txt
```

Update the MWAA environment's `requirements_s3_path` and object version if you are using a requirements file.

### Step 8: Verify MWAA

```bash
aws mwaa get-environment \
  --name sales-airflow-prod
```

Wait until the environment is available.

### Step 9: Check DAGs

Use the Airflow UI or CLI/API supported by your environment to check that:

- DAG files have been parsed.
- The DAG appears in the UI.
- No import errors exist.
- The expected schedule is present.
- The AWS connection works.
- The Glue job can be started.

---

# PART 14 — COST

## 39. How MWAA pricing works

MWAA costs are not simply based on how many DAGs you create.

The main cost components are:

1. Base environment usage.
2. Additional worker instances.
3. Additional scheduler instances.
4. Additional webserver instances.
5. Metadata database storage.
6. Supporting AWS services.

AWS bills the environment while it is running, including periods when it is idle.

### Pricing model

```text
Monthly MWAA cost =
Base environment cost
+ Additional worker cost
+ Additional scheduler cost
+ Additional webserver cost
+ Metadata storage cost
+ Supporting AWS service costs
```

### Example: small environment

Using the illustrative small-environment price of $0.49 per hour:

```text
Environment price = $0.49/hour

Monthly hours = 730

Base cost = 730 x $0.49

Base monthly cost = $357.70
```

This is an illustrative calculation, not a guaranteed Ireland quote. Confirm the current `eu-west-1` rates in the AWS pricing page or AWS Pricing Calculator.

### Additional cost example

Suppose the environment scales to two additional small workers for 100 hours each.

Using an illustrative additional-worker rate of $0.055 per hour:

```text
Additional workers = 2

Hours = 100

Rate = $0.055

Cost = 2 x 100 x $0.055

Additional worker cost = $11.00
```

Total illustrative cost:

```text
Base environment = $357.70

Additional workers = $11.00

Total = $368.70
```

This excludes metadata storage and other AWS services.

### Additional services to include

| AWS service | Possible cost |
|---|---|
| S3 | DAG files, logs and data storage |
| CloudWatch Logs | Log ingestion and storage |
| CloudWatch metrics | Monitoring and custom metrics |
| KMS | Customer-managed key usage |
| NAT Gateway | Hourly and data processing charges |
| VPC endpoints | Endpoint hours and data processing |
| Glue | Job execution time and DPUs |
| Redshift | Compute and storage |
| ECS | Task compute |
| SQS | Queue requests |
| Data transfer | Applicable data transfer charges |

### Cost optimisation

- Choose the smallest environment that meets actual workload requirements.
- Avoid unnecessary minimum workers.
- Set a realistic `max_workers`.
- Use reschedule or deferrable sensors.
- Avoid excessive DAG parsing and expensive top-level Python operations.
- Keep DAGs efficient.
- Use external compute services for heavy processing.
- Set CloudWatch log retention.
- Avoid excessive debug logging.
- Monitor metadata database growth.
- Review NAT Gateway and VPC endpoint costs.
- Delete unused development environments when appropriate.

---

# PART 15 — SECURITY BEST PRACTICES

## 40. IAM security

- Use a dedicated execution role for each MWAA environment.
- Restrict S3 access to the required DAG and data buckets.
- Restrict Glue access to approved jobs.
- Avoid `AdministratorAccess`.
- Avoid hardcoded AWS credentials in DAG files.
- Use IAM roles and supported secrets backends.
- Keep Glue execution permissions separate from MWAA permissions.
- Restrict who can access the Airflow UI and trigger production DAGs.

## 41. Network security

For production:

- Use private subnets in two Availability Zones.
- Use a private webserver where appropriate.
- Restrict security group ingress.
- Permit required self-referencing MWAA communication.
- Use VPC endpoints for required AWS services where appropriate.
- Restrict endpoint policies.
- Control internet egress.
- Use VPN or approved internal access for the private Airflow UI.

**Important:** MWAA requires correctly configured VPC networking. A private environment without the required endpoints and service connectivity will not work simply because the subnets are private.

## 42. Encryption

- Encrypt the DAG source bucket.
- Enable S3 versioning.
- Use KMS where required by your security policy.
- Protect CloudWatch log groups.
- Protect Airflow connections and secrets.
- Never put credentials in DAG code.
- Do not print sensitive data into task logs.

## 43. DAG security

Avoid:

```python
password = "MyPassword123"
```

Avoid:

```python
aws_access_key = "AKIA..."
```

Instead:

- Use the MWAA execution role.
- Use IAM-based AWS connections.
- Use AWS Secrets Manager or another supported secrets backend.
- Restrict DAG deployment permissions.
- Review third-party provider packages.
- Scan dependencies for vulnerabilities.

---

# PART 16 — POLICY AS CODE

## 44. What is Policy as Code?

Policy as Code means automatically checking infrastructure against security and operational rules before deployment.

For MWAA, policies can enforce:

- Private webserver access.
- CloudWatch logging.
- S3 public access blocking.
- S3 encryption.
- Required tags.
- Approved Airflow versions.
- Least-privilege IAM.
- Approved environment sizes.

### Recommended tools

| Tool | Purpose |
|---|---|
| Checkov | Terraform security scanning |
| tfsec | Terraform security scanning |
| OPA | Custom policy evaluation |
| Conftest | Runs Rego policies against Terraform plan JSON |
| Terraform validate | Validates Terraform configuration |
| CI/CD | Enforces deployment gates |

## 45. Checkov

Install:

```bash
pip install checkov
```

Scan the Terraform project:

```bash
checkov -d .
```

Scan a Terraform plan:

```bash
terraform plan -out=tfplan

terraform show -json tfplan > tfplan.json

checkov -f tfplan.json --framework terraform_plan
```

Checkov can identify potential problems such as:

- Public S3 access.
- Missing encryption.
- Weak IAM policies.
- Missing logging.
- Missing tags.
- Insecure network configurations.

Review findings and document justified exceptions.

## 46. OPA / Rego policy

Create:

`policy/mwaa.rego`

```rego
package terraform.mwaa

import rego.v1

resources := object.get(input, "resource_changes", [])

mwaa_resources := [
    rc |
    some rc in resources
    rc.type == "aws_mwaa_environment"
    rc.change.actions[_] != "delete"
]

deny contains msg if {
    some rc in mwaa_resources

    after := rc.change.after

    object.get(after, "webserver_access_mode", "") != "PRIVATE_ONLY"

    msg := sprintf(
        "%s must use PRIVATE_ONLY webserver access",
        [rc.address]
    )
}

deny contains msg if {
    some rc in mwaa_resources

    after := rc.change.after

    not after.logging_configuration

    msg := sprintf(
        "%s must configure CloudWatch logging",
        [rc.address]
    )
}

deny contains msg if {
    some rc in mwaa_resources

    after := rc.change.after

    not after.tags

    msg := sprintf(
        "%s must have resource tags",
        [rc.address]
    )
}
```

This is a starter policy. Validate it against your actual Terraform plan JSON and adjust for your provider version and organisational rules.

### Run OPA

```bash
terraform plan -out=tfplan

terraform show -json tfplan > tfplan.json

opa eval \
  --data policy/mwaa.rego \
  --input tfplan.json \
  "data.terraform.mwaa.deny"
```

If the policy returns a denial message, investigate and correct the configuration before deployment.

An empty denial result only means these particular policies passed. It is not a complete security certification.

## 47. Production policy checklist

| Policy | Required control |
|---|---|
| Webserver | Private access for designated production environments |
| S3 | Public access blocked |
| S3 encryption | Encryption enabled |
| S3 transport | HTTPS enforced |
| Logging | Task and scheduler logging enabled |
| IAM | No unnecessary administrative permissions |
| Network | Approved private subnets |
| Security group | Required MWAA communication only |
| Tags | Environment, Owner, Application, CostCenter |
| Airflow version | Approved and supported release |
| Dependencies | Version-pinned and reviewed |
| Worker scaling | Approved minimum and maximum |
| Secrets | No hardcoded credentials |
| Deployment | Terraform plan and policy checks required |

## 48. CI/CD pipeline

```text
Developer pushes DAG and Terraform
                |
                v
             Git PR
                |
                v
         Python linting
                |
                v
         DAG validation
                |
                v
         terraform fmt
                |
                v
         terraform validate
                |
                v
          Checkov scan
                |
                v
         Terraform plan
                |
                v
        OPA / Conftest
                |
                v
         Security approval
                |
                v
        Terraform apply
                |
                v
          Upload DAGs
                |
                v
          MWAA testing
```

Production deployment should stop if mandatory checks fail.

---

# PART 17 — MONITORING AND TROUBLESHOOTING

## 49. What should you monitor?

| Metric or signal | What it tells you |
|---|---|
| DAG run success | Whether workflows complete |
| DAG run failure | Whether workflows fail |
| Task duration | Slow tasks |
| Task retries | Unstable integrations |
| Scheduler heartbeat | Scheduler health |
| DAG parsing errors | Invalid DAG files |
| Worker utilisation | Worker capacity |
| Queue backlog | Tasks waiting to execute |
| Triggerer health | Deferred-task processing |
| Metadata DB usage | Metadata growth |
| CloudWatch task logs | Individual task errors |
| Glue job metrics | ETL processing health |
| S3 output checks | Data delivery correctness |

## 50. Common errors

| Problem | Possible reason | Solution |
|---|---|---|
| DAG not visible | Python syntax or import error | Check DAG processing logs |
| Task stuck queued | Worker capacity or executor issue | Check workers and queue |
| Task fails with AccessDenied | Missing IAM permission | Review MWAA execution role |
| Glue job fails | Glue role or job configuration issue | Check Glue logs and IAM |
| S3 sensor times out | Wrong key or missing file | Check bucket and object path |
| DAG runs multiple times | Catchup or concurrency configuration | Review schedule and catchup |
| XCom too large | Passing large datasets | Pass S3 references instead |
| MWAA creation fails | Network configuration problem | Check subnets, routes, security group and endpoints |
| Requirements fail | Incompatible Python/provider version | Pin compatible dependencies |
| Slow scheduling | Too many DAGs or heavy DAG parsing | Simplify DAG imports and parsing |
| High cost | Too many workers or large environment | Review autoscaling and class |
| UI inaccessible | Private access or IAM authorisation | Check VPN, routing and IAM |

---

# PART 18 — PRODUCTION CHECKLIST

## 51. Before going live

### Airflow configuration

- [ ] DAG IDs are unique.
- [ ] DAG start dates are fixed and timezone-aware.
- [ ] Scheduling and data intervals are correct.
- [ ] Catchup behaviour is intentional.
- [ ] DAG and task concurrency are configured.
- [ ] Task timeouts are configured.
- [ ] Retry policies are bounded.
- [ ] Trigger rules are correct.
- [ ] Sensors use efficient waiting modes.
- [ ] XCom carries only small metadata.
- [ ] Large datasets are stored externally.

### MWAA infrastructure

- [ ] Supported Airflow version selected.
- [ ] Correct environment class selected.
- [ ] Two private subnets configured.
- [ ] Security group configured.
- [ ] Required VPC endpoints or egress connectivity configured.
- [ ] Private webserver access configured where required.
- [ ] IAM execution role reviewed.
- [ ] S3 DAG bucket encrypted.
- [ ] S3 versioning enabled.
- [ ] S3 public access blocked.
- [ ] CloudWatch logs enabled.
- [ ] Log retention configured.
- [ ] Worker scaling configured.
- [ ] Tags applied.

### Data engineering

- [ ] Input file checks implemented.
- [ ] Data quality validation implemented.
- [ ] Glue jobs are idempotent.
- [ ] Failed runs do not publish success markers.
- [ ] Backfill procedure tested.
- [ ] Duplicate processing considered.
- [ ] Output locations are deterministic.
- [ ] Data lineage and ownership documented.

### Governance

- [ ] Checkov scan passed.
- [ ] OPA policy passed.
- [ ] IAM least privilege reviewed.
- [ ] Dependencies pinned.
- [ ] Secrets are not hardcoded.
- [ ] Deployment approval enabled.
- [ ] Rollback process tested.
- [ ] Cost monitoring enabled.

---

# PART 19 — INTERVIEW QUESTIONS

## 52. Common Apache Airflow questions

**Q1. What is Apache Airflow?**

Apache Airflow is a workflow orchestration platform used to schedule, execute and monitor workflows defined as DAGs.

**Q2. What is a DAG?**

A Directed Acyclic Graph is the definition of a workflow, including its tasks, dependencies and schedule.

**Q3. What is an operator?**

An operator defines the work a task performs, such as running Python, executing SQL or invoking AWS Glue.

**Q4. What is a sensor?**

A sensor waits for an external condition, such as an S3 file or another DAG's completion.

**Q5. What is XCom?**

XCom is a mechanism for passing small values between tasks.

**Q6. What is the difference between an operator and a sensor?**

An operator performs work. A sensor waits for a condition to become true.

**Q7. What is catchup?**

Catchup controls whether Airflow creates DAG runs for historical data intervals that were missed.

**Q8. What is a trigger rule?**

It determines when a task can execute based on the status of upstream tasks.

**Q9. What is TaskFlow?**

TaskFlow is a Python decorator-based API for creating tasks and dependencies more simply.

**Q10. What is dynamic task mapping?**

It creates task instances dynamically from runtime input, such as a list of S3 files.

**Q11. What is the difference between poke and reschedule mode?**

Poke mode occupies a worker while waiting. Reschedule mode releases the worker between checks.

**Q12. What is a deferrable operator?**

An operator that can suspend waiting work and hand it to the Triggerer, freeing worker capacity.

**Q13. How do you pass large data between tasks?**

Store the data in S3 or another external system and pass a small reference through XCom.

**Q14. How do you prevent duplicate processing?**

Design tasks to be idempotent, use stable data partitions or idempotency keys, and ensure retries do not create duplicate side effects.

## 53. AWS MWAA questions

**Q15. What is MWAA?**

Amazon Managed Workflows for Apache Airflow is AWS's managed service for running Apache Airflow.

**Q16. Where are DAG files stored in MWAA?**

In an S3 source bucket configured for the environment.

**Q17. How does MWAA access AWS services?**

Through its IAM execution role and the required network connectivity.

**Q18. How do you deploy DAGs?**

Upload DAG files to the configured S3 DAG folder, usually through CI/CD.

**Q19. How do you secure the Airflow UI?**

Use private webserver access where appropriate, IAM controls and approved network access.

**Q20. How do you scale MWAA?**

Select an appropriate environment class and configure supported worker, scheduler and webserver capacity.

**Q21. How do you monitor MWAA?**

Use the Airflow UI, CloudWatch logs and metrics, plus monitoring for downstream services.

**Q22. How is MWAA charged?**

By environment usage, additional worker/scheduler/webserver usage and metadata database storage, plus supporting AWS services.

**Q23. What does the MWAA execution role do?**

It allows MWAA and its workflows to access the AWS resources required by the environment.

**Q24. How do you deploy MWAA with Terraform?**

Use `aws_mwaa_environment` along with IAM, S3, networking, logging and supporting infrastructure resources.

---

# PART 20 — QUICK REVISION

| Topic | Remember |
|---|---|
| Service | Apache Airflow |
| AWS managed service | Amazon MWAA |
| Workflow | DAG |
| Task implementation | Operator |
| Wait for event | Sensor |
| Task data exchange | XCom |
| Scheduling | `schedule` |
| Historical runs | `catchup` |
| Retry | `retries`, `retry_delay` |
| Timeout | `execution_timeout` |
| Conditional execution | Branch operator |
| Parallel processing | Dynamic task mapping |
| AWS deployment | `aws_mwaa_environment` |
| DAG storage | S3 |
| Permissions | IAM execution role |
| Monitoring | CloudWatch |
| Networking | VPC, private subnets, security groups and endpoints |
| Encryption | S3 encryption and KMS where required |
| Policy as Code | Checkov, OPA, Conftest |
| Main production concern | Reliability, idempotency, concurrency and observability |

---

# PART 21 — OFFICIAL DOCUMENTATION

1. Apache Airflow documentation: https://airflow.apache.org/docs/apache-airflow/stable/
2. DAG concepts: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html
3. TaskFlow API: https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html
4. Operators: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/operators.html
5. Sensors: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/sensors.html
6. XCom: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html
7. AWS MWAA documentation: https://docs.aws.amazon.com/mwaa/latest/userguide/
8. AWS MWAA networking: https://docs.aws.amazon.com/mwaa/latest/userguide/networking.html
9. AWS MWAA execution role: https://docs.aws.amazon.com/mwaa/latest/userguide/mwaa-create-role.html
10. AWS MWAA pricing: https://aws.amazon.com/managed-workflows-for-apache-airflow/pricing/
11. Terraform MWAA resource: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/mwaa_environment

**Final architecture principle:**

Use Airflow/MWAA to orchestrate workflows, Glue or other compute services to process data, S3 to store datasets, IAM to control access, CloudWatch to monitor execution, and Terraform plus Policy as Code to govern infrastructure deployment.
