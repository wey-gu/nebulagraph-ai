# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The NebulaGraph Authors. All rights reserved.
from __future__ import annotations

from ng_ai.config import NebulaGraphConfig
from ng_ai.nebula_data import NebulaDataFrameObject

SPARK_NEBULA_SINKS = ["nebulagraph_vertex", "nebulagraph_edge"]
SPARK_FILE_SINKS = ["csv", "json", "parquet"]
SPARK_SERVER_SINKS = []
SPARK_SINKS = SPARK_NEBULA_SINKS + SPARK_FILE_SINKS + SPARK_SERVER_SINKS

NEBULA_SINKS = ["nebulagraph_vertex"]
NEBULA_BATCH_SIZE = 256
NEBULA_WRITER_MODES = ["insert", "update"]
DEFAULT_NEBULA_WRITER_MODE = "insert"


class NebulaWriterBase(object):
    def __init__(self, engine=None, config=None, **kwargs):
        self.engine_type = engine
        self.config = config

    def write(self, **kwargs):
        raise NotImplementedError

    def options(self, **kwargs):
        raise NotImplementedError

    def show_options(self, **kwargs):
        raise NotImplementedError


class NebulaWriter:
    def __init__(
        self,
        data,
        sink: str = "nebulagraph_vertex",
        config: NebulaGraphConfig = NebulaGraphConfig(),
        engine: str = "spark",
        **kwargs,
    ):
        self.engine_type = engine
        if self.engine_type == "spark":
            self.writer = NebulaWriterWithSpark(data, sink, config, **kwargs)
        elif self.engine_type == "nebula":
            self.writer = NebulaWriterWithGraph(data, sink, config, **kwargs)
        else:
            raise NotImplementedError

    def __getattr__(self, name):
        return getattr(self.writer, name)


class NebulaWriterWithGraph(NebulaWriterBase):
    def __init__(self, data, sink: str, config: NebulaGraphConfig, **kwargs):
        super().__init__("nebula", config, **kwargs)
        from ng_ai.engines import NebulaEngine

        self.engine = NebulaEngine(config)
        self.sink = sink
        self.nx_writer = self.engine.nx_writer(data=data, nebula_config=config)
        self.raw_data = data
        self._options = {
            "batch_size": NEBULA_BATCH_SIZE,
            "write_mode": DEFAULT_NEBULA_WRITER_MODE,
            "label": None,
            "properties": None,
            "sink": self.sink,
        }

    def set_options(self, **kwargs):
        for k, v in kwargs.items():
            if k in self._options:
                self._options[k] = v
            elif k in ["tag", "edge"]:
                self._options["label"] = v
        self.nx_writer.set_options(**self._options)

    def get_options(self):
        return self._options

    def write(self):
        # Ensure self.nx_writer.label, self.nx_writer.properties are not None
        if self.nx_writer.label is None:
            raise Exception("Label(tag or edge) should be set for NebulaWriter")
        if self.nx_writer.properties is None:
            raise Exception("Properties should be set for NebulaWriter")

        self.nx_writer.write()


