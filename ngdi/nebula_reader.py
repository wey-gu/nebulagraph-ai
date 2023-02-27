# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The NebulaGraph Authors. All rights reserved.
from __future__ import annotations

from ngdi.config import NebulaGraphConfig
from ngdi.nebula_data import NebulaDataFrameObject


class NebulaReaderBase(object):
    def __init__(self, engine=None, config=None, **kwargs):
        self.engine_type = engine
        self.config = config

    def scan(self, **kwargs):
        raise NotImplementedError

    def query(self, **kwargs):
        raise NotImplementedError

    def load(self, **kwargs):
        raise NotImplementedError

    def read(self, **kwargs):
        raise NotImplementedError

    def show(self, **kwargs):
        raise NotImplementedError


class NebulaReader:
    def __init__(self, engine="spark", config=NebulaGraphConfig(), **kwargs):
        if self.engine_type == "spark":
            self.reader = NebulaReaderWithSpark(config, **kwargs)
        elif self.engine_type == "nebula":
            self.reader = NebulaReaderWithGraph(config, **kwargs)
        else:
            raise NotImplementedError

    def __getattr__(self, name):
        return getattr(self.reader, name)

    def scan(self, **kwargs):
        raise NotImplementedError


class NebulaReaderWithGraph(NebulaReaderBase):
    def __init__(self, config: NebulaGraphConfig, **kwargs):
        super().__init__("nebula", config, **kwargs)
        from ngdi.engines import NebulaEngine

        self.engine = NebulaEngine(config)
        self.raw_df = None
        self.df = None

    def scan(self, **kwargs):
        # Implement the scan method specific to Nebula engine
        raise NotImplementedError

    def query(self, **kwargs):
        # Implement the query method specific to Nebula engine
        raise NotImplementedError

    def load(self, **kwargs):
        # Implement the load method specific to Nebula engine
        raise NotImplementedError

    def read(self, **kwargs):
        # Implement the read method specific to Nebula engine
        raise NotImplementedError

    def show(self, **kwargs):
        # Implement the show method specific to Nebula engine
        raise NotImplementedError


class NebulaReaderWithSpark(NebulaReaderBase):
    def __init__(self, config: NebulaGraphConfig, **kwargs):
        super().__init__("spark", config, **kwargs)
        from ngdi.engines import SparkEngine

        self.engine = SparkEngine(config)
        self.raw_df = None
        self.df = None

    def scan(self, **kwargs):
        """
        example:
        df = spark.read.format(
        "com.vesoft.nebula.connector.NebulaDataSource").option(
            "type", "edge").option(
            "spaceName", "basketballplayer").option(
            "label", "follow").option(
            "returnCols", "degree").option(
            "metaAddress", "metad0:9559").option(
            "partitionNumber", 3).load()
        """

        # validate kwargs, there should be:
        # - edge: edge type, string
        # - props: properties to be returned, string

        assert "edge" in kwargs, "edge type should be specified"
        assert "props" in kwargs, "properties to be returned should be specified"

        # validate config, there should be:
        # - metad_hosts: meta server address, string
        # - space: space name, string
        assert self.config.metad_hosts, "metad_hosts should be specified"
        assert self.config.space, "space should be specified"
        edge_type = kwargs["edge"]
        props = kwargs["props"]
        partition_number = kwargs.get("partition_number", 3)  # default 3

        space_name = self.config.space
        metad_hosts = self.config.metad_hosts

        spark = self.engine.spark
        datasource_format = self.engine.nebula_spark_ds

        self.raw_df = (
            spark.read.format(datasource_format)
            .option("type", "edge")
            .option("spaceName", space_name)
            .option("label", edge_type)
            .option("returnCols", props)
            .option("metaAddress", metad_hosts)
            .option("partitionNumber", partition_number)
        )

    def query(self, query=None, **kwargs):
        # Implement the query method specific to Spark engine
        """
        df = spark.read.format(
        "com.vesoft.nebula.connector.NebulaDataSource").option(
            "type", "edge").option(
            "spaceName", "basketballplayer").option(
            "label", "follow").option(
            "returnCols", "degree").option(
            "metaAddress", "metad0:9559").option(
            "graphAddress", "graphd:9669").option(
            "ngql", "MATCH ()-[e:follow]->() return e LIMIT 1000").option(
            "partitionNumber", 1).load()
        """

        # validate kwargs, there should be:
        # - edge: edge type, string
        # - props: properties to be returned, string
        # - ngql: ngql to be executed, string

        assert "edge" in kwargs, "edge type should be specified"
        assert "props" in kwargs, "properties to be returned should be specified"
        assert query is not None, "ngql should be specified"

        # validate config, there should be:
        # - metad_hosts: meta server address, string
        # - space: space name, string
        # - graphd_hosts: graph server address, string
        assert self.config.metad_hosts, "metad_hosts should be specified"
        assert self.config.space, "space should be specified"
        assert self.config.graphd_hosts, "graphd_hosts should be specified"
        edge_type = kwargs["edge"]
        props = kwargs["props"]

        space_name = self.config.space
        metad_hosts = self.config.metad_hosts
        graphd_hosts = self.config.graphd_hosts

        spark = self.engine.spark
        datasource_format = self.engine.nebula_spark_ds

        self.raw_df = (
            spark.read.format(datasource_format)
            .option("type", "edge")
            .option("spaceName", space_name)
            .option("label", edge_type)
            .option("returnCols", props)
            .option("metaAddress", metad_hosts)
            .option("graphAddress", graphd_hosts)
            .option("ngql", query)
            .option("partitionNumber", 1)
        )

    def load(self, **kwargs):
        # Implement the load method specific to Spark engine
        raise NotImplementedError

    def read(self, **kwargs):
        # Check self.raw_df, if it is None, raise exception
        if self.raw_df is None:
            raise Exception("No data loaded, please use scan or query first")
        self.raw_df.load()
        self.df = NebulaDataFrameObject(engine=self.engine, data=self.raw_df)
        return self.df

    def show(self, **kwargs):
        # Implement the show method specific to Spark engine
        raise NotImplementedError
