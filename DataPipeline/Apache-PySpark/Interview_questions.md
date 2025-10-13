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
Q8. How do you compute the average salary per department?
```pyhton
from pyspark.sql.functions import avg
df.groupBy("department").agg(avg("salary").alias("avg_salary")).show()
```
Q9. What are window functions and why would you use them?
Window functions perform calculations across a subset of rows (partition) while retaining all rows.
Example: rank employees by salary within each department:

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, desc

window = Window.partitionBy("department").orderBy(desc("salary"))
df.withColumn("rank", row_number().over(window)).show()
```
Q10. How do you perform joins in PySpark (inner, left, right, outer)?
```python
df.join(df2, on="department", how="left")  # left, right, inner, outer
```
Q11. How do you optimize joins in Spark for performance?
Use broadcast joins for small tables:
```python
from pyspark.sql.functions import broadcast
df.join(broadcast(df_small), on="id")
```
Repartition large tables before joining to reduce skew
Avoid unnecessary wide transformations; prefer DataFrame API

Q12. How do you run SQL queries on a DataFrame?
```pyhton
df.createOrReplaceTempView("employees")
spark.sql("SELECT department, AVG(salary) FROM employees GROUP BY department").show()
```
Q13. What is a UDF and when would you use it in PySpark?
UDF = User Defined Function (custom logic not covered by built-in functions)
```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

def title_case(s):
    return s.title() if s else None

title_udf = udf(title_case, StringType())
df.withColumn("name_title", title_udf(col("name")))
```
Q14. What is the difference between RDD and DataFrame?
| Feature       | RDD                        | DataFrame                         |
| ------------- | -------------------------- | --------------------------------- |
| Schema        | No                         | Yes                               |
| Optimizations | Limited                    | Catalyst & Tungsten optimizations |
| API           | Functional (map, reduce)   | SQL-like, expressive              |
| Performance   | Slower for structured data | Faster                            |

Q15. Give a simple example of creating an RDD and performing a map operation.
```python
rdd = spark.sparkContext.parallelize([1, 2, 3, 4, 5])
squared = rdd.map(lambda x: x**2)
print(squared.collect())
```
Q16. How do you read a streaming source in PySpark?
```python
lines = spark.readStream.format("socket").option("host", "localhost").option("port", 9999).load()
```
Q17. How do you write streaming output to the console or S3?
```python
query = lines.writeStream.outputMode("append").format("console").start()
query.awaitTermination()
```
Q18. How do you read/write data from/to S3 in PySpark?
```python
# Read from S3
df = spark.read.csv("s3a://bucket/raw/file.csv")

# Write to S3 in Parquet
df.write.parquet("s3a://bucket/processed/output/")
```
Q19. How do you load data into Amazon Redshift using PySpark?
```pyhton
df.write.format("jdbc") \
  .option("url", "jdbc:redshift://host:5439/db") \
  .option("dbtable", "schema.table") \
  .option("user", "<username>") \
  .option("password", "<password>") \
  .mode("overwrite").save()
```
Q20. What is partitioning and why is it important?
Partitioning splits data into separate folders/files based on column values
Benefits: faster queries, reduced shuffle, optimized storage
```pyhton
df.write.partitionBy("department").parquet("s3a://bucket/processed/")
```
Q21. What are caching and persisting in PySpark? How are they used
```python
df.cache()  # store in memory for repeated access
df.persist(StorageLevel.DISK_ONLY)  # store on disk or memory/disk
```
Reduces repeated computation for expensive transformations

Q22. What are broadcast joins and why are they used?
Broadcast joins send a small table to all executors, avoiding shuffling a large table.
Use for small dimension tables in joins to optimize performance.

Q23. How do you debug or optimize slow PySpark jobs?
Use Spark UI to inspect DAG, stages, and tasks
Use .explain() to check the physical plan
Avoid unnecessary wide transformations and small file issues
Repartition large DataFrames and cache intermediate results


