# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The NebulaGraph Authors. All rights reserved.

from __future__ import annotations

from ngdi.nebula_data import NebulaGraphObject, NebulaDataFrameObject

class NebulaAlgorithm:
    def __init__(self, obj: NebulaGraphObject or NebulaDataFrameObject):
        if isinstance(obj, NebulaGraphObject):
            self.algorithm = NebulaGraphAlgorithm(obj)
        elif isinstance(obj, NebulaDataFrameObject):
            self.algorithm = NebulaDataFrameAlgorithm(obj)
        else:
            raise ValueError(
                f"Unsupported object type: {type(obj)}",
                "NebulaAlgorithm only supports NebulaGraphObject and"
                "NebulaDataFrameObject",
            )
        self.obj = obj
        self.engine = obj.engine

    def __getattr__(self, name):
        return getattr(self.algorithm, name)


class NebulaDataFrameAlgorithm:
    """
    Spark Dataframe to run algorithm
    """
    def __init__(self, ndf_obj: NebulaDataFrameObject):
        self.ndf_obj = ndf_obj

    def check_engine(self):
        """
        Check if the engine is supported.
        For netowrkx, we need to convert the NebulaDataFrameObject to NebulaGraphObject
        For spark, we can directly use the NebulaDataFrameObject
        """
        if self.ndf_obj.engine.type == "networkx":
            raise Exception(
                "For NebulaDataFrameObject in networkx engine,"
                "Please transform it to NebulaGraphObject to run algorithm",
                "For example: g = nebula_df.to_graph; g.algo.pagerank()",
            )

    def get_spark_engine_context(self, config_class, lib_class):
        """
        Get the engine context
        """
        self.check_engine()
        engine = self.ndf_obj.engine
        spark = engine.spark
        jspark = engine.jspark
        engine.import_algo_config_class(config_class)
        engine.import_algo_lib_class(lib_class)
        return engine, spark, jspark, engine.encode_vertex_id

    def pagerank(self, reset_prob=0.85, max_iter=3):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "PRConfig", "PageRankAlgo")
        df = self.ndf_obj.data
        # double check df is a spark dataframe
        if not isinstance(df, spark.DataFrame):
            raise Exception("The NebulaDataFrameObject is not a spark dataframe")

        config = spark._jvm.PRConfig(max_iter, reset_prob, encode_vertex_id)
        result = spark._jvm.PageRankAlgo.apply(
            jspark,
            df._jdf,
            config,
            False)
        # TBD: False means not to use the default partitioner,
        # we could make it configurable in the future
        return result
    
    def connected_components(self, max_iter=3):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "CCConfig", "ConnectedComponentsAlgo")
        df = self.ndf_obj.data
        # double check df is a spark dataframe
        if not isinstance(df, spark.DataFrame):
            raise Exception("The NebulaDataFrameObject is not a spark dataframe")

        config = spark._jvm.CCConfig(max_iter, encode_vertex_id)
        result = spark._jvm.ConnectedComponentsAlgo.apply(
            jspark,
            df._jdf,
            config,
            False)
        # TBD: False means not to use the default partitioner,
        # we could make it configurable in the future
        return result

    def label_propagation(self, max_iter=3):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "LPAConfig", "LabelPropagationAlgo")
        df = self.ndf_obj.data
        # double check df is a spark dataframe
        if not isinstance(df, spark.DataFrame):
            raise Exception("The NebulaDataFrameObject is not a spark dataframe")

        config = spark._jvm.LPAConfig(max_iter, encode_vertex_id)
        result = spark._jvm.LabelPropagationAlgo.apply(
            jspark,
            df._jdf,
            config,
            False)
        # TBD: False means not to use the default partitioner,
        # we could make it configurable in the future
        return result

    def louvain(self, max_iter=3, internalIter=10, tol=0.0001):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "LouvainConfig", "LouvainAlgo")
        df = self.ndf_obj.data
        # double check df is a spark dataframe
        if not isinstance(df, spark.DataFrame):
            raise Exception("The NebulaDataFrameObject is not a spark dataframe")

        config = spark._jvm.LouvainConfig(
            max_iter,
            internalIter,
            tol,
            encode_vertex_id)
        result = spark._jvm.LouvainAlgo.apply(
            jspark,
            df._jdf,
            config,
            False)
        # TBD: False means not to use the default partitioner,
        # we could make it configurable in the future
        return result

    def k_core(self, max_iter=3, degree=3):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "KCoreConfig", "KCoreAlgo")
        df = self.ndf_obj.data
        # double check df is a spark dataframe
        if not isinstance(df, spark.DataFrame):
            raise Exception("The NebulaDataFrameObject is not a spark dataframe")

        config = spark._jvm.KCoreConfig(
            max_iter,
            degree,
            encode_vertex_id)

        result = spark._jvm.KCoreAlgo.apply(
            jspark,
            df._jdf,
            config,
            False)
        # TBD: False means not to use the default partitioner,
        # we could make it configurable in the future
        return result


class NebulaGraphAlgorithm:
    """
    Networkx to run algorithm
    """
    def __init__(self, graph):
        self.graph = graph

    def check_engine(self):
        """
        Check if the engine is supported.
        For netowrkx, we can directly call .algo.pagerank()
        For spark, we need to convert the NebulaGraphObject to NebulaDataFrameObject
        """
        if self.graph.engine.type == "spark":
            raise Exception(
                "For NebulaGraphObject in spark engine,"
                "Please transform it to NebulaDataFrameObject to run algorithm",
                "For example: df = nebula_graph.to_df; df.algo.pagerank()",
            )

    def pagerank(self, reset_prob=0.15, max_iter=10):
        self.check_engine()

        g = self.graph
        return result