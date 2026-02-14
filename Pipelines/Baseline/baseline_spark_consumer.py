from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("BaselineSinglePipeline") \
    .getOrCreate()

schema = StructType([
    StructField("timestamp", StringType()),
    StructField("vibration", DoubleType()),
    StructField("temperature", DoubleType()),
    StructField("pressure", DoubleType()),
    StructField("rms_vibration", DoubleType()),
    StructField("mean_temperature", DoubleType()),
    StructField("fault_label", IntegerType()),
    StructField("event_timestamp", DoubleType())
])

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "base_data") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()


parsed_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

query = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("checkpointLocation", "/tmp/baseline_checkpoint") \
    .start()


query.awaitTermination()
