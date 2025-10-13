## Step 1: Install and Set Up PySpark
pip install pyspark

Verify installation:
python -c "import pyspark; print(pyspark.__version__)"

Option 2: Run in Jupyter Notebook
pip install pyspark notebook

jupyter notebook

# Create Your First Spark Session
Step 1. Everything in PySpark starts with a SparkSession — the entry point for Spark functionality.

``` python 
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyFirstSparkApp") \
    .master("local[*]") \
    .getOrCreate()

print("Spark is ready!")
```
> .appName() — name of your app (appears in Spark UI)

> .master("local[*]") — run locally using all CPU cores
(In AWS Glue or EMR, Spark manages this automatically)

Step 2: Load Data into a DataFrame
> PySpark reads data from many sources: CSV, JSON, Parquet, S3, JDBC, etc.

```python
df = spark.read \
    .csv("employees.csv")\
    .option("header", True) \
    .option("inferSchema", True) 
   
df.show() or df.dispaly
```
