# API Reference

## Table of contents

- [NebulaGraphConfig](#NebulaGraphConfig)
- [NebulaReader](#NebulaReader)
- [engines](#engines)
- [NebulaDataFrameObject](#NebulaDataFrameObject)
- [NebulaGraphObject](#NebulaGraphObject)
- [NebulaAlgorithm](#NebulaAlgorithm)
- [NebulaWriter](#NebulaWriter)
- [NebulaGNN](#NebulaGNN)

## NebulaGraphConfig

`ng_ai.NebulaGraphConfig` is the configuration for `ng_ai.NebulaReader`, `ng_ai.NebulaWriter` and `ng_ai.NebulaAlgorithm`.

See code for details: [ng_ai/config.py](../ng_ai/config.py)

## NebulaReader

`ng_ai.NebulaReader` reads data from NebulaGraph and constructs `NebulaDataFrameObject` or `NebulaGraphObject`.
It supports different engines, including Spark and NebulaGraph. The default engine is Spark.

Per each engine, `ng_ai.NebulaReader` supports different read modes, including query, scan, and load.
For now, Spark Engine supports query, scan and load modes, while NebulaGraph Engine supports query and scan modes.

In Spark Engine:
- All modes are underlyingly implemented by NebulaGraph Spark Connector nGQL Reader, while in the future, query mode will be optionally done by opencypher/morpheus to bypass the Nebula-GraphD.
- The `NebulaDataFrameObject` returned by `ng_ai.NebulaReader.read()` is a Spark DataFrame, which can be further processed by Spark SQL or Spark MLlib.

In NebulaGraph Engine:
- Query mode is implemented by Python Nebula-GraphD Client, while scan mode the Nebula-StoreageD Client.
- The `NebulaDataFrameObject` returned by `ng_ai.NebulaReader.read()` is a Pandas DataFrame, which can be further processed by Pandas. And the graph returned by ng_ai.

### Functions

- `ng_ai.NebulaReader.query()` sets the query statement.
- `ng_ai.NebulaReader.scan()` sets the scan statement.
- `ng_ai.NebulaReader.load()` sets the load statement. (not yet implemented)
- `ng_ai.NebulaReader.read()` executes the read operation and returns a DataFrame or `NebulaGraphObject`.
- `ng_ai.NebulaReader.show()` shows the DataFrame returned by `ng_ai.NebulaReader.read()`.

### Examples

#### Spark Engine

- Scan mode

```python
from ng_ai import NebulaReader
# read data with spark engine, scan mode
reader = NebulaReader(engine="spark")
reader.scan(edge="follow", props="degree")
df = reader.read()
```

- Query mode

```python
from ng_ai import NebulaReader
# read data with spark engine, query mode
reader = NebulaReader(engine="spark")
query = """
    MATCH ()-[e:follow]->()
    RETURN e LIMIT 100000
"""
reader.query(query=query, edge="follow", props="degree")
df = reader.read()
```

- Load mode

> not yet implemented

```python
# read data with spark engine, load mode (not yet implemented)
reader = NebulaReader(engine="spark")
reader.load(source="hdfs://path/to/edge.csv", format="csv", header=True, schema="src: string, dst: string, rank: int")
df = reader.read() # this will take some time
df.show(10)
```

#### NebulaGraph Engine(NetworkX)

```python
from ng_ai import NebulaReader
from ng_ai.config import NebulaGraphConfig
# read data with nebula engine, query mode
config_dict = {
    "graphd_hosts": "127.0.0.1:9669",
    "user": "root",
    "password": "nebula",
    "space": "basketballplayer",
}
config = NebulaGraphConfig(**config_dict)
reader = NebulaReader(engine="nebula", config=config)
reader.query(edges=["follow", "serve"], props=[["degree"],[]])
g = reader.read()
g.show(10)
g.draw()
```

## engines

- `ng_ai.engines.SparkEngine` is the Spark Engine for `ng_ai.NebulaReader`, `ng_ai.NebulaWriter` and `ng_ai.NebulaAlgorithm`.

- `ng_ai.engines.NebulaEngine` is the NebulaGraph Engine for `ng_ai.NebulaReader`, `ng_ai.NebulaWriter` and `ng_ai.NebulaAlgorithm`, which is based on NetworkX and Nebula-Python.

## `NebulaDataFrameObject`

ng_ai.`NebulaDataFrameObject` is a Spark DataFrame or Pandas DataFrame, which can be further processed by Spark SQL or Spark MLlib or Pandas.

### Functions

- `ng_ai.NebulaDataFrameObject.algo.pagerank()` runs the PageRank algorithm on the Spark DataFrame.
- `ng_ai.NebulaDataFrameObject.to_graphx()` converts the DataFrame to a GraphX Graph. not yet implemented.

## NebulaGraphObject

`ng_ai.NebulaGraphObject` is a GraphX Graph or NetworkX Graph, which can be further processed by GraphX or NetworkX.

### Functions

- `ng_ai.NebulaGraphObject.algo.get_all_algo()` returns all algorithms supported by the engine.
- `ng_ai.NebulaGraphObject.algo.pagerank()` runs the PageRank algorithm on the NetworkX Graph. not yet implemented.

## NebulaAlgorithm

`ng_ai.NebulaAlgorithm` is a collection of algorithms that can be run on ng_ai.`NebulaDataFrameObject`(spark engine) or `ng_ai.NebulaGraphObject`(networkx engine).

## NebulaWriter

`ng_ai.NebulaWriter` writes the computed or queried data to different sinks.
Supported sinks include:
- NebulaGraph(Spark Engine, NebulaGraph Engine)
- CSV(Spark Engine, NebulaGraph Engine)
- S3(Spark Engine, NebulaGraph Engine), not yet implemented.

### Functions

- `ng_ai.NebulaWriter.options()` sets the options for the sink.
- `ng_ai.NebulaWriter.write()` writes the data to the sink.
- `ng_ai.NebulaWriter.show_options()` shows the options for the sink.

### Examples

#### Spark Engine

- NebulaGraph sink

Assume that we have a Spark DataFrame `df_result` computed with `df.algo.louvain()` with the following schema:

```python
df_result.printSchema()
# result:
root
 |-- _id: string (nullable = false)
 |-- louvain: string (nullable = false)
```

We created a TAG `louvain` in NebulaGraph on same space with the following schema:

```ngql
CREATE TAG IF NOT EXISTS louvain (
    cluster_id string NOT NULL
);
```

Then, we could write the louvain result to NebulaGraph, map the column `louvain` to `cluster_id` with the following code:

```python
from ng_ai import NebulaWriter
from ng_ai.config import NebulaGraphConfig

config = NebulaGraphConfig()

properties = {
    "louvain": "cluster_id"
}

writer = NebulaWriter(data=df_result, sink="nebulagraph_vertex", config=config, engine="spark")
writer.set_options(
    tag="louvain",
    vid_field="_id",
    properties=properties,
    batch_size=256,
    write_mode="insert",
)
writer.write()
```

Then we could query the result in NebulaGraph:

```cypher
MATCH (v:louvain)
RETURN id(v), v.louvain.cluster_id LIMIT 10;
```

#### NebulaGraph Engine(NetworkX) Writer

Create schema in NebulaGraph:

```ngql
CREATE TAG IF NOT EXISTS pagerank (
    pagerank double NOT NULL
);
```

Assuming we have a `graph_result` computed with `graph.algo.pagerank()`:

```python
graph_result = g.algo.pagerank()
```

Then we could write the pagerank result back to NebulaGraph with the following code:

```python
from ng_ai import NebulaWriter

writer = NebulaWriter(
    data=graph_result,
    sink="nebulagraph_vertex",
    config=config,
    engine="nebula",
)

# properties to write
properties = ["pagerank"]

writer.set_options(
    tag="pagerank",
    properties=properties,
    batch_size=256,
    write_mode="insert",
)
# write back to NebulaGraph
writer.write()
```

## NebulaGNN

`ng_ai.NebulaGNN` is a collection of graph neural network models that can be run on ng_ai. not yet implemented.
