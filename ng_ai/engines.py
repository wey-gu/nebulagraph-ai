# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The NebulaGraph Authors. All rights reserved.
from __future__ import annotations

# SPARK DEFAULTS
DEFAULT_SHUFFLE_PARTITIONS = 5
DEFAULT_EXECUTOR_MEMORY = "8g"
DEFAULT_DRIVER_MEMORY = "4g"

# NebulaGraph Algorithm Path
NEBULA_ALGO = "com.vesoft.nebula.algorithm"
NEBULA_ALGO_CONFIG = f"{NEBULA_ALGO}.config"
NEBULA_ALGO_LIB = f"{NEBULA_ALGO}.lib"

# NebulaGraph Spark Connector Path
NEBULA_SPARK_CONNECTOR = "com.vesoft.nebula.connector"
NEBULA_SPARK_CONNECTOR_DATASOURCE = f"{NEBULA_SPARK_CONNECTOR}.NebulaDataSource"

# NebulaGraph Algorithm Default Config
ENCODE_VERTEX_ID = True


class BaseEngine(object):
    def __init__(self, config):
        pass

    def __str__(self):
        return f"BaseEngine: {self.type}"

    def prepare():
        raise NotImplementedError


class SparkEngine(BaseEngine):
    def __init__(self, config):
        self.type = "spark"
        self.config = config
        self.shuffle_partitions = DEFAULT_SHUFFLE_PARTITIONS
        self.executor_memory = DEFAULT_EXECUTOR_MEMORY
        self.driver_memory = DEFAULT_DRIVER_MEMORY
        self.encode_vid = ENCODE_VERTEX_ID
        self.parse_config()

        from pyspark.sql import SparkSession

        self.spark = (
            SparkSession.builder.appName("NebulaGraph AI")
            .config("spark.sql.shuffle.partitions", self.shuffle_partitions)
            .config("spark.executor.memory", self.executor_memory)
            .config("spark.driver.memory", self.driver_memory)
            .getOrCreate()
        )

        self.jspark = self.spark._jsparkSession
        self.java_import = None
        self.prepare()
        self.nebula_spark_ds = NEBULA_SPARK_CONNECTOR_DATASOURCE

        # TBD: ping NebulaGraph Meta and Storage Server
        # fail and guide user to check config

    def __str__(self):
        return f"SparkEngine: {self.spark}"

    def parse_config(self):
        """parse and validate config"""
        if self.config is None:
            return

        if self.config.shuffle_partitions is not None:
            self.shuffle_partitions = self.config.shuffle_partitions

        if self.config.executor_memory is not None:
            self.executor_memory = self.config.executor_memory

        if self.config.driver_memory is not None:
            self.driver_memory = self.config.driver_memory

        if self.config.encode_vid is not None:
            self.encode_vid = self.config.encode_vid

    def prepare(self):
        self.java_import = self._get_java_import()

    def _get_java_import(self, force=False):
        if self.java_import is not None and not force:
            return self.java_import

        from py4j.java_gateway import java_import

        # scala:
        # import "com.vesoft.nebula.algorithm.config.SparkConfig"
        java_import(
            self.spark._jvm, "com.vesoft.nebula.algorithm.config.SparkConfig"
        )
        return java_import

    def import_scala_class(self, class_name):
        """
        For example:
        scala:
            import "com.vesoft.nebula.algorithm.lib.PageRankAlgo"
        python:
            java_import(spark._jvm, "com.vesoft.nebula.algorithm.lib.PageRankAlgo")
        """
        self.java_import(self.spark._jvm, class_name)

    def import_algo_config_class(self, class_name):
        self.import_scala_class(f"{NEBULA_ALGO_CONFIG}.{class_name}")

    def import_algo_lib_class(self, class_name):
        self.import_scala_class(f"{NEBULA_ALGO_LIB}.{class_name}")


class NebulaEngine(BaseEngine):
    def __init__(self, config=None):
        self.type = "nebula"
        self.config = config

        # let's make all nx related import here
        import community as community_louvain
        import networkx as nx
        import ng_nx
        from ng_nx import NebulaReader as NxReader
        from ng_nx import NebulaScanReader as NxScanReader
        from ng_nx import NebulaWriter as NxWriter
        from ng_nx.utils import NebulaGraphConfig as NxConfig
        from ng_nx.utils import result_to_df
        from node2vec import Node2Vec

        self.nx = nx
        self.ng_nx = ng_nx
        self.nx_reader = NxReader
        self.nx_writer = NxWriter
        self.nx_scan_reader = NxScanReader
        self.nx_community_louvain = community_louvain
        self.nx_node2vec = Node2Vec
        self._nx_config = NxConfig
        self.nx_config = None

        self.result_to_df = result_to_df

        self.nx_config = None
        self.parse_config()

    def __str__(self):
        return (
            f"NebulaEngine(NetworkX): {self.config}, "
            f"nx version: {self.nx.__version__}, "
            f"ng_nx version: {self.ng_nx.__version__}"
        )

    def parse_config(self):
        """parse and validate config"""
        if self.config is None:
            return
        self.nx_config = self._nx_config(**self.config.__dict__)


class DGLEngine(BaseEngine):
    def __init__(self, config=None):
        self.type = "dgl"
        self.config = config

        # let's make all dgl related import here
        import dgl
        import dgl.nn as dglnn
        import dgl.function as fn
        import torch.nn as nn
        import torch.nn.functional as F
        import torch

        self.dgl = dgl
        self.dglnn = dglnn
        self.fn = fn
        self.nn = nn
        self.F = F
        self.torch = torch

        self.dgl_config = None
        self.parse_config()

    def __str__(self):
        return (
            f"DGLEngine(DGL): {self.config}, "
            f"dgl version: {self.dgl.__version__}"
        )

    def parse_config(self):
        """parse and validate config"""
        if self.config is None:
            return
        self.dgl_config = self._dgl_config(**self.config.__dict__)
