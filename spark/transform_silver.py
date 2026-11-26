from pyspark.sql import SparkSession
from pyspark.sql.types import DecimalType
from pyspark.sql.functions import col, try_to_date

spark = (
    SparkSession.builder.appName("transform_silver")
    .master("local[*]")
    .getOrCreate()
)

try:
    df_bronze = (
        spark.read
        .option("multiLine", True)
        .json('./data/raw/despesas_209787_2024.json')
    )

    df_silver = (
        df_bronze
        .select("dataDocumento", "nomeFornecedor", "valorLiquido", "tipoDespesa")
        .withColumn("valorLiquido", col("valorLiquido").cast(DecimalType(10, 2)))
        .withColumn("dataDocumento", try_to_date(col("dataDocumento"), "yyyy-MM-dd'T'HH:mm:ss"))
        .dropDuplicates(["dataDocumento", "nomeFornecedor", "valorLiquido"])
    )

    df_silver.printSchema()
    df_teste = df_silver.where(col("dataDocumento").isNull())

    print(f"Contagem de datas nulas: {df_teste.count()}")

    print(f"Total de registros na camada Bronze: {df_bronze.count()}")
    print(f"Total de registros na camada Silver: {df_silver.count()}")

    df_silver.write.mode("overwrite").parquet("./data/silver/despesas")
    

finally:
    spark.stop()