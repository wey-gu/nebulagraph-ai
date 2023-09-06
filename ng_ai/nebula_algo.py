# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The NebulaGraph Authors. All rights reserved.

from __future__ import annotations

from ng_ai.nebula_data import NebulaDataFrameObject as NebulaDataFrameObjectImpl
from ng_ai.nebula_data import NebulaGraphObject as NebulaGraphObjectImpl


def algo(func):
    func.is_algo = True
    return func


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
        self.algorithms = []

    def register_algo(self, func):
        self.algorithms.append(func.__name__)

    def get_all_algo(self):
        if not self.algorithms:
            for name, func in NebulaDataFrameAlgorithm.__dict__.items():
                if hasattr(func, "is_algo"):
                    self.register_algo(func)
        return self.algorithms

    def check_engine(self):
        """
        Check if the engine is supported.
        For netowrkx, we need to convert the NebulaDataFrameObject
            to NebulaGraphObject
        For spark, we can directly use the NebulaDataFrameObject
        """
        if self.ndf_obj.engine.type == "nebula":
            raise Exception(
                "For NebulaDataFrameObject in networkx engine,"
                "Plz transform it to NebulaGraphObject to run algorithm",
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
        return engine, spark, jspark, engine.encode_vid

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

    @algo
    def pagerank(
        self, reset_prob: float = 0.15, max_iter: int = 10, weighted: bool = False
    ):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "PRConfig", "PageRankAlgo"
        )
        df = self.get_spark_dataframe()
        config = spark._jvm.PRConfig(max_iter, reset_prob, encode_vid)
        result = spark._jvm.PageRankAlgo.apply(jspark, df._jdf, config, weighted)

        return result

    @algo
    def connected_components(self, max_iter: int = 10, weighted: bool = False):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "CcConfig", "ConnectedComponentsAlgo"
        )
        df = self.get_spark_dataframe()
        config = spark._jvm.CcConfig(max_iter, encode_vid)
        result = spark._jvm.ConnectedComponentsAlgo.apply(
            jspark, df._jdf, config, weighted
        )

        return result

    @algo
    def label_propagation(self, max_iter: int = 10, weighted: bool = False):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "LPAConfig", "LabelPropagationAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.LPAConfig(max_iter, encode_vid)
        result = spark._jvm.LabelPropagationAlgo.apply(
            jspark, df._jdf, config, weighted
        )

        return result

    @algo
    def louvain(self, max_iter: int = 20, internalIter: int = 10, tol: float = 0.5):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "LouvainConfig", "LouvainAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.LouvainConfig(max_iter, internalIter, tol, encode_vid)
        result = spark._jvm.LouvainAlgo.apply(jspark, df._jdf, config, False)

        return result

    @algo
    def k_core(self, max_iter: int = 10, degree: int = 2):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "KCoreConfig", "KCoreAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.KCoreConfig(max_iter, degree, encode_vid)

        result = spark._jvm.KCoreAlgo.apply(jspark, df._jdf, config)

        return result

    # def shortest_path(self, landmarks: list, weighted: bool = False):
    #     engine, spark, jspark, encode_vid = self.get_spark_engine_context(
    #         "ShortestPathConfig", "ShortestPathAlgo"
    #     )
    #     # TBD: ShortestPathAlgo is not yet encodeID compatible
    #     df = self.get_spark_dataframe()

    #     config = spark._jvm.ShortestPathConfig(landmarks, encode_vid)
    #     result = spark._jvm.ShortestPathAlgo.apply(
    #         jspark, df._jdf, config, weighted)

    #     return result

    @algo
    def degree_statics(self):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "DegreeStaticConfig", "DegreeStaticAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.DegreeStaticConfig(encode_vid)
        result = spark._jvm.DegreeStaticAlgo.apply(jspark, df._jdf, config)

        return result

    @algo
    def betweenness_centrality(self, max_iter: int = 10, weighted: bool = False):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "BetweennessConfig", "BetweennessCentralityAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.BetweennessConfig(max_iter, encode_vid)
        result = spark._jvm.BetweennessCentralityAlgo.apply(
            jspark, df._jdf, config, weighted
        )

        return result

    @algo
    def clustering_coefficient(self, type: str = "local"):
        # type could be either "local" or "global"
        assert type.lower() in ["local", "global"], (
            "type should be either local or global"
            f"in clustering_coefficient algo. Got type: {type}"
        )
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "CoefficientConfig", "ClusteringCoefficientAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.CoefficientConfig(type, encode_vid)
        result = spark._jvm.ClusteringCoefficientAlgo.apply(jspark, df._jdf, config)

        return result

    @algo
    def bfs(self, max_depth: int = 10, root: int = 1):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "BfsConfig", "BfsAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.BfsConfig(max_depth, root, encode_vid)
        result = spark._jvm.BfsAlgo.apply(jspark, df._jdf, config)

        return result

    # dfs is not yet supported, need to revisit upstream nebula-algorithm
    @algo
    def dfs(self, max_depth: int = 10, root: int = 1):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "DfsConfig", "DfsAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.DfsConfig(max_depth, root, encode_vid)
        result = spark._jvm.DfsAlgo.apply(jspark, df._jdf, config)

        return result

    @algo
    def hanp(
        self,
        hop_attenuation: float = 0.5,
        max_iter: int = 10,
        preference: float = 1.0,
        weighted: bool = False,
        preferences=None,
    ):
        """
        Hop Attenuation & Node Preference
        """
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "HanpConfig", "HanpAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.HanpConfig(
            hop_attenuation, max_iter, preference, encode_vid
        )
        result = spark._jvm.HanpAlgo.apply(
            jspark, df._jdf, config, weighted, preferences
        )

        return result

    # @algo
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
    #     engine, spark, jspark, encode_vid = self.get_spark_engine_context(
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
    #         encode_vid,
    #     )
    #     result = spark._jvm.Node2VecAlgo.apply(jspark, df._jdf, config, weighted)

    #     return result

    @algo
    def jaccard(self, tol: float = 1.0):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "JaccardConfig", "JaccardAlgo"
        )
        df = self.get_spark_dataframe()

        config = spark._jvm.JaccardConfig(tol, encode_vid)
        result = spark._jvm.JaccardAlgo.apply(jspark, df._jdf, config)

        return result

    @algo
    def strong_connected_components(
        self, max_iter: int = 10, weighted: bool = False
    ):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "CcConfig", "StronglyConnectedComponentsAlgo"
        )
        df = self.get_spark_dataframe()
        config = spark._jvm.CcConfig(max_iter, encode_vid)
        result = spark._jvm.StronglyConnectedComponentsAlgo.apply(
            jspark, df._jdf, config, weighted
        )

        return result

    @algo
    def triangle_count(self):
        engine, spark, jspark, encode_vid = self.get_spark_engine_context(
            "TriangleConfig", "TriangleCountAlgo"
        )
        df = self.get_spark_dataframe()
        config = spark._jvm.TriangleConfig(encode_vid)
        result = spark._jvm.TriangleCountAlgo.apply(jspark, df._jdf, config)

        return result

    # @algo
    # def closeness_centrality(self, weighted: bool = False):
    #     # TBD: ClosenessAlgo is not yet encodeID compatible
    #     engine, spark, jspark, encode_vid = self.get_spark_engine_context(
    #         "ClosenessConfig", "ClosenessAlgo"
    #     )
    #     df = self.get_spark_dataframe()
    #     config = spark._jvm.ClosenessConfig(weighted, encode_vid)
    #     result = spark._jvm.ClosenessAlgo.apply(
    #         jspark, df._jdf, config, False)

    #     return result


