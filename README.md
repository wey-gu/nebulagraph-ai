<img alt="NebulaGraph AI Suite(ng_ai)" src="https://user-images.githubusercontent.com/1651790/226242809-fe488ff2-bb4a-4e7d-b23a-70865a7b3228.png">

<p align="center">
    <em>NebulaGraph AI Suite with 4 line code to run Graph Algo on NebulaGraph</em>
</p>

<p align="center">
<a href="LICENSE" target="_blank">
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License">
</a>

<a href="https://badge.fury.io/py/ng_ai" target="_blank">
    <img src="https://badge.fury.io/py/ng_ai.svg" alt="PyPI version">
</a>

<!-- <a href="https://www.python.org/downloads/release/python-360/" target="_blank">
    <img src="https://img.shields.io/badge/python-3.6%2B-blue.svg" alt="Python">
</a> -->

<a href="https://pdm.fming.dev" target="_blank">
    <img src="https://img.shields.io/badge/pdm-managed-blueviolet" alt="pdm-managed">
</a>

<a href="https://github.com/wey-gu/nebulagraph-ai/actions/workflows/ci.yml">
  <img src="https://github.com/wey-gu/nebulagraph-ai/actions/workflows/ci.yml/badge.svg" alt="Tests">
</a>

<img src="https://img.shields.io/badge/Python-3.9-blue.svg" alt="Python 3.9">

</p>

---

**Documentation**: <a href="https://github.com/wey-gu/nebulagraph-ai#documentation" target="_blank">https://github.com/wey-gu/nebulagraph-ai#documentation</a>

**Source Code**: <a href="https://github.com/wey-gu/nebulagraph-ai" target="_blank">https://github.com/wey-gu/nebulagraph-ai</a>

---


NebulaGraph AI Suite for Python (ng_ai) is a powerful Python library that offers APIs for data scientists to effectively read, write, analyze, and compute data in NebulaGraph.

With the support of single-machine engine(NetworkX), or distributed computing environment using Spark we could perform Graph Analysis and Algorithms on top of NebulaGraph in less than 10 lines of code, in unified and intuitive API.

## Quick Start in 5 Minutes

