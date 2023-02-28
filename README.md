# ngdi

NebulaGraph Data Intelligence Suite for Python (ngdi) is a Python library for NebulaGraph Data Intelligence.

## Installation

Prerequisites:
- Spark 2.4
- NebulaGraph 3.4+
- [NebulaGraph Spark Connector 3.4+](https://repo1.maven.org/maven2/com/vesoft/nebula-spark-connector/)
- [NebulaGraph Algorithm 3.4+](https://repo1.maven.org/maven2/com/vesoft/nebula-algorithm/)

```bash
pip install ngdi
```

## Run on PySpark Jupyter Notebook

Assuming we have put the `nebula-spark-connector.jar` and `nebula-algo.jar` in `/opt/nebulagraph/ngdi/package/`.

```bash
export PYSPARK_PYTHON=python3
export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS="notebook --ip=0.0.0.0 --port=8888 --no-browser"

pyspark --driver-class-path /opt/nebulagraph/ngdi/package/nebula-spark-connector.jar \
    --driver-class-path /opt/nebulagraph/ngdi/package/nebula-algo.jar \
    --jars /opt/nebulagraph/ngdi/package/nebula-spark-connector.jar \
    --jars /opt/nebulagraph/ngdi/package/nebula-algo.jar
```

## Submit to Spark Cluster

Assuming we have put the `nebula-spark-connector.jar` and `nebula-algo.jar` in `/opt/nebulagraph/ngdi/package/`;
We have put the `ngdi-py3-env.zip` in `/opt/nebulagraph/ngdi/package/`.
And we have the following Algorithm job in `pagerank.py`:

```python
from ngdi import NebulaGraphConfig
from ngdi import NebulaReader

# set NebulaGraph config
config_dict = {
    "graphd_hosts": "graphd:9669",
    "metad_hosts": "metad0:9669,metad1:9669,metad2:9669",
    "user": "root",
    "password": "nebula",
    "space": "basketballplayer",
}
config = NebulaGraphConfig(**config_dict)

# read data with spark engine, query mode
reader = NebulaReader(engine="spark")
query = """
    MATCH ()-[e:follow]->()
    RETURN e LIMIT 100000
"""
reader.query(query=query, edge="follow", props="degree")
df = reader.read()

# run pagerank algorithm
pr_result = df.algo.pagerank(reset_prob=0.15, max_iter=10) # this will take some time
```

Then we can submit the job to Spark cluster:

```bash
spark-submit --master spark://master:7077 \
    --driver-class-path /opt/nebulagraph/ngdi/package/nebula-spark-connector.jar \
    --driver-class-path /opt/nebulagraph/ngdi/package/nebula-algo.jar \
    --jars /opt/nebulagraph/ngdi/package/nebula-spark-connector.jar \
    --jars /opt/nebulagraph/ngdi/package/nebula-algo.jar \
    --py-files /opt/nebulagraph/ngdi/package/ngdi-py3-env.zip \
    pagerank.py
```

## Documentation

[API Reference](docs/API.md)

## Usage

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
