
# ngdi API Gateway

ngdi API Gateway is a RESTful API server that provides a unified interface for ngdi algorithms.

With ngdi API Gateway and ngdi UDF, we could call ngdi algorithms from ngql.

## Playground in 5 minutes

```bash
curl -fsSL nebula-up.siwei.io/all-in-one.sh | bash -s -- v3 spark
```

> see [Nebula-UP](https://github.com/wey-gu/nebula-up) for more details.

Then load the basketballplayer dataset:

```bash
~/.nebula-up/load-basketballplayer-dataset.sh
```

And start ngdi API Gateway from PySpark Jupyter Notebook:

Go to http://localhost:8888, open data_intelligence_suite_nGQL_UDF.ipynb and run the first cell to start the ngdi API Gateway.

Call ngdi from NebulaGraph studio: http://localhost:7001 , **note** the host to login is `ngdi_graphd` `9669`.
Run query in the console:

```cypher
RETURN ngdi("pagerank", ["follow"], ["degree"], "spark",
            {space: "basketballplayer"})
```


## Calling from ngql

```cypher
RETURN ngdi("pagerank", ["follow"], ["degree"], "spark", {space: "basketballplayer", max_iter: 10}, {write_mode: "insert"})
```

## Setup ngdi API Gateway

For Spark engine, we could run it from the Spark Juptyer Notebook, see: [../examples/ngdi_from_ngql_udf.ipynb](https://github.com/wey-gu/nebulagraph-di/blob/main/examples/ngdi_from_ngql_udf.ipynb)

For NetworkX engine, we could run it in same way as it was in Jupyter Notebook, see: [../examples/run_ngdi_api.py](https://github.com/wey-gu/nebulagraph-di/blob/main/examples/run_ngdi_api.py)

Or you could call with `pdm`:

```bash
export NGDI_PORT=9999
pdm run ngdi-api
```

## UDF build

See https://github.com/wey-gu/nebula/tree/ngdi_udf

### Build binary `ngdi.so` file

Clone the `nebula` repo and checkout the hash of your existing nebulagraph cluster(check with `SHOW HOSTS GRAPH`)

```bash
git clone https://github.com/vesoft-inc/nebula && cd nebula
```

Prepare nebula_dev docker container for building UDF.

```bash
export TAG=ubuntu2004
docker run -ti \
  --network nebula-net \
  --security-opt seccomp=unconfined \
  -v "$PWD":/home/nebula \
  -w /home/nebula \
  --name nebula_dev \
  vesoft/nebula-dev:$TAG \
  bash

mkdir build && cd build
cmake -DCMAKE_CXX_COMPILER=$TOOLSET_CLANG_DIR/bin/g++ -DCMAKE_C_COMPILER=$TOOLSET_CLANG_DIR/bin/gcc -DENABLE_WERROR=OFF -DCMAKE_BUILD_TYPE=Release -DENABLE_TESTING=OFF ..

Build the `ngdi.so` file.

```bash
cd ../udf
make UDF=ngdi
```

## Setup ngdi-graphd

The ngdi-graphd is just a graphd with ngdi UDF installed.

We just need to put the `ngdi.so` file into one path of graphd like `/udf/`, and then set the `--udf_path` to this path together with `--enable_udf=true`.

- Note that the `ngdi.so` file should be built in the same environment as the graphd.
- The ngdi.so should be granted the `x` permission. (`chmod +x ngdi.so`)
- The ngdi-api's url should be set in the `ngdi_gateway_url_prefix` environment variable. i.e. `export ngdi_gateway_url_prefix=http://jupyter:9999"`.

Example docker compose:

```yaml
  graphd:
    image: weygu/ngdi-graphd:2023.03.13
    container_name: ngdi_graphd
    environment:
      USER: root
      TZ:   "${TZ:-Asia/Shanghai}"
      ngdi_gateway_url_prefix: "http://jupyter:9999"
    command:
      - --meta_server_addrs=metad0:9559,metad1:9559,metad2:9559
      - --port=9669
      - --local_ip=ngdi_graphd
      - --ws_ip=ngdi_graphd
      - --ws_http_port=19669
      - --log_dir=/logs
      - --v=5
      - --enable_udf=true
      - --udf_path=/udf/
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://ngdi_graphd:19669/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s
    ports:
      - "29669:9669"
      - 19669
      - 19670
    volumes:
      - ./logs/graph:/logs
      - ./udf:/udf
    networks:
      - nebula-net
    restart: on-failure
    cap_add:
      - SYS_PTRACE
```