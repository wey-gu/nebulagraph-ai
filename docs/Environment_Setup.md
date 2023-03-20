# Envrionment Setup

**TOC**

- [Quick Start in 5 Minutes](#with-nebula-upqiuck-start)
- [Run In Production](#in-production)
    - [Run on PySpark Jupyter Notebook](#run-on-pyspark-jupyter-notebook)
    - [Submit Algorithm job to Spark Cluster](#submit-algorithm-job-to-spark-cluster)
    - [Run ng_ai algorithm PySpark job from python script](#run-ng_ai-algorithm-pyspark-job-from-python-script)
    - [Run on single machine with NebulaGraph engine](#run-on-single-machine-with-nebulagraph-engine)

## With Nebula-UP(qiuck start)

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

Open data_intelligence_suite_demo.ipynb and run the first cell to install ng_ai, then you can run the rest cells.

### Access to NebulaGraph

Just visit [http://localhost:7001](http://localhost:7001) in your browser, with:

- host: `graphd:9669`
- user: `root`
- password: `nebula`

## Run In Production

### Run on PySpark Jupyter Notebook

Assuming we have put the `nebula-spark-connector.jar` and `nebula-algo.jar` in `/opt/nebulagraph/ng_ai/package/`.

```bash
export PYSPARK_PYTHON=python3
export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS="notebook --ip=0.0.0.0 --port=8888 --no-browser"

pyspark --driver-class-path /opt/nebulagraph/ng_ai/package/nebula-spark-connector.jar \
    --driver-class-path /opt/nebulagraph/ng_ai/package/nebula-algo.jar \
    --jars /opt/nebulagraph/ng_ai/package/nebula-spark-connector.jar \
    --jars /opt/nebulagraph/ng_ai/package/nebula-algo.jar
```

Then we could access Jupyter Notebook with PySpark and refer to [examples/spark_engine.ipynb](https://github.com/wey-gu/nebulagraph-ai/blob/main/examples/spark_engine.ipynb)

### Submit Algorithm job to Spark Cluster

Assuming we have put the `nebula-spark-connector.jar` and `nebula-algo.jar` in `/opt/nebulagraph/ng_ai/package/`;
We have put the `ng_ai-py3-env.zip` in `/opt/nebulagraph/ng_ai/package/`.
And we have the following Algorithm job in `pagerank.py`:

```python
from ng_ai import NebulaGraphConfig
from ng_ai import NebulaReader

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
spark-submit --master spark://sparkmaster:7077 \
    --driver-class-path <hdfs_or_local_path_to>/nebula-spark-connector.jar \
    --driver-class-path <hdfs_or_local_path_to>/nebula-algo.jar \
    --jars <hdfs_or_local_path_to>/nebula-spark-connector.jar \
    --jars <hdfs_or_local_path_to>/nebula-algo.jar \
    --py-files <hdfs_or_local_path_to>/ng_ai-py3-env.zip \
    pagerank.py
```

## Prepare for py-files

```bash
pip install pdm
# prepare dep list in ng_ai codebase
pdm export -o dist/requirements.txt --without-hashes
# build a wheel for ng_ai
pdm build
# output it to dependencies
pip install -r dist/requirements.txt --target dist/dependencies
pip install . --target dist/dependencies
# zip dependencies and ng_ai wheel
cd dist
zip -r ng_ai-py3-env.zip dependencies
# copy ng_ai-py3-env.zip to hdfs
hdfs dfs -put ng_ai-py3-env.zip /
# check it's there
hdfs dfs -ls /
```

Now we have all files ready:

```bash
# hdfs dfs -ls /
Found 4 items
-rw-r--r--   3 root supergroup  167042166 2023-03-17 03:54 /nebula-algo.jar
-rw-r--r--   3 root supergroup  165992037 2023-03-17 03:54 /nebula-spark-connector.jar
-rw-r--r--   3 root supergroup    5068513 2023-03-17 03:52 /ng_ai-py3-env.zip
```

### Run ng_ai algorithm PySpark job from python script

We have everything ready as above, including the `pagerank.py`.

```python
import subprocess

subprocess.run(["spark-submit", "--master", "spark://master:7077",
                "--driver-class-path", "/opt/nebulagraph/ng_ai/package/nebula-spark-connector.jar",
                "--driver-class-path", "/opt/nebulagraph/ng_ai/package/nebula-algo.jar",
                "--jars", "/opt/nebulagraph/ng_ai/package/nebula-spark-connector.jar",
                "--jars", "/opt/nebulagraph/ng_ai/package/nebula-algo.jar",
                "--py-files", "/opt/nebulagraph/ng_ai/package/ng_ai-py3-env.zip",
                "pagerank.py"])
```

### Run on single machine with NebulaGraph engine

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