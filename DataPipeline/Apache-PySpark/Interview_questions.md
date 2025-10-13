Q1. What is PySpark and how is it different from Pandas?
PySpark = Python API for Apache Spark, a distributed data processing engine.
Differences from Pandas:
| Feature         | Pandas          | PySpark                             |
| --------------- | --------------- | ----------------------------------- |
| Data size       | Fits in memory  | Distributed, can handle TBs of data |
| Parallelism     | Single-threaded | Multi-node parallel execution       |
| Lazy evaluation | No              | Yes                                 |
| API             | Python only     | Python, Scala, Java, R              |

Q2. What are the main data abstractions in PySpark?
RDD (Resilient Distributed Dataset): Low-level distributed collection, immutable
DataFrame: High-level, schema-based, optimized
Dataset (Scala/Java only): Type-safe version of DataFrame
Spark SQL: SQL queries on DataFrames

Q3. What is lazy evaluation in Spark and why is it important?
Transformations (filter, map, select) do not execute immediately.
Actions (show, count, write) trigger execution.
Benefits: optimized DAG execution, reduced I/O, efficient parallelism.

Q4. How do you read data from S3 in PySpark?
.option("header", True).csv("s3a://bucket/path/file.csv")

Q5. What is the difference between select and withColumn in PySpark?
select: choose columns or create expressions; returns a new DataFrame
withColumn: add or replace a column in the DataFrame

Q6. How do you handle missing/null data in PySpark?
# Drop rows with null values in specific columns
```python
df.dropna(subset=['col1', 'col2'])

# Fill null values with defaults
df.fillna({'col1': 0, 'col2': 'unknown'})
```
Q7. How do you add a new column with conditional logic?
from pyspark.sql.functions import when, col
```python
df = df.withColumn(
    "age_group",
    when(col("age") < 30, "Young")
    .when(col("age") < 60, "Adult")
    .otherwise("Senior")
)
```