**Option 1**: Try on your Desktop? Go with [NebulaGraph Docker Extension](https://hub.docker.com/extensions/weygu/nebulagraph-dd-ext)!

**Option 2**: On Linux Server? Go with Nebula-Up 👇🏻

- Setup env with Nebula-Up following [this guide](https://github.com/wey-gu/nebulagraph-ai/blob/main/docs/Environment_Setup.md).
- Install ng_ai with pip from the Jupyter Notebook with http://localhost:8888 (password: `nebula`).
- Open the demo notebook and run cells one by one.
- Check the [API Reference](https://github.com/wey-gu/nebulagraph-ai/blob/main/docs/API.md)

## Installation

```bash
pip install ng_ai
```

## Usage

### Call from nGQL

See more details in [docs](https://github.com/wey-gu/nebulagraph-ai/blob/main/docs/ng_ai_API_Gateway.md)

```cypher
RETURN ng_ai("pagerank", ["follow"], ["degree"], "spark",
    {space: "basketballplayer", max_iter: 10}, {write_mode: "insert"})
```

### Spark Engine Examples

See also: [examples/spark_engine.ipynb](https://github.com/wey-gu/nebulagraph-ai/blob/main/examples/spark_engine.ipynb)

Run Algorithm on top of NebulaGraph:

> Note, there is also query mode, refer to [examples](https://github.com/wey-gu/nebulagraph-ai/blob/main/examples/spark_engine.ipynb) or [docs](https://github.com/wey-gu/nebulagraph-ai/blob/main/docs/API.md) for more details.

```python
from ng_ai import NebulaReader

# read data with spark engine, scan mode
reader = NebulaReader(engine="spark")
reader.scan(edge="follow", props="degree")
df = reader.read()

# run pagerank algorithm
pr_result = df.algo.pagerank(reset_prob=0.15, max_iter=10)
```

Write back to NebulaGraph:

```python
from ng_ai import NebulaWriter
from ng_ai.config import NebulaGraphConfig

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

[Environment Setup](https://github.com/wey-gu/nebulagraph-ai/blob/main/docs/Environment_Setup.md)

[API Reference](https://github.com/wey-gu/nebulagraph-ai/blob/main/docs/API.md)

## How it works

ng_ai is an unified abstraction layer for different engines, the current implementation is based on Spark, NetworkX, DGL and NebulaGraph, but it's easy to extend to other engines like Flink, GraphScope, PyG etc.

```
          ┌───────────────────────────────────────────────────┐
          │   Spark Cluster                                   │
          │    .─────.    .─────.    .─────.    .─────.       │
          │   ;       :  ;       :  ;       :  ;       :      │
       ┌─▶│   :       ;  :       ;  :       ;  :       ;      │
       │  │    ╲     ╱    ╲     ╱    ╲     ╱    ╲     ╱       │
       │  │     `───'      `───'      `───'      `───'        │
  Algo Spark                                                  │
    Engine└───────────────────────────────────────────────────┘
       │  ┌────────────────────────────────────────────────────┬──────────┐
       └──┤                                                    │          │
          │   NebulaGraph AI Suite(ngai)                       │ ngai-api │◀─┐
          │                                                    │          │  │
          │                                                    └──────────┤  │
          │     ┌────────┐    ┌──────┐    ┌────────┐   ┌─────┐            │  │
          │     │ Reader │    │ Algo │    │ Writer │   │ GNN │            │  │
 ┌───────▶│     └────────┘    └──────┘    └────────┘   └─────┘            │  │
 │        │          │            │            │          │               │  │
 │        │          ├────────────┴───┬────────┴─────┐    └──────┐        │  │
 │        │          ▼                ▼              ▼           ▼        │  │
 │        │   ┌─────────────┐ ┌──────────────┐ ┌──────────┐┌──────────┐   │  │
 │     ┌──┤   │ SparkEngine │ │ NebulaEngine │ │ NetworkX ││ DGLEngine│   │  │
 │     │  │   └─────────────┘ └──────────────┘ └──────────┘└──────────┘   │  │
 │     │  └──────────┬────────────────────────────────────────────────────┘  │
 │     │             │        Spark                                          │
 │     │             └────────Reader ────────────┐                           │
 │  Spark                   Query Mode           │                           │
 │  Reader                                       │                           │
 │Scan Mode                                      ▼                      ┌─────────┐
 │     │  ┌───────────────────────────────────────────────────┬─────────┤ ngai-udf│◀─────────────┐
 │     │  │                                                   │         └─────────┤              │
 │     │  │  NebulaGraph Graph Engine         Nebula-GraphD   │   ngai-GraphD     │              │
 │     │  ├──────────────────────────────┬────────────────────┼───────────────────┘              │
 │     │  │                              │                    │                                  │
 │     │  │  NebulaGraph Storage Engine  │                    │                                  │
 │     │  │                              │                    │                                  │
 │     └─▶│  Nebula-StorageD             │    Nebula-Metad    │                                  │
 │        │                              │                    │                                  │
 │        └──────────────────────────────┴────────────────────┘                                  │
 │                                                                                               │
 │    ┌───────────────────────────────────────────────────────────────────────────────────────┐  │
 │    │ RETURN ng_ai("pagerank", ["follow"], ["degree"], "spark", {space:"basketballplayer"}) │──┘
 │    └───────────────────────────────────────────────────────────────────────────────────────┘
 │  ┌─────────────────────────────────────────────────────────────┐
 │  │ from ng_ai import NebulaReader                              │
 │  │                                                             │
 │  │ # read data with spark engine, scan mode                    │
 │  │ reader = NebulaReader(engine="spark")                       │
 │  │ reader.scan(edge="follow", props="degree")                  │
 └──│ df = reader.read()                                          │
    │                                                             │
    │ # run pagerank algorithm                                    │
    │ pr_result = df.algo.pagerank(reset_prob=0.15, max_iter=10)  │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘  
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


## Contributing

See [HACKING.md](https://github.com/wey-gu/nebulagraph-ai/blob/main/HACKING.md) for details.

## License

This project is licensed under the terms of the Apache License 2.0.
