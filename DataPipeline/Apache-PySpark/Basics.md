## PySpark
• PySpark is the Python API for Apache Spark.  
• It allows you to use Python to write Spark applications.  
• Apache Spark is a distributed computing framework for big data processing and analytics.  
• PySpark enables large-scale data processing across multiple machines (clusters).  
• It provides high-level APIs for DataFrames, SQL, streaming, and machine learning (MLlib).  
• It combines Python’s simplicity with Spark’s speed and scalability.  
• Commonly used for ETL, data analytics, and big data machine learning tasks.

## Apache Spark architecture (how PySpark works internally).
• Apache Spark follows a master–slave architecture with a Driver and Executors.  
• The **Driver** program runs the main control flow — it creates the SparkSession, builds the logical plan, and sends tasks to Executors.  
• **Executors** are worker processes running on cluster nodes — they execute the tasks assigned by the Driver.  
• Data in Spark is distributed across Executors in partitions (chunks of data).  
• Spark performs transformations lazily — it builds a Directed Acyclic Graph (DAG) of execution.  
• When an action (like show(), count(), or write()) is called, Spark’s scheduler optimizes and executes the DAG on the cluster.  
• The **Cluster Manager** (like YARN, Kubernetes, or Spark Standalone) allocates resources (CPU, memory) to the Driver and Executors.  
• PySpark communicates with the JVM-based Spark engine through the Py4J library — letting Python commands run on the JVM backend.  
• This architecture makes Spark fast, fault-tolerant, and scalable for large datasets.

## key components of PySpark
• **SparkSession** – The entry point to any PySpark program. 
                     It allows you to create DataFrames, run SQL queries, and manage Spark configurations.
• **SparkContext** – The core connection to the Spark cluster. 
                    It manages the communication between your application and the cluster. (SparkSession internally creates it.)
• **RDD (Resilient Distributed Dataset)** – The low-level data structure in Spark. 
                                            It represents an immutable, distributed collection of data across nodes in a cluster.
• **DataFrame** – A distributed collection of data organized into named columns (like a SQL table). 
                  It’s built on top of RDDs and provides high-level operations.
• **Dataset** – A strongly-typed distributed data structure (mainly used in Scala/Java). 
                In PySpark, DataFrames are used instead.
• **Transformations** – Lazy operations (like filter, map, select) that describe how data should be modified but don’t execute immediately.
• **Actions** – Operations (like show, count, collect, write) that trigger the actual computation and return a result.
• **Spark SQL** – A module that lets you query structured data using SQL syntax on top of DataFrames.
• **PySpark Streaming** – A module to process real-time data streams (for example, data from Kafka or sockets).
• **MLlib** – Spark’s machine learning library for scalable ML algorithms (classification, regression, clustering, etc.).
• **GraphX / GraphFrames** – Used for graph-based computations (e.g., PageRank, social network analysis).
• **Cluster Manager** – Allocates resources and manages nodes (examples: YARN, Kubernetes, or Spark Standalone).

<img width="887" height="391" alt="image" src="https://github.com/user-attachments/assets/67ca4bbd-00c3-4791-bcff-f4c829c0c13e" />





