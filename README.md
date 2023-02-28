# ngdi

NebulaGraph Data Intelligence Suite

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
