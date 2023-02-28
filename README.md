# NebulaGraph Data Intelligence(ngdi) Suite

![](https://user-images.githubusercontent.com/1651790/221790471-d4e5b487-9fc3-4126-ba50-77875a0e1686.jpeg)

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE) [![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/release/python-360/) [![PyPI version](https://badge.fury.io/py/ngdi.svg)](https://badge.fury.io/py/ngdi)

NebulaGraph Data Intelligence Suite for Python (ngdi) is a Python library for NebulaGraph Data Intelligence.

ngdi provides a set of APIs for data scientists to read, write and analyze/compute data in NebulaGraph, on single(NetworkX for now) machine or distributed(Spark for now) cluster.
```
        ┌───────────────────────────────────────────────────┐            
        │   Spark Cluster                                   │            
        │    .─────.    .─────.    .─────.    .─────.       │            
     ┌─▶│   :       ;  :       ;  :       ;  :       ;      │            
     │  │     `───'      `───'      `───'      `───'        │            
Algorithm                                                   │            
  Spark └───────────────────────────────────────────────────┘            
 Engine ┌───────────────────────────────────────────────────────────────┐
     └──┤                                                               │
        │   NebulaGraph Data Intelligence Suite(ngdi)                   │
        │     ┌────────┐    ┌──────┐    ┌────────┐   ┌─────┐            │
        │     │ Reader │    │ Algo │    │ Writer │   │ GNN │            │
        │     └────────┘    └──────┘    └────────┘   └─────┘            │
        │          ├────────────┴───┬────────┴─────┐    └──────┐        │
        │          ▼                ▼              ▼           ▼        │
        │   ┌─────────────┐ ┌──────────────┐ ┌──────────┐┌──────────┐   │
     ┌──┤   │ SparkEngine │ │ NebulaEngine │ │ NetworkX ││ DGLEngine│   │
     │  │   └─────────────┘ └──────────────┘ └──────────┘└──────────┘   │
     │  └──────────┬────────────────────────────────────────────────────┘
     │             │        Spark                                        
     │             └────────Reader ────────────┐                         
Spark Reader              Query Mode           │                         
Scan Mode                                      ▼                         
     │  ┌───────────────────────────────────────────────────┐            
     │  │  NebulaGraph Graph Engine         Nebula-GraphD   │            
     │  ├──────────────────────────────┬────────────────────┤            
     │  │  NebulaGraph Storage Engine  │                    │            
     └─▶│  Nebula-StorageD             │    Nebula-Metad    │            
        └──────────────────────────────┴────────────────────┘            
```

## Installation

```bash
pip install ngdi
```

### Spark Engine Prerequisites
- Spark 2.4, 3.0(not yet tested)
- [NebulaGraph 3.4+](https://github.com/vesoft-inc/nebula)
- [NebulaGraph Spark Connector 3.4+](https://repo1.maven.org/maven2/com/vesoft/nebula-spark-connector/)
- [NebulaGraph Algorithm 3.4+](https://repo1.maven.org/maven2/com/vesoft/nebula-algorithm/)

### NebulaGraph Engine Prerequisites
- [NebulaGraph 3.4+](https://github.com/vesoft-inc/nebula)
- [NebulaGraph Python Client 3.4+](https://github.com/vesoft-inc/nebula-python)
- [NetworkX](https://networkx.org/)

## Run on PySpark Jupyter Notebook(Spark Engine)

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

## Submit Algorithm job to Spark Cluster(Spark Engine)

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
pr_result = df.algo.pagerank(reset_prob=0.15, max_iter=10)
```

> Note, this could be done by Airflow, or other job scheduler in production.

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

## Run ngdi algorithm job from python script(Spark Engine)

We have everything ready as above, including the `pagerank.py`.

```python
import subprocess

subprocess.run(["spark-submit", "--master", "spark://master:7077",
                "--driver-class-path", "/opt/nebulagraph/ngdi/package/nebula-spark-connector.jar",
                "--driver-class-path", "/opt/nebulagraph/ngdi/package/nebula-algo.jar",
                "--jars", "/opt/nebulagraph/ngdi/package/nebula-spark-connector.jar",
                "--jars", "/opt/nebulagraph/ngdi/package/nebula-algo.jar",
                "--py-files", "/opt/nebulagraph/ngdi/package/ngdi-py3-env.zip",
                "pagerank.py"])
```

## Run on single machine(NebulaGraph Engine)

Assuming we have NebulaGraph cluster up and running, and we have the following Algorithm job in `pagerank_nebula_engine.py`:

This file is the same as `pagerank.py` except for the following line:

```diff
- reader = NebulaReader(engine="spark")
+ reader = NebulaReader(engine="nebula")
```

Then we can run the job on single machine:

```bash
python3 pagerank.py
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