class NebulaGraphAlgorithm:
    """
    Networkx to run algorithm
    """

    def __init__(self, ng_obj: NebulaGraphObjectImpl):
        self.ngraph = ng_obj
        self.algorithms = []
        self.engine = ng_obj.engine

    def register_algo(self, func):
        self.algorithms.append(func.__name__)

    def get_all_algo(self):
        if not self.algorithms:
            for name, func in NebulaGraphAlgorithm.__dict__.items():
                if hasattr(func, "is_algo"):
                    self.register_algo(func)
        return self.algorithms

    def check_engine(self):
        """
        Check if the engine is supported.
        For netowrkx, we can directly call .algo.pagerank()
        For spark, we need to convert the NebulaGraphObject
            to NebulaDataFrameObject
        """
        if self.engine.type == "spark":
            raise Exception(
                "For NebulaGraphObject in spark engine,"
                "Plz transform it to NebulaDataFrameObject to run algorithm",
                "For example: df = nebula_graph.to_df; df.algo.pagerank()",
            )
        if self.engine.type == "nebula":
            return True
        else:
            raise Exception("Unsupported engine type")

    @algo
    def pagerank(self, reset_prob=0.15, max_iter=10, **kwargs):
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        weight = kwargs.get("weight", None)
        assert type(weight) in [str, type(None)], "weight must be str or None"
        assert type(reset_prob) == float, "reset_prob must be float"
        assert type(max_iter) == int, "max_iter must be int"
        tol = kwargs.get("tol", 1e-06)
        assert type(tol) == float, "tol must be float"

        return self.engine.nx.pagerank(
            g, alpha=1 - reset_prob, max_iter=max_iter, tol=tol, weight=weight
        )

    @algo
    def louvain(self, weight: str = None, resolution: float = 1.0):
        """
        doc: https://github.com/taynaud/python-louvain
        """
        weight = weight if weight else ""
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        ug = g.to_undirected()
        return self.engine.nx_community_louvain.best_partition(
            ug, weight=weight, resolution=resolution
        )

    @algo
    def label_propagation(self, **kwargs):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /community.html
        """

        self.check_engine()
        g = self.ngraph.get_nx_graph()
        ug = g.to_undirected()
        return self.engine.nx.algorithms.community.label_propagation_communities(
            ug, **kwargs
        )

    @algo
    def k_core(self, k: int = 2):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /generated/networkx.algorithms.core.k_core.html
        return: networkx.classes.digraph.DiGraph
        """
        # TBD, k_core requires single graph
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        # MultiDiGraph to DiGraph
        single_g = self.engine.nx.DiGraph()
        for u, v in g.edges():
            single_g.add_edge(u, v)
        return self.engine.nx.k_core(single_g, k=k)

    @algo
    def k_truss(self, k: int = 2):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /generated/networkx.algorithms.core.k_truss.html
        return: networkx.classes.graph.Graph
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        # MultiDiGraph to Graph
        single_ug = self.engine.nx.Graph()
        for u, v in g.edges():
            single_ug.add_edge(u, v)
        return self.engine.nx.k_truss(single_ug, k=k)

    @algo
    def k_clique_communities(self, k: int = 2, **kwargs):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /community.html
        return: Yields sets of nodes, one for each k-clique community.
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        ug = g.to_undirected()
        return self.engine.nx.algorithms.community.k_clique_communities(
            ug, k=k, **kwargs
        )

    @algo
    def degree_statics(self):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/classes
        /generated/networkx.MultiDiGraph.degree.html
        return:
          List[Tuple[str, int, int, int]],
          (node_id, degree, in_degree, out_degree)
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        degrees = dict(g.degree())
        in_degrees = dict(g.in_degree())
        out_degrees = dict(g.out_degree())

        result = []
        for node_id in g.nodes():
            degree = degrees[node_id]
            in_degree = in_degrees[node_id]
            out_degree = out_degrees[node_id]
            result.append((node_id, degree, in_degree, out_degree))
        return result

    @algo
    def betweenness_centrality(
        self, k: int = None, normalized: bool = True, weight: str = None, **kwargs
    ):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /generated/networkx.algorithms.centrality.betweenness_centrality.html
        return: Dictionary of nodes with betweenness centrality as the value.
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        # MultiDiGraph to DiGraph
        single_g = self.engine.nx.DiGraph()
        for u, v, data in g.edges(data=True):
            if weight is not None and weight in data:
                single_g.add_edge(u, v, weight=data[weight])
            else:
                single_g.add_edge(u, v)
        return self.engine.nx.betweenness_centrality(
            single_g, k=k, normalized=normalized, weight=weight, **kwargs
        )

    @algo
    def clustering_coefficient(self, weight: str = None, **kwargs):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /generated/networkx.algorithms.cluster.clustering.html
        return: Dictionary of nodes with clustering coefficient as the value.
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        # MultiDiGraph to DiGraph
        single_g = self.engine.nx.DiGraph()
        for u, v, data in g.edges(data=True):
            if weight is not None and weight in data:
                single_g.add_edge(u, v, weight=data[weight])
            else:
                single_g.add_edge(u, v)
        return self.engine.nx.clustering(single_g, weight=weight, **kwargs)

    @algo
    def bfs(self, root=None, max_depth: int = 10, reverse: bool = False, **kwargs):
        """
        doc:
        https://networkx.org/documentation/networkx-2.6.2/reference/algorithms/
        generated/networkx.algorithms.traversal.breadth_first_search.bfs_edges.html
        root: The node at which to start the search,
          defaults to the first node in the graph.
        reverse: If True, perform a reverse breadth-first-search.
        return: Yields edges in a breadth-first-search starting at source.
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        if root is None:
            root = next(iter(g.nodes()))
        return self.engine.nx.bfs_edges(
            g, source=root, depth_limit=max_depth, reverse=reverse, **kwargs
        )

    @algo
    def dfs(self, root=None, max_depth: int = 10, **kwargs):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /generated/networkx.algorithms.traversal.depth_first_search.dfs_edges.html
        root: The node at which to start the search,
          defaults to the first node in the graph.
        return: Yields edges in a depth-first-search starting at source.
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        if root is None:
            root = next(iter(g.nodes()))
        return self.engine.nx.dfs_edges(
            g, source=root, depth_limit=max_depth, **kwargs
        )

    @algo
    def node2vec(
        self,
        dimensions: int = 128,
        walk_length: int = 80,
        num_walks: int = 10,
        workers: int = 1,
        fit_args: dict = {},
        **kwargs,
    ):
        """
        doc: https://github.com/eliorc/node2vec
        dimensions: int, optional (default = 128), Dimensionality of the
          word vectors.
        walk_length: int, optional (default = 80), Length of walk per source.
          Default value is 80.
        num_walks: int, optional (default = 10), Number of walks per source.
          Default value is 10.
        workers: int, optional (default = 1), Number of parallel workers.
          Default is 1.
        fit_args: dict, optional (default = {}), Arguments for
          gensim.models.Word2Vec.fit()
        return: gensim.models.keyedvectors.Word2VecKeyedVectorsmodel
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        node2vec = self.engine.nx_node2vec(
            graph=g,
            dimensions=dimensions,
            walk_length=walk_length,
            num_walks=num_walks,
            workers=workers,
            **kwargs,
        )
        model = node2vec.fit(**fit_args)
        return model

    @algo
    def jaccard(self, ebunch: list = None, **kwargs):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /generated/networkx.algorithms.link_prediction.jaccard_coefficient.html
        ebunch: iterable of node pairs, optional (default = None),
          If provided, only return the Jaccard coefficient for the specified pairs.
            example: [('A', 'B'), ('A', 'C')]
        return: Yields tuples of (u, v, p) where u and v are nodes
          and p is the Jaccard coefficient of the neighbors of u and v.
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        # MultiDiGraph to Graph
        single_ug = self.engine.nx.Graph()
        for u, v in g.edges():
            single_ug.add_edge(u, v)
        return self.engine.nx.jaccard_coefficient(
            single_ug, ebunch=ebunch, **kwargs
        )

    @algo
    def connected_components(self, **kwargs):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /generated/networkx.algorithms.components.connected_components.html
        return: A generator of sets of nodes, one for each connected component
          in the graph.
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        # MultiDiGraph to MultiGraph
        ug = g.to_undirected()
        return self.engine.nx.connected_components(ug, **kwargs)

    @algo
    def weakly_connected_components(self, **kwargs):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /generated/networkx.algorithms.components.weakly_connected_components.html
        return: A generator of sets of nodes, one for each weakly connected
          component in the graph.
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        return self.engine.nx.weakly_connected_components(g, **kwargs)

    @algo
    def strongly_connected_components(self, **kwargs):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /generated/networkx.algorithms.components.strongly_connected_components.html
        return: A generator of sets of nodes, one for each strongly connected
          component in the graph.
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        return self.engine.nx.strongly_connected_components(g, **kwargs)

    @algo
    def triangle_count(self, **kwargs):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /generated/networkx.algorithms.cluster.triangles.html
        return: A dictionary keyed by node to the number of triangles that include
          that node as a vertex.
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        # MultiDiGraph to Graph
        single_ug = self.engine.nx.Graph()
        for u, v in g.edges():
            single_ug.add_edge(u, v)
        return self.engine.nx.triangles(single_ug, **kwargs)

    @algo
    def closeness_centrality(
        self, u=None, distance=None, wf_improved=True, **kwargs
    ):
        """
        doc: https://networkx.org/documentation/networkx-2.6.2/reference/algorithms
        /generated/networkx.algorithms.centrality.closeness_centrality.html
        u: node, optional (default = None), If specified, return only the value
            for the node u.
        distance: edge attribute key, optional (default = None), Use the specified
            edge attribute as the edge distance in shortest path calculations.
        wf_improved: bool, optional (default = True), If True, use the improved
            algorithm of Freeman and Bader which computes the closeness centrality
            using the number of reachable nodes instead of the number of nodes in
            the graph.
        return: A dictionary keyed by node to the closeness centrality of that
            node.
        """
        self.check_engine()
        g = self.ngraph.get_nx_graph()
        return self.engine.nx.closeness_centrality(
            g, u=u, distance=distance, wf_improved=wf_improved, **kwargs
        )
