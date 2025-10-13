## Step 1: Install and Set Up PySpark
pip install pyspark

Verify installation:
python -c "import pyspark; print(pyspark.__version__)"

Option 2: Run in Jupyter Notebook
pip install pyspark notebook

jupyter notebook

**Data**
employees.csv
id,name,age,department,salary
1,Alice,30,Engineering,120000
2,Bob,22,Marketing,65000
3,Carol,45,Engineering,150000
4,Dan,17,Intern,20000
5,Eve,35,Product,110000

# Create Your First Spark Session
**Step 1. Everything in PySpark starts with a SparkSession — the entry point for Spark functionality.**
``` python 
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyFirstSparkApp") \
    .master("local[*]") \
    .getOrCreate()

print("Spark is ready!")
```
**> .appName() — name of your app (appears in Spark UI)**

**> .master("local[*]") — run locally using all CPU cores
(In AWS Glue or EMR, Spark manages this automatically)**

**Step 2: Load Data into a DataFrame**
> PySpark reads data from many sources: CSV, JSON, Parquet, S3, JDBC, etc.

```python
df = spark.read \
    .csv("employees.csv")\
    .option("header", True) \
    .option("inferSchema", True) 
   
df.show() or df.dispaly
```
**Basic Transformations**
**1. Filtering rows**
``` python
adults = df.filter(df.age >= 18)
adults.show()
```

**2. Selecting columns**
``` python
adults.select("name", "department").show()
```
**3. Adding new columns**
``` python
from pyspark.sql.functions import when, col

df2 = adults.withColumn(
    "seniority",
    when(col("age") >= 40, "Senior")
    .when(col("age") >= 25, "Mid")
    .otherwise("Junior")
)
df2.show()

```
🧠 SUMMARY
• withColumn() → Creates or updates a column.
• col() → References a column.
• when() → Applies conditional logic.
• otherwise() → Defines the default case.
• show() → Executes and displays results.
This code adds a new column "seniority" based on the employee’s age category (Senior, Mid, or Junior).

**4. Renaming columns**
``` python
df2 = df2.withColumnRenamed("salary", "annual_salary")
```
**Step 5: Transformations vs Actions**
This is key to understanding Spark.
Transformations → Create a new DataFrame (lazy)
e.g. .filter(), .select(), .withColumn()
Actions → Trigger computation
e.g. .show(), .count(), .collect(), .write()
``` python
transformed = df.filter(df.age >= 18)    # Transformation (lazy)
print(transformed.count())     # Action (triggers job)
```
**Step 6: Aggregations
Example: Find average salary by department.**
``` python
from pyspark.sql.functions import avg

avg_salary = df.groupBy("department").agg(avg("salary").alias("avg_salary"))
avg_salary.show()

```
op
+------------+-----------+
| department | avg_salary|
+------------+-----------+
| Engineering| 135000.0  |
| Marketing  | 65000.0   |
| Product    | 110000.0  |
| Intern     | 20000.0   |
+------------+-----------+

**Step 7: Joins**
Create another DataFrame for departments.
``` python
dept = spark.createDataFrame([
    ("Engineering", "ENG"),
    ("Marketing", "MKT"),
    ("Product", "PRD"),
    ("Intern", "INT")
], ["department", "dept_code"])

joined = df.join(dept, on="department", how="left")
joined.show()
```
op
+------------+---+-----+---+------+---------+
| department | id| name|age|salary|dept_code|
+------------+---+-----+---+------+---------+
| Engineering| 1 |Alice| 30|120000| ENG     |
| Marketing  | 2 | Bob | 22| 65000| MKT     |
| Engineering| 3 |Carol| 45|150000| ENG     |
| Intern     | 4 | Dan | 17| 20000| INT     |
| Product    | 5 | Eve | 35|110000| PRD     |
+------------+---+-----+---+------+---------+

**Step 8: SQL in PySpark**
You can use SQL syntax directly on DataFrames.
```python
df.createOrReplaceTempView("employees")

result = spark.sql("""
SELECT department, COUNT(*) as count, AVG(salary) as avg_salary
FROM employees
WHERE age >= 18
GROUP BY department
""")

result.show()
```

**Step 9: Writing Data (e.g. to S3 or local)**
Write output to CSV or Parquet.
```python
df2.write.mode("overwrite").parquet("output/employee_data/")
```

**In AWS Glue or EMR, this same command can write to S3:**
Write output to CSV or Parquet.
```python
df2.write.mode("overwrite").parquet("s3://my-bucket/processed/employees/")
```

**Step 10: Stop the Spark Session**
Always end your session.
```python
spark.stop()
```
***Final example**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, year, avg

# 1️⃣ Create Spark session
spark = SparkSession.builder \
    .appName("ETL_S3_to_S3_Redshift") \
    .getOrCreate()

# 2️⃣ Define input and output locations
input_path = "s3a://my-bucket/raw/employees.csv"
output_path = "s3a://my-bucket/processed/employees/"

# 3️⃣ Read data from S3 (CSV)
df = spark.read.option("header", True).option("inferSchema", True).csv(input_path)

print("=== Raw Data ===")
df.show()

# 4️⃣ Data Cleaning
# Remove rows with missing essential fields
df_clean = df.dropna(subset=["id", "name", "department", "salary"])

# Filter valid age (>= 18)
df_clean = df_clean.filter(col("age") >= 18)

# 5️⃣ Data Transformation
# Add age group and tenure years
df_transformed = (
    df_clean
    .withColumn("age_group",
        when(col("age") < 30, "Young")
        .when(col("age") < 50, "Mid")
        .otherwise("Senior"))
    .withColumn("join_year", year(col("join_date")))
)

# 6️⃣ Aggregate (average salary per department)
avg_salary = (
    df_transformed.groupBy("department")
    .agg(avg("salary").alias("avg_salary"))
)

print("=== Aggregated Data ===")
avg_salary.show()

# 7️⃣ Write transformed data back to S3 (Parquet format, partitioned by department)
df_transformed.write \
    .mode("overwrite") \
    .partitionBy("department") \
    .parquet(output_path)

print("✅ Data successfully written to:", output_path)

# 8️⃣ Optional: Write aggregated data to Redshift
# -----------------------------------------------
# Uncomment if you have a Redshift cluster and JDBC connector configured
#
jdbc_url = "jdbc:redshift://<cluster-endpoint>:5439/dev"
redshift_table = "public.department_salary"
iam_role = "arn:aws:iam::<account-id>:role/MyRedshiftCopyRole"

 avg_salary.write \
     .format("jdbc") \
     .option("url", jdbc_url) \
     .option("dbtable", redshift_table) \
     .option("aws_iam_role", iam_role) \
     .mode("overwrite") \
     .save()

 print("✅ Aggregated data written to Redshift table:", redshift_table)

# 9️⃣ Stop the Spark session
spark.stop()
```

