# API Reference

## NebulaGraphConfig

`ngdi.NebulaGraphConfig` is the configuration for `ngdi.NebulaReader`, `ngdi.NebulaWriter` and `ngdi.NebulaAlgorithm`.

See code for details: [ngdi/config.py](../ngdi/config.py)

## NebulaReader

`ngdi.NebulaReader` reads data from NebulaGraph and constructs `NebulaDataFrameObject` or `NebulaGraphObject`.
It supports different engines, including Spark and NebulaGraph. The default engine is Spark.

Per each engine, `ngdi.NebulaReader` supports different read modes, including query, scan, and load.
For now, Spark Engine supports query, scan and load modes, while NebulaGraph Engine supports query and scan modes.

In Spark Engine:
- All modes are underlyingly implemented by NebulaGraph Spark Connector nGQL Reader, while in the future, query mode will be optionally done by opencypher/morpheus to bypass the Nebula-GraphD.
- The `NebulaDataFrameObject` returned by `ngdi.NebulaReader.read()` is a Spark DataFrame, which can be further processed by Spark SQL or Spark MLlib.

In NebulaGraph Engine:
- Query mode is implemented by Python Nebula-GraphD Client, while scan mode the Nebula-StoreageD Client.
- The `NebulaDataFrameObject` returned by `ngdi.NebulaReader.read()` is a Pandas DataFrame, which can be further processed by Pandas. And the graph returned by ngdi.

### Functions

- `ngdi.NebulaReader.query()` sets the query statement.
- `ngdi.NebulaReader.scan()` sets the scan statement.
- `ngdi.NebulaReader.load()` sets the load statement.
- `ngdi.NebulaReader.read()` executes the read operation and returns a DataFrame or `NebulaGraphObject`.
- `ngdi.NebulaReader.show()` shows the DataFrame returned by `ngdi.NebulaReader.read()`.

## engines

- `ngdi.engines.SparkEngine` is the Spark Engine for `ngdi.NebulaReader`, `ngdi.NebulaWriter` and `ngdi.NebulaAlgorithm`.

- `ngdi.engines.NebulaEngine` is the NebulaGraph Engine for `ngdi.NebulaReader`, `ngdi.NebulaWriter`.

- `ngdi.engines.NetworkXEngine` is the NetworkX Engine for `ngdi.NebulaAlgorithm`.

## `NebulaDataFrameObject`

ngdi.`NebulaDataFrameObject` is a Spark DataFrame or Pandas DataFrame, which can be further processed by Spark SQL or Spark MLlib or Pandas.

### Functions

- `ngdi.NebulaDataFrameObject.algo.pagerank()` runs the PageRank algorithm on the Spark DataFrame.
- `ngdi.NebulaDataFrameObject.to_graphx()` converts the DataFrame to a GraphX Graph. not yet implemented.

## NebulaGraphObject

`ngdi.NebulaGraphObject` is a GraphX Graph or NetworkX Graph, which can be further processed by GraphX or NetworkX.

### Functions

- `ngdi.NebulaGraphObject.algo.get_all_algo()` returns all algorithms supported by the engine.
- `ngdi.NebulaGraphObject.algo.pagerank()` runs the PageRank algorithm on the NetworkX Graph. not yet implemented.

## NebulaAlgorithm

`ngdi.NebulaAlgorithm` is a collection of algorithms that can be run on ngdi.`NebulaDataFrameObject`(spark engine) or `ngdi.NebulaGraphObject`(networkx engine).

## NebulaGNN

`ngdi.NebulaGNN` is a collection of graph neural network models that can be run on ngdi. not yet implemented.
