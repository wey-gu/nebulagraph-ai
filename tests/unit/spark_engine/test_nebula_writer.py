from unittest.mock import Mock, patch

import pytest
from pyspark.sql import SparkSession

from ng_ai.config import NebulaGraphConfig
from ng_ai.nebula_writer import NebulaWriter, NebulaWriterWithSpark


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
    df = spark.createDataFrame(data, ["_srcId", "_dstId", "_rank", "degree"])
    return df


# TBD, need to test writer with data: NebulaDataFrameObject
# @pytest.fixture
# def nebula_writer_with_spark_nebula_df():
#     config = NebulaGraphConfig()
#     spark_engine = SparkEngine(config=config)
#     data = NebulaDataFrameObject(engine=spark_engine, data=spark_df)
#     return NebulaWriter(data, "nebulagraph_vertex", config=config, engine="spark")


@pytest.fixture
def nebula_writer_with_spark_jdf(spark_df):
    config = NebulaGraphConfig()
    data = spark_df._jdf
    return NebulaWriter(data, "nebulagraph_vertex", config=config, engine="spark")


def test_nebula_writer_init(spark_df):
    config = NebulaGraphConfig()
    data = spark_df._jdf
    writer = NebulaWriter(data, "nebulagraph_vertex", config=config, engine="spark")

    assert isinstance(writer, NebulaWriter)
    assert isinstance(writer.writer, NebulaWriterWithSpark)
    assert writer.jdf is not None


@patch("ng_ai.nebula_writer.NebulaWriterWithSpark._get_raw_df_writer_with_nebula")
def test_set_options_with_nebula(mock_get_raw_df_writer, nebula_writer_with_spark_jdf):
    mock_raw_df_writer = Mock()
    mock_get_raw_df_writer.return_value = mock_raw_df_writer

    properties = {"lpa": "cluster_id"}

    kwargs = {
        "space": "basketballplayer",
        "type": "vertex",
        "tag": "person",
        "write_mode": "insert",
        "batch": 128,
        "vid_policy": "",
        "vid_field": "id",
        "properties": properties,
    }
    nebula_writer_with_spark_jdf.set_options(**kwargs)

    assert mock_get_raw_df_writer.called
    assert mock_raw_df_writer.option.called
    assert mock_raw_df_writer.option.call_count == 11


@patch("ng_ai.nebula_writer.NebulaWriterWithSpark._get_raw_df_writer_with_nebula")
def test_write(mock_get_raw_df_writer, nebula_writer_with_spark_jdf):
    mock_raw_df_writer = Mock()
    mock_get_raw_df_writer.return_value = mock_raw_df_writer

    # set up options for writing
    properties = {"lpa": "cluster_id"}

    kwargs = {
        "space": "basketballplayer",
        "type": "vertex",
        "tag": "person",
        "write_mode": "insert",
        "batch": 128,
        "vid_policy": "",
        "vid_field": "id",
        "properties": properties,
    }

    nebula_writer_with_spark_jdf.set_options(**kwargs)

    with patch.object(mock_raw_df_writer, "save") as mock_save:
        nebula_writer_with_spark_jdf.write()
        assert mock_save.called