class NebulaWriterWithSpark(NebulaWriterBase):
    def __init__(self, data, sink: str, config: NebulaGraphConfig, **kwargs):
        super().__init__("spark", config, **kwargs)
        from ng_ai.engines import SparkEngine

        self.engine = SparkEngine(config)
        self.raw_df = None
        self.raw_df_writer = None
        self.df = None
        self.jdf = None
        self.sink = sink
        self._options = {}

        from py4j.java_gateway import JavaObject

        if isinstance(data, NebulaDataFrameObject):
            self.df = data
            self.raw_df = data.data
        elif isinstance(data, JavaObject):
            self.jdf = data
        else:
            raise NotImplementedError

    def _convert_java_object_to_spark_df(self, jdf, column_map: dict = {}):
        """
        Convert JavaObject to Spark DataFrame, with column name mapping
        ref: https://stackoverflow.com/
             questions/36023860/how-to-use-a-scala-class-inside-pyspark
        """
        from pyspark.sql import DataFrame

        spark = self.engine.spark
        jdf = jdf.toDF()
        for k, v in column_map.items():
            jdf = jdf.withColumnRenamed(k, v)
        return DataFrame(jdf, spark)

    def _get_raw_df_writer_with_nebula(self):
        datasource_format = self.engine.nebula_spark_ds
        # hard code as overwrite SaveMode
        return self.raw_df.write.format(datasource_format).mode("overwrite")

    def _get_raw_df_writer_with_file(self):
        raise NotImplementedError

    def _get_raw_df_writer_with_server(self):
        raise NotImplementedError

    def _get_raw_df_writer(self):
        # validate sink
        assert self.sink in SPARK_SINKS, (
            f"Sink should be one of {SPARK_SINKS}, " f"but got {self.sink}",
        )

        if self.raw_df_writer is None:
            if self.sink in SPARK_NEBULA_SINKS:
                self.raw_df_writer = self._get_raw_df_writer_with_nebula()
            elif self.sink in SPARK_FILE_SINKS:
                self.raw_df_writer = self._get_raw_df_writer_with_file()
            elif self.sink in SPARK_SERVER_SINKS:
                self.raw_df_writer = self._get_raw_df_writer_with_server()
            else:
                raise NotImplementedError
        return self.raw_df_writer

    def _set_options_with_nebula(self, **kwargs):
        writer = self.raw_df_writer
        # type setting
        type = kwargs.get("type", "vertex")
        assert type in [
            "vertex",
            "edge",
        ], f"type should be vertex or edge, but got {type}"
        writer.option("type", type)
        self._options["type"] = type

        # space setting, set only when it's specified, else inherit
        # from NebulaGraphConfig
        space = kwargs.get("space", self.config.space)
        assert space is not None, "space should be specified"
        writer.option("spaceName", space)
        self._options["spaceName"] = space

        # label setting, for vertex case, it's tag, for edge case, it's edge type
        label = (
            kwargs.get("tag", None)
            if type == "vertex"
            else kwargs.get("edge_type", None)
        )
        assert (
            label is not None
        ), "tag(for vertex) or edge_type(for edge) should be specified"
        writer.option("label", label)
        self._options["label"] = label

        # writeMode setting, by default, it's insert, accept update or delete, too
        write_mode = kwargs.get("write_mode", "insert")
        assert write_mode in [
            "insert",
            "update",
            "delete",
        ], f"write_mode should be insert, update or delete, but got {write_mode}"
        writer.option("writeMode", write_mode)

        # batch setting, by default, it's 256
        batch = kwargs.get("batch", 256)
        assert isinstance(
            batch, int
        ), f"batch should be an integer, but got {type(batch)}"
        writer.option("batch", batch)
        self._options["batch"] = batch

        # credential from NebulaGraphConfig
        writer.option("metaAddress", self.config.metad_hosts)
        writer.option("graphAddress", self.config.graphd_hosts)
        writer.option("user", self.config.user)
        self._options["metaAddress"] = self.config.metad_hosts
        self._options["graphAddress"] = self.config.graphd_hosts
        self._options["user"] = self.config.user
        writer.option("password", self.config.password)

        if type == "vertex":
            # vidPolicy setting, by default, it's empty, accept hash or uuid, too
            vid_policy = kwargs.get("vid_policy", "")
            assert vid_policy in [
                "",
                "hash",
                "uuid",
            ], f"vid_policy should be empty, hash or uuid, but got {vid_policy}"
            writer.option("vidPolicy", vid_policy)
            self._options["vidPolicy"] = vid_policy

            # vertexField setting, by default, it's _id, must be a string
            vertexField = kwargs.get("vid_field", "_id")
            assert isinstance(
                vertexField, str
            ), f"vid_field should be a string, but got {type(vertexField)}"
            writer.option("vertexField", vertexField)
            self._options["vertexField"] = vertexField

        if type == "edge":
            # srcId setting, by default, it's srcId, must be a string
            src_id = kwargs.get("src_id", "srcId")
            assert isinstance(
                src_id, str
            ), f"src_id should be a string, but got {type(src_id)}"
            writer.option("srcId", src_id)
            self._options["srcId"] = src_id

            # dstId setting, by default, it's dstId, must be a string
            dst_id = kwargs.get("dst_id", "dstId")
            assert isinstance(
                dst_id, str
            ), f"dst_id should be a string, but got {type(dst_id)}"
            writer.option("dstId", dst_id)
            self._options["dstId"] = dst_id

            # srcIdPolicy setting, by default, it's empty, accept hash or uuid, too
            src_id_policy = kwargs.get("src_id_policy", "")
            assert src_id_policy in [
                "",
                "hash",
                "uuid",
            ], f"id_policy valid value: [empty, hash, uuid], got {src_id_policy}"
            writer.option("srcIdPolicy", src_id_policy)
            self._options["srcIdPolicy"] = src_id_policy

            # dstIdPolicy setting, by default, it's empty, accept hash or uuid, too
            dst_id_policy = kwargs.get("dst_id_policy", "")
            assert dst_id_policy in [
                "",
                "hash",
                "uuid",
            ], f"id_policy valid value: [empty, hash, uuid], got {dst_id_policy}"
            writer.option("dstIdPolicy", dst_id_policy)
            self._options["dstIdPolicy"] = dst_id_policy

            # randkField setting, by default, it's empty, must be a string
            rank_field = kwargs.get("rank_field", "")
            assert isinstance(
                rank_field, str
            ), f"rank_field should be a string, but got {type(rank_field)}"
            writer.option("rankField", rank_field)
            self._options["rankField"] = rank_field

    def _set_options_with_file(self, **kwargs):
        raise NotImplementedError

    def _set_options_with_server(self, **kwargs):
        raise NotImplementedError

    def set_options(self, **kwargs):
        """
        example:
        # change col name
        louvain_result_df = louvain_result.toDF()

        # CREATE TAG IF NOT EXISTS louvain (
        #     cluster_id string NOT NULL
        # );

        louvain_result_df = louvain_result_df.withColumnRenamed(
            "louvain", "cluster_id")
        louvain_result_df.write.format(
                "com.vesoft.nebula.connector.NebulaDataSource").option(
            "type", "vertex").option(
            "spaceName", "basketballplayer").option(
            "label", "louvain").option(
            "vidPolicy", "").option(
            "vertexField", "_id").option(
            "batch", 1).option(
            "metaAddress", "metad0:9559,metad1:9559,metad2:9559").option(
            "graphAddress", "graphd:9669").option(
            "passwd", "nebula").option(
            "user", "root").option(
            "writeType", "insert")
        """
        if self.raw_df is None:
            if self.jdf is None:
                raise ValueError("DataFrame is None in NebulaWriter")
            self.raw_df = self._convert_java_object_to_spark_df(
                self.jdf, kwargs.get("properties", {})
            )
        # TBD: check tag/edge type's schema against df's schema,
        #      raise error if not match

        self._get_raw_df_writer()  # self.raw_df_writer

        # case switch based on sink
        if self.sink in SPARK_NEBULA_SINKS:
            self._set_options_with_nebula(**kwargs)
        elif self.sink in SPARK_FILE_SINKS:
            self._set_options_with_file(**kwargs)
        elif self.sink in SPARK_SERVER_SINKS:
            self._set_options_with_server(**kwargs)
        else:
            raise NotImplementedError

        return self._options

    def get_options(self):
        return self._options

    def write(self):
        # Check self.raw_df, if it is None, raise exception
        if self.raw_df_writer is None:
            raise Exception(
                "No options set for NebulaWriter, please call options() first"
            )
        return self.raw_df_writer.save()
