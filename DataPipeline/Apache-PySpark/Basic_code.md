## Step 1: Install and Set Up PySpark
pip install pyspark

Verify installation:
python -c "import pyspark; print(pyspark.__version__)"

Option 2: Run in Jupyter Notebook
pip install pyspark notebook

jupyter notebook

# Create Your First Spark Session
Everything in PySpark starts with a SparkSession — the entry point for Spark functionality.

``` python 
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyFirstSparkApp") \
    .master("local[*]") \
    .getOrCreate()

print("Spark is ready!")

```
