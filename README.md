# ngdi

NebulaGraph Data Intelligence Suite

## API

### NebulaReader

ngdi.NebulaReader reads data from NebulaGraph and constructs NebulaDataFrameObject or NebulaGraphObject.
It supports different engines, including Spark and NebulaGraph. The default engine is Spark.

Per each engine, ngdi.NebulaReader supports different read modes, including query, scan, and load.
For now, Spark Engine supports query, scan and load modes, while NebulaGraph Engine supports query and scan modes.

In Spark Engine, all modes are underlyingly implemented by NebulaGraph Spark Connector nGQL Reader, while in the future, query mode will be optionally done by opencypher/morpheus to bypass the Nebula-GraphD.

The NebulaDataFrameObject returned by ngdi.NebulaReader.read() is a Spark DataFrame, which can be further processed by Spark SQL or Spark MLlib. And the graph returned by ngdi.NebulaReader.to_graph() is a GraphX Graph, which can be further processed by GraphX. In the future, the graph returned by ngdi.NebulaReader.to_graph() will support GraphFrame, too.

In NebulaGraph Engine, query mode is implemented by Python Nebula-GraphD Client, while scan mode the Nebula-StoreageD Client.

The NebulaDataFrameObject returned by ngdi.NebulaReader.read() is a Pandas DataFrame, which can be further processed by Pandas. And the graph returned by ngdi.NebulaReader.to_graph() is a NetworkX Graph, which can be further processed by NetworkX.

#### Functions

- ngdi.NebulaReader.query() sets the query statement.
- ngdi.NebulaReader.scan() sets the scan statement.
- ngdi.NebulaReader.load() sets the load statement.
- ngdi.NebulaReader.read() executes the read operation and returns a DataFrame or NebulaGraphObject.
- ngdi.NebulaReader.show() shows the DataFrame returned by ngdi.NebulaReader.read().

### NebulaDataFrameObject

ngdi.NebulaDataFrameObject is a Spark DataFrame or Pandas DataFrame, which can be further processed by Spark SQL or Spark MLlib or Pandas.

#### Functions

- ngdi.NebulaDataFrameObject.algo.pagerank() runs the PageRank algorithm on the Spark DataFrame.
- ngdi.NebulaDataFrameObject.to_graphx() converts the DataFrame to a GraphX Graph. not yet implemented.

### NebulaGraphObject

ngdi.NebulaGraphObject is a GraphX Graph or NetworkX Graph, which can be further processed by GraphX or NetworkX.

#### Functions

- ngdi.NebulaGraphObject.algo.pagerank() runs the PageRank algorithm on the NetworkX Graph. not yet implemented.

### NebulaAlgorithm

ngdi.NebulaAlgorithm is a collection of algorithms that can be run on ngdi.NebulaDataFrameObject(spark engine) or ngdi.NebulaGraphObject(networkx engine).

### NebulaGNN

ngdi.NebulaGNN is a collection of graph neural network models that can be run on ngdi. not yet implemented.

## Examples

### Spark Engine Examples

See also: [examples/spark_engine.ipynb](examples/spark_engine.ipynb)

```python
from ngdi import NebulaReader

# read data with spark engine, query mode
reader = NebulaReader(engine="spark")
query = """
    MATCH ()-[e:follow]->()
    RETURN e LIMIT 100000
"""
reader.query(query=query, edge="follow", props="degree")
df = reader.read() # this will take some time
df.show(10)

# read data with spark engine, scan mode
reader = NebulaReader(engine="spark")
reader.scan(edge="follow", props="degree")
df = reader.read() # this will take some time
df.show(10)

# read data with spark engine, load mode (not yet implemented)
reader = NebulaReader(engine="spark")
reader.load(source="hdfs://path/to/edge.csv", format="csv", header=True, schema="src: string, dst: string, rank: int")
df = reader.read() # this will take some time
df.show(10)

# run pagerank algorithm
pr_result = df.algo.pagerank(reset_prob=0.15, max_iter=10) # this will take some time

# convert dataframe to NebulaGraphObject
graph = reader.to_graphx() # not yet implemented
```

### NebulaGraph Engine Examples(not yet implemented)

```python
from ngdi import NebulaReader

# read data with nebula engine, query mode
reader = NebulaReader(engine="nebula")
reader.query("""
    MATCH ()-[e:follow]->()
    RETURN e.src, e.dst, e.degree LIMIT 100000
""")
df = reader.read() # this will take some time
df.show(10)

# read data with nebula engine, scan mode
reader = NebulaReader(engine="nebula")
reader.scan(edge_types=["follow"])
df = reader.read() # this will take some time
df.show(10)

# convert dataframe to NebulaGraphObject
graph = reader.to_graph() # this will take some time
graph.nodes.show(10)
graph.edges.show(10)

# run pagerank algorithm
pr_result = graph.algo.pagerank(reset_prob=0.15, max_iter=10) # this will take some time
```
