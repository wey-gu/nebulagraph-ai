import subprocess

from nebula3.Config import Config
from nebula3.gclient.net import ConnectionPool


def test_networkx_engine_query_reader():
    import networkx as nx

    from ng_ai import NebulaReader
    from ng_ai.config import NebulaGraphConfig

    # read data with spark engine, query mode
    config_dict = {
        "graphd_hosts": "127.0.0.1:39669",
        "user": "root",
        "password": "nebula",
        "space": "basketballplayer",
    }
    config = NebulaGraphConfig(**config_dict)
    reader = NebulaReader(engine="nebula", config=config)
    reader.query(edges=["follow", "serve"], props=[["degree"], []])
    g = reader.read()
    assert isinstance(g.data, nx.MultiDiGraph)
    g.show(10)


def test_networkx_engine_algo():
    """
    Test networkx engine with all algorithms
    """
    import networkx as nx

    from ng_ai import NebulaReader
    from ng_ai.config import NebulaGraphConfig

    # read data with spark engine, query mode
    config_dict = {
        "graphd_hosts": "127.0.0.1:39669",
        "user": "root",
        "password": "nebula",
        "space": "basketballplayer",
    }
    config = NebulaGraphConfig(**config_dict)
    reader = NebulaReader(engine="nebula", config=config)
    reader.query(edges=["follow", "serve"], props=[["degree"], []])
    g = reader.read()

    for algo_name in g.algo.get_all_algo():
        algo_func = getattr(g.algo, algo_name)
        print(f"Running {algo_name}...")
        result = algo_func()
        if hasattr(result, "__iter__"):
            for x in result:
                print(x)
        else:
            print(result)
        print("=" * 20)


def test_networkx_engine_writer():
    from ng_ai import NebulaReader, NebulaWriter
    from ng_ai.config import NebulaGraphConfig

    # read data with spark engine, query mode
    config_dict = {
        "graphd_hosts": "127.0.0.1:39669",
        "user": "root",
        "password": "nebula",
        "space": "basketballplayer",
    }
    config = NebulaGraphConfig(**config_dict)
    reader = NebulaReader(engine="nebula", config=config)
    reader.query(edges=["follow", "serve"], props=[["degree"], []])
    g = reader.read()

    graph_result = g.algo.louvain()

    writer = NebulaWriter(
        data=graph_result,
        sink="nebulagraph_vertex",
        config=config,
        engine="nebula",
    )

    # properties to write
    properties = ["cluster_id"]

    writer.set_options(
        tag="louvain",
        properties=properties,
        batch_size=256,
        write_mode="insert",
    )
    # write back to NebulaGraph
    writer.write()

    nebula_config = Config()
    connection_pool = ConnectionPool()
    connection_pool.init([("127.0.0.1", 39669)], nebula_config)

    with connection_pool.session_context("root", "nebula") as session:
        session.execute("USE basketballplayer")
        result = session.execute(
            "MATCH (v:louvain) RETURN id(v), v.louvain.cluster_id LIMIT 10;"
        )
        print(result)
    connection_pool.close()

    assert result.is_succeeded(), f"ERROR during query NebulaGraph: {result}"
    assert (
        not result.is_empty()
    ), f"louvain not written to NebulaGraph result: {result}"

    print(f"Label propagation result:\n{result}")
