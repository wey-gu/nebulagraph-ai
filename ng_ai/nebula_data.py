# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The NebulaGraph Authors. All rights reserved.

from __future__ import annotations

from ng_ai.engines import NebulaEngine


class NebulaGraphObject:
    def __init__(self, engine: NebulaEngine, raw_graph, **kwargs):
        self.engine = engine
        # if engine is nebula, self._graph is a networkx graph object
        # if engine is spark, self._graph is a spark graph object
        self._graph = raw_graph
        # let's keep unified interface as NebulaDataFrameObject
        self.data = self._graph

    def get_engine(self):
        return self.engine

    @property
    def algo(self):
        if self.engine.type == "spark":
            print(
                "NebulaGraphObject.algo is not supported in spark engine, "
                "please use NebulaDataFrameObject.algo instead"
            )
            raise NotImplementedError
        if self.engine.type == "nebula":
            from ng_ai.nebula_algo import NebulaAlgorithm as NebulaAlgorithmImpl

            return NebulaAlgorithmImpl(self)

    def get_nx_graph(self):
        if self.engine.type == "nebula":
            return self._graph
        else:
            # for now the else case will be spark, to networkx is not supported
            raise Exception(
                "For NebulaGraphObject in spark engine,"
                "convert to networkx graph is not supported",
            )

    def stats(self, *keywords, **kwargs):
        if self.engine.type == "spark":
            raise NotImplementedError
        elif self.engine.type == "nebula":
            print(self.data)

    def draw(self, with_labels=True, **kwargs):
        if self.engine.type == "nebula":
            self.engine.nx.draw(self.data, with_labels=with_labels, **kwargs)
        else:
            raise NotImplementedError

    def show(self, limit=None):
        if self.engine.type == "spark":
            raise NotImplementedError
        elif self.engine.type == "nebula":
            if limit is None:
                limit = 0
            for u, v, key, attrs in self.data.edges(keys=True, data=True):
                print(f"{u} -> {v} ({key}): {attrs}")
                limit -= 1
                if limit == 0:
                    break


class NebulaDataFrameObject:
    def __init__(self, engine, data):
        """
        data: pd.DataFrame or spark.DataFrame
        """
        self.engine = engine
        self.data = data
        # if engine is nebula, self.data is a pandas dataframe
        # if engine is spark, self.data is a spark dataframe

    def get_engine(self):
        return self.engine

    @property
    def algo(self):
        if self.engine.type == "spark":
            from ng_ai.nebula_algo import NebulaAlgorithm as NebulaAlgorithmImpl

            return NebulaAlgorithmImpl(self)
        else:
            print(
                "NebulaDataFrameObject.algo is not supported in nebula engine, "
                "please use NebulaGraphObject.algo instead"
            )
            raise NotImplementedError

    def get_spark_df(self):
        if self.engine.type == "spark":
            return self.data
        else:
            # convert pandas dataframe to spark dataframe
            # not implemented now
            raise NotImplementedError

    def to_pandas_df(self):
        if self.engine.type == "nebula":
            return self.data
        else:
            # convert the spark df to a pandas data frame
            # we should carefully think about this use case
            # not implemented now
            raise NotImplementedError

    def to_networkx(self):
        # for now the else case will be spark, to networkx is not supported
        raise Exception(
            "For NebulaDataFrameObject in spark engine,"
            "convert to networkx graph is not supported",
        )

    def to_graphx(self):
        if self.engine.type == "spark":
            df = self.data  # noqa: F841
            # convert the df to a graphx graph, not implemented now
            raise NotImplementedError
        else:
            # for now the else case will be nebula, to graphx is not supported
            raise Exception(
                "For NebulaDataFrameObject in nebula engine,"
                "convert to graphx is not supported",
            )

    def to_graph(self):
        raise NotImplementedError

    def show(self, *keywords, **kwargs):
        if self.engine.type == "spark":
            self.data.show(*keywords, **kwargs)
        elif self.engine.type == "nebula":
            print(self.data)
        else:
            raise NotImplementedError
