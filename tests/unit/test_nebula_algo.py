import sys
from unittest.mock import MagicMock

import pytest
from pyspark.sql import SparkSession

from ng_ai import NebulaGraphConfig
from ng_ai.engines import SparkEngine
from ng_ai.nebula_algo import NebulaDataFrameAlgorithm
from ng_ai.nebula_data import NebulaDataFrameObject


# Pytest fixture to create a SparkSession instance
@pytest.fixture(scope="session")
def spark():
    spark = (
        SparkSession.builder.master("local[1]")
        .config("spark.port.maxRetries", "1000")
        .config("spark.sql.shuffle.partitions", "1")
        .getOrCreate()
    )
    return spark


# Pytest fixture to create a sample Spark DataFrame
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


def test_algo_dot_call_spark_engine(spark_df):
    config = NebulaGraphConfig()
    spark_engine = SparkEngine(config=config)
    nebula_df = NebulaDataFrameObject(engine=spark_engine, data=spark_df)

    mock_pagerank = MagicMock()
    NebulaDataFrameAlgorithm.pagerank = mock_pagerank

    nebula_df.algo.pagerank(reset_prob=0.15, max_iter=10)

    mock_pagerank.assert_called_once_with(reset_prob=0.15, max_iter=10)
