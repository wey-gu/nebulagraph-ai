from unittest.mock import Mock

import pytest

from ng_ai.config import NebulaGraphConfig
from ng_ai.engines import SparkEngine
from ng_ai.nebula_data import NebulaDataFrameObject
from ng_ai.nebula_reader import NebulaReader, NebulaReaderWithSpark


@pytest.fixture
def nebula_reader_with_spark():
    config = NebulaGraphConfig()
    return NebulaReaderWithSpark(config=config)


def test_nebula_reader_init():
    config = NebulaGraphConfig()
    reader = NebulaReader(engine="spark", config=config)

    assert isinstance(reader, NebulaReader)
    assert isinstance(reader.reader, NebulaReaderWithSpark)


def test_scan(nebula_reader_with_spark):
    kwargs = {"edge": "follow", "props": "degree"}

    nebula_reader_with_spark.scan(**kwargs)

    assert nebula_reader_with_spark.raw_df_reader is not None
    assert isinstance(nebula_reader_with_spark.engine, SparkEngine)

    spark = nebula_reader_with_spark.engine.spark
    assert spark is not None


def test_query(nebula_reader_with_spark):
    kwargs = {
        "query": "MATCH ()-[e:follow]->() RETURN e LIMIT 100000",
        "edge": "follow",
        "props": "degree",
    }

    nebula_reader_with_spark.query(**kwargs)

    assert nebula_reader_with_spark.raw_df_reader is not None
    assert isinstance(nebula_reader_with_spark.engine, SparkEngine)

    spark = nebula_reader_with_spark.engine.spark
    assert spark is not None


def test_read(nebula_reader_with_spark):
    data = [[1, "foo"], [2, "bar"]]
    mock_raw_df_reader = Mock()
    mock_raw_df_reader.load.return_value = data
    nebula_reader_with_spark.raw_df_reader = mock_raw_df_reader

    result = nebula_reader_with_spark.read()

    assert mock_raw_df_reader.load.called
    assert isinstance(result, NebulaDataFrameObject)
    assert nebula_reader_with_spark.raw_df == data
