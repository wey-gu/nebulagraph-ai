# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The NebulaGraph Authors. All rights reserved.
from __future__ import annotations

from ng_ai.config import NebulaGraphConfig

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
        self.encode_vertex_id = ENCODE_VERTEX_ID
        self.parse_config()

        from pyspark.sql import SparkSession

        self.spark = (
            SparkSession.builder.appName("NebulaGraph Data Intelligence")
            .config("spark.sql.shuffle.partitions", self.shuffle_partitions)
            .config("spark.executor.memory", self.executor_memory)
            .config("spark.driver.memory", self.driver_memory)
            .getOrCreate()
        )

        self.jspark = self.spark._jsparkSession
        self.java_import = None
        self.prepare()
        self.nebula_spark_ds = NEBULA_SPARK_CONNECTOR_DATASOURCE

        # TBD: ping NebulaGraph Meta and Storage Server, fail and guide user to check config

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

        if self.config.encode_vertex_id is not None:
            self.encode_vertex_id = self.config.encode_vertex_id

    def prepare(self):
        self.java_import = self._get_java_import()

    def _get_java_import(self, force=False):
        if self.java_import is not None and not force:
            return self.java_import

        from py4j.java_gateway import java_import

        # scala:
        # import "com.vesoft.nebula.algorithm.config.SparkConfig"
        java_import(self.spark._jvm, "com.vesoft.nebula.algorithm.config.SparkConfig")
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
        self.parse_config()

    def __str__(self):
        return f"NebulaEngine: {self.config}"

    def parse_config(self):
        """parse and validate config"""
        if self.config is None:
            return

    def prepare(self):
        pass
