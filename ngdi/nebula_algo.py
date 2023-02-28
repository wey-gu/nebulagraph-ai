# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The NebulaGraph Authors. All rights reserved.

from __future__ import annotations

from ngdi.nebula_data import NebulaGraphObject as NebulaGraphObjectImpl
from ngdi.nebula_data import NebulaDataFrameObject as NebulaDataFrameObjectImpl


class NebulaAlgorithm:
    def __init__(self, obj: NebulaGraphObjectImpl or NebulaDataFrameObjectImpl):
        if isinstance(obj, NebulaGraphObjectImpl):
            self.algorithm = NebulaGraphAlgorithm(obj)
        elif isinstance(obj, NebulaDataFrameObjectImpl):
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

    def __init__(self, ndf_obj: NebulaDataFrameObjectImpl):
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

    def get_spark_engine_context(self, config_class: str, lib_class: str):
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

    def get_spark_dataframe(self):
        """
        Check if df is a pyspark.sql.dataframe.DataFrameme, and return it
        """
        df = self.ndf_obj.data
        from pyspark.sql.dataframe import DataFrame as pyspark_sql_df

        if not isinstance(df, pyspark_sql_df):
            raise Exception(
                "The NebulaDataFrameObject is not a spark dataframe",
                f"Got type(df): {type(df)}",
            )
        return df

    def pagerank(
        self, reset_prob: float = 0.15, max_iter: int = 10, weighted: bool = False
    ):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "PRConfig", "PageRankAlgo"
        )
        df = self.get_spark_dataframe()
        config = spark._jvm.PRConfig(max_iter, reset_prob, encode_vertex_id)
        result = spark._jvm.PageRankAlgo.apply(jspark, df._jdf, config, weighted)

        return result

    def connected_components(self, max_iter: int = 10, weighted: bool = False):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "CcConfig", "ConnectedComponentsAlgo"
        )
        df = self.get_spark_dataframe()
        config = spark._jvm.CcConfig(max_iter, encode_vertex_id)
        result = spark._jvm.ConnectedComponentsAlgo.apply(
            jspark, df._jdf, config, weighted
        )

        return result

    def label_propagation(self, max_iter: int = 10, weighted: bool = False):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "LPAConfig", "LabelPropagationAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.LPAConfig(max_iter, encode_vertex_id)
        result = spark._jvm.LabelPropagationAlgo.apply(
            jspark, df._jdf, config, weighted
        )

        return result

    def louvain(self, max_iter: int = 10, internalIter: int = 10, tol: float = 0.0001):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "LouvainConfig", "LouvainAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.LouvainConfig(max_iter, internalIter, tol, encode_vertex_id)
        result = spark._jvm.LouvainAlgo.apply(jspark, df._jdf, config, False)

        return result

    def k_core(self, max_iter: int = 10, degree: int = 2):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "KCoreConfig", "KCoreAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.KCoreConfig(max_iter, degree, encode_vertex_id)

        result = spark._jvm.KCoreAlgo.apply(jspark, df._jdf, config)

        return result

    # def shortest_path(self, landmarks: list, weighted: bool = False):
    #     engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
    #         "ShortestPathConfig", "ShortestPathAlgo"
    #     )
    #     # TBD: ShortestPathAlgo is not yet encodeID compatible
    #     df = self.get_spark_dataframe()

    #     config = spark._jvm.ShortestPathConfig(landmarks, encode_vertex_id)
    #     result = spark._jvm.ShortestPathAlgo.apply(jspark, df._jdf, config, weighted)

    #     return result

    def degree_statics(self):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "DegreeStaticConfig", "DegreeStaticAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.DegreeStaticConfig(encode_vertex_id)
        result = spark._jvm.DegreeStaticAlgo.apply(jspark, df._jdf, config)

        return result

    def betweenness_centrality(
        self, max_iter: int = 10, degree: int = 2, weighted: bool = False
    ):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "BetweennessConfig", "BetweennessCentralityAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.BetweennessConfig(max_iter, encode_vertex_id)
        result = spark._jvm.BetweennessCentralityAlgo.apply(
            jspark, df._jdf, config, weighted
        )

        return result

    def coefficient_centrality(self, type: str = "local"):
        # type could be either "local" or "global"
        assert type.lower() in ["local", "global"], (
            "type should be either local or global"
            f"in coefficient_centrality algo. Got type: {type}"
        )
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "CoefficientConfig", "ClusteringCoefficientAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.CoefficientConfig(type, encode_vertex_id)
        result = spark._jvm.ClusteringCoefficientAlgo.apply(jspark, df._jdf, config)

        return result

    def bfs(self, max_depth: int = 10, root: int = 1):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "BfsConfig", "BfsAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.BfsConfig(max_depth, root, encode_vertex_id)
        result = spark._jvm.BfsAlgo.apply(jspark, df._jdf, config)

        return result

    # dfs is not yet supported, need to revisit upstream nebula-algorithm
    #
    # def dfs(self, max_depth: int = 10, root: int = 1):
    #     engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
    #         "DfsConfig", "DfsAlgo"
    #     )
    #     df = self.get_spark_dataframe()

    #     config = spark._jvm.DfsConfig(max_depth, root, encode_vertex_id)
    #     result = spark._jvm.DfsAlgo.apply(jspark, df._jdf, config)

    #     return result

    def hanp(
        self,
        hop_attenuation: float = 0.5,
        max_iter: int = 10,
        preference: float = 1.0,
        weighted: bool = False,
        preferences=None,
    ):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "HanpConfig", "HanpAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.HanpConfig(
            hop_attenuation, max_iter, preference, encode_vertex_id
        )
        result = spark._jvm.HanpAlgo.apply(
            jspark, df._jdf, config, weighted, preferences
        )

        return result

    # def node2vec(
    #     self,
    #     max_iter: int = 10,
    #     lr: float = 0.025,
    #     data_num_partition: int = 10,
    #     model_num_partition: int = 10,
    #     dim: int = 10,
    #     window: int = 3,
    #     walk_length: int = 5,
    #     num_walks: int = 3,
    #     p: float = 1.0,
    #     q: float = 1.0,
    #     directed: bool = False,
    #     degree: int = 30,
    #     emb_separator: str = ",",
    #     model_path: str = "hdfs://127.0.0.1:9000/model",
    #     weighted: bool = False,
    # ):
    #     engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
    #         "Node2vecConfig", "Node2VecAlgo"
    #     )
    #     # TBD: Node2VecAlgo is not yet encodeID compatible
    #     df = self.get_spark_dataframe()
    #     config = spark._jvm.Node2vecConfig(
    #         max_iter,
    #         lr,
    #         data_num_partition,
    #         model_num_partition,
    #         dim,
    #         window,
    #         walk_length,
    #         num_walks,
    #         p,
    #         q,
    #         directed,
    #         degree,
    #         emb_separator,
    #         model_path,
    #         encode_vertex_id,
    #     )
    #     result = spark._jvm.Node2VecAlgo.apply(jspark, df._jdf, config, weighted)

    #     return result

    def jaccard(self, tol: float = 1.0):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "JaccardConfig", "JaccardAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.JaccardConfig(tol, encode_vertex_id)
        result = spark._jvm.JaccardAlgo.apply(jspark, df._jdf, config)

        return result

    def strong_connected_components(self, max_iter: int = 10, weighted: bool = False):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "CcConfig", "StronglyConnectedComponentsAlgo"
        )
        df = self.get_spark_dataframe()
        config = spark._jvm.CcConfig(max_iter, encode_vertex_id)
        result = spark._jvm.StronglyConnectedComponentsAlgo.apply(
            jspark, df._jdf, config, weighted
        )

        return result

    def triangle_count(self):
        engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
            "TriangleConfig", "TriangleCountAlgo"
        )
        df = self.get_spark_dataframe()
        config = spark._jvm.TriangleConfig(encode_vertex_id)
        result = spark._jvm.TriangleCountAlgo.apply(jspark, df._jdf, config)

        return result

    # def closeness(self, weighted: bool = False):
    #     # TBD: ClosenessAlgo is not yet encodeID compatible
    #     engine, spark, jspark, encode_vertex_id = self.get_spark_engine_context(
    #         "ClosenessConfig", "ClosenessAlgo"
    #     )
    #     df = self.get_spark_dataframe()
    #     config = spark._jvm.ClosenessConfig(weighted, encode_vertex_id)
    #     result = spark._jvm.ClosenessAlgo.apply(jspark, df._jdf, config, False)

    #     return result


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
        pass
