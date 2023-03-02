<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/1651790/221885742-80a9ba15-55f5-40df-80cb-934e60c02665.png">
  <img alt="NebulaGraph Data Intelligence Suite(ngdi)" src="https://user-images.githubusercontent.com/1651790/221876073-61ef4edb-adcd-4f10-b3fc-8ddc24918ea1.png">
</picture>

<p align="center">
    <em>Data Intelligence Suite with 4 line code to run Graph Algo on NebulaGraph</em>
</p>

<p align="center">
<a href="LICENSE" target="_blank">
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License">
</a>

<a href="https://badge.fury.io/py/ngdi" target="_blank">
    <img src="https://badge.fury.io/py/ngdi.svg" alt="PyPI version">
</a>

<a href="https://www.python.org/downloads/release/python-360/" target="_blank">
    <img src="https://img.shields.io/badge/python-3.6%2B-blue.svg" alt="Python">
</a>

<a href="https://pdm.fming.dev" target="_blank">
    <img src="https://img.shields.io/badge/pdm-managed-blueviolet" alt="pdm-managed">
</a>

</p>

---

**Documentation**: <a href="https://github.com/wey-gu/nebulagraph-di#documentation" target="_blank">https://github.com/wey-gu/nebulagraph-di#documentation</a>

**Source Code**: <a href="https://github.com/wey-gu/nebulagraph-di" target="_blank">https://github.com/wey-gu/nebulagraph-di</a>

---


NebulaGraph Data Intelligence Suite for Python (ngdi) is a powerful Python library that offers APIs for data scientists to effectively read, write, analyze, and compute data in NebulaGraph.

With the support of single-machine engine(NetworkX), or distributed computing environment using Spark we could perform Graph Analysis and Algorithms on top of NebulaGraph in less than 10 lines of code, in unified and intuitive API.

## Quick Start in 5 Minutes

- Setup env with Nebula-Up following [this guide](https://github.com/wey-gu/nebulagraph-di/blob/main/docs/Environment_Setup.md).
- Install ngdi with pip from the Jupyter Notebook with http://localhost:8888 (password: `nebula`).
- Open the demo notebook and run cells one by one.
- Check the [API Reference](https://github.com/wey-gu/nebulagraph-di/blob/main/docs/API.md)

## Installation

```bash
pip install ngdi
```

## Usage

### Spark Engine Examples

See also: [examples/spark_engine.ipynb](https://github.com/wey-gu/nebulagraph-di/blob/main/examples/spark_engine.ipynb)

Run Algorithm on top of NebulaGraph:

> Note, there is also query mode, refer to [examples](https://github.com/wey-gu/nebulagraph-di/blob/main/examples/spark_engine.ipynb) or [docs](https://github.com/wey-gu/nebulagraph-di/blob/main/docs/API.md) for more details.

```python
from ngdi import NebulaReader

# read data with spark engine, scan mode
reader = NebulaReader(engine="spark")
reader.scan(edge="follow", props="degree")
df = reader.read()

# run pagerank algorithm
pr_result = df.algo.pagerank(reset_prob=0.15, max_iter=10)
```

Write back to NebulaGraph:

```python
from ngdi import NebulaWriter
from ngdi.config import NebulaGraphConfig

config = NebulaGraphConfig()

properties = {"louvain": "cluster_id"}

writer = NebulaWriter(
    data=df_result, sink="nebulagraph_vertex", config=config, engine="spark")
writer.set_options(
    tag="louvain", vid_field="_id", properties=properties,
    batch_size=256, write_mode="insert",)
writer.write()
```

Then we could query the result in NebulaGraph:

```cypher
MATCH (v:louvain)
RETURN id(v), v.louvain.cluster_id LIMIT 10;
```

### NebulaGraph Engine Examples(not yet implemented)

Basically the same as Spark Engine, but with `engine="nebula"`.

```diff
- reader = NebulaReader(engine="spark")
+ reader = NebulaReader(engine="nebula")
```

## Documentation

[Environment Setup](https://github.com/wey-gu/nebulagraph-di/blob/main/docs/Environment_Setup.md)

[API Reference](https://github.com/wey-gu/nebulagraph-di/blob/main/docs/API.md)

## How it works

ngdi is an unified abstraction layer for different engines, the current implementation is based on Spark, NetworkX, DGL and NebulaGraph, but it's easy to extend to other engines like Flink, GraphScope, PyG etc.

```
        ┌───────────────────────────────────────────────────┐            
        │   Spark Cluster                                   │            
        │    .─────.    .─────.    .─────.    .─────.       │            
     ┌─▶│   :       ;  :       ;  :       ;  :       ;      │            
     │  │     `───'      `───'      `───'      `───'        │            
Algorithm                                                   │            
  Spark └───────────────────────────────────────────────────┘            
 Engine ┌────────────────────────────────────────────────────────────────┐
     └──┤                                                                │
        │   NebulaGraph Data Intelligence Suite(ngdi)                    │
        │     ┌────────┐    ┌──────┐    ┌────────┐   ┌─────┐             │
        │     │ Reader │    │ Algo │    │ Writer │   │ GNN │             │
        │     └────────┘    └──────┘    └────────┘   └─────┘             │
        │          ├────────────┴───┬────────┴─────┐    └──────┐         │
        │          ▼                ▼              ▼           ▼         │
        │   ┌─────────────┐ ┌──────────────┐ ┌──────────┐┌───────────┐   │
     ┌──┤   │ SparkEngine │ │ NebulaEngine │ │ NetworkX ││ DGLEngine │   │
     │  │   └─────────────┘ └──────────────┘ └──────────┘└───────────┘   │
     │  └──────────┬─────────────────────────────────────────────────────┘
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

### Spark Engine Prerequisites
- Spark 2.4, 3.0(not yet tested)
- [NebulaGraph 3.4+](https://github.com/vesoft-inc/nebula)
- [NebulaGraph Spark Connector 3.4+](https://repo1.maven.org/maven2/com/vesoft/nebula-spark-connector/)
- [NebulaGraph Algorithm 3.1+](https://repo1.maven.org/maven2/com/vesoft/nebula-algorithm/)

### NebulaGraph Engine Prerequisites
- [NebulaGraph 3.4+](https://github.com/vesoft-inc/nebula)
- [NebulaGraph Python Client 3.4+](https://github.com/vesoft-inc/nebula-python)
- [NetworkX](https://networkx.org/)

## License

This project is licensed under the terms of the Apache License 2.0.