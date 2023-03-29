import sys

import pytest
from chispa.dataframe_comparer import assert_df_equality
from pyspark.sql import SparkSession

from ng_ai.config import NebulaGraphConfig
from ng_ai.engines import SparkEngine
from ng_ai.nebula_data import NebulaDataFrameObject, NebulaGraphObject


@pytest.fixture(scope="session")
def spark():
    spark = (
        SparkSession.builder.master("local[1]")
        .config("spark.port.maxRetries", "1000")
        .config("spark.sql.shuffle.partitions", "1")
        .getOrCreate()
    )
    return spark


@pytest.fixture(scope="session")
def spark_df(spark):
    """
    +---------+---------+-----+------+
    |   _srcId|   _dstId|_rank|degree|
    +---------+---------+-----+------+
    |player105|player100|    0|    70|
    |player105|player104|    0|    83|
    +---------+---------+-----+------+
    """
    data = [
        ("player105", "player100", 0, 70),
        ("player105", "player104", 0, 83),
    ]

    # spark engine can only be tested in python 3.9 or lower
    assert sys.version_info < (
        3,
        10,
    ), "spark engine can only be tested in python 3.9 or lower"
    df = spark.createDataFrame(data, ["_srcId", "_dstId", "_rank", "degree"])
    return df


def test_nebula_data_frame_object(spark_df):
    config = NebulaGraphConfig()
    spark_engine = SparkEngine(config=config)
    nebula_df = NebulaDataFrameObject(engine=spark_engine, data=spark_df)
    assert nebula_df.get_engine().type == "spark"
    assert_df_equality(nebula_df.data, spark_df)
