import os

from ngdi import NebulaReader, NebulaWriter
from ngdi.config import NebulaGraphConfig

from flask import Flask, request

app = Flask(__name__)


def get_nebulagraph_config(space="basketballplayer"):
    # get credentials from env
    graphd_hosts = os.getenv("GRAPHD_HOSTS", "graphd:9669")
    metad_hosts = os.getenv("METAD_HOSTS", "metad0:9559,metad1:9559,metad2:9559")
    user = os.getenv("USER", "root")
    password = os.getenv("PASSWORD", "nebula")

    return NebulaGraphConfig(
        graphd_hosts=graphd_hosts,
        metad_hosts=metad_hosts,
        user=user,
        password=password,
        space=space,
    )


@app.route("/api/v0/spark", methods=["GET"])
def parallel_healthcheck():
    return {"status": "OK"}


@app.route("/api/v0/spark/<algo_name>", methods=["POST"])
def parallel(algo_name):
    data = request.get_json()

    try:
        # get algo_context
        algo_context = data.get("algo_context")
        assert algo_context is not None, "algo_context should not be None"
        assert algo_context.get("space") is not None, "space should not be None"
    except Exception as e:
        print(e)
        return {"error": f"algo context parsing failed: {e}"}
    space = algo_context.get("space")
    nebula_config = get_nebulagraph_config(space=space)

    reader = NebulaReader(engine="spark", config=nebula_config)
    # get read_context
    try:
        read_context = data.get("read_context")
        read_mode = read_context.get("read_mode")
        edges = read_context.get("edge_types")
        edge_weights = read_context.get("edge_weights")

        assert (
            len(edges) == len(edge_weights) and len(edges) > 0
        ), "edges and edge_weights should have the same length and length > 0"
        # TBD, it seems that the reader.scan() need to support more than one edge type
        # https://github.com/wey-gu/nebulagraph-di/issues/19
        # need to query all and union them.
        if read_mode == "scan":
            reader.scan(edge=edges[0], props=edge_weights[0])
        elif read_mode == "query":
            query = read_context.get("query")
            assert query is not None, "query should not be None"
            reader.query(query, edge=edges[0], props=edge_weights[0])
            # TODO(wey): need to revisit the query and scan API, to align them.
            # ref: https://github.com/vesoft-inc/nebula-algorithm/blob/master/nebula-algorithm/src/main/scala/com/vesoft/nebula/algorithm/Main.scala
            # ref: https://github.com/vesoft-inc/nebula-algorithm/blob/master/nebula-algorithm/src/main/scala/com/vesoft/nebula/algorithm/reader/DataReader.scala
            # ref: https://github.com/vesoft-inc/nebula-spark-connector/blob/master/example/src/main/scala/com/vesoft/nebula/examples/connector/NebulaSparkReaderExample.scala
        df = reader.read()
    except Exception as e:
        # TBD, need to return error code, return empty json for now
        print(e)
        return {"error": f"read failed: {e}"}
    try:
        # ensure the algo_name is supported
        assert algo_name in df.algo.get_all_algo(), f"{algo_name} is not supported"

        algo_config = dict(algo_context)
        algo_config.pop("space")
        algo_config.pop("name")
        # call df.algo.algo_name(**algo_config)
        algo_result = getattr(df.algo, algo_name)(**algo_config)
    except Exception as e:
        # TBD, need to return error code, return empty json for now
        print(e)
        return {"error": f"algo execution failed: {e}"}

    try:
        # get write_context
        write_context = data.get("write_context")
        write_mode = write_context.get("write_mode")
        properties = write_context.get("properties", {})
        batch_size = write_context.get("batch_size", 256)
        # TBD, need to support more than one edge type
        writer = NebulaWriter(
            data=algo_result,
            sink="nebulagraph_vertex",
            config=nebula_config,
            engine="spark",
        )
        writer.set_options(
            tag=algo_name,
            vid_field="_id",
            properties=properties,
            batch_size=batch_size,
            write_mode=write_mode,
        )
        response = writer.write()
    except Exception as e:
        # TBD, need to return error code, return empty json for now
        print(e)
        return {"error": f"write failed: {e}"}
    # return reader result's stats, algo result's stats, writer result
    return {
        "reader_result_stats": list(
            map(lambda r: r.asDict(), df.data.summary().collect())
        ),
        "algo_result_stats": list(
            map(lambda r: r.asDict(), writer.raw_df.summary().collect())
        ),
        "writer_result": response is None or response,
    }
