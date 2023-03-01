# Envrionment Setup

## With Nebula-UP

### Installation

```bash
curl -fsSL nebula-up.siwei.io/all-in-one.sh | bash -s -- v3 spark
```

> see [Nebula-UP](https://github.com/wey-gu/nebula-up) for more details.

Then load the basketballplayer dataset:

```bash
~/.nebula-up/load-basketballplayer-dataset.sh
```

### Access to PySpark Jupyter Notebook

Just visit [http://localhost:8888](http://localhost:8888) in your browser.

> The default password is `nebula`.

Open data_intelligence_suite_demo.ipynb and run the first cell to install ngdi, then you can run the rest cells.

### Access to NebulaGraph

Just visit [http://localhost:7001](http://localhost:7001) in your browser, with:

- host: `graphd:9669`
- user: `root`
- password: `nebula`
