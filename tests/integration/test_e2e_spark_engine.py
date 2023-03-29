import subprocess

from nebula3.Config import Config
from nebula3.gclient.net import ConnectionPool


def test_scan_reader_spark_engine():
    """
    Just call:
    /spark/bin/spark-submit \
        --jars /root/download/nebula-algo.jar \
        /root/run/scan_reader.py
    in container: master_spark
    assert the return value is 0
    """

    result = subprocess.run(
        "docker exec master_spark /spark/bin/spark-submit "
        "--jars /root/download/nebula-algo.jar "
        "/root/run/scan_reader.py",
        shell=True,
        check=True,
        capture_output=True,
    )

    assert result.returncode == 0, f"ERROR during run scan_reader.py: {result}"
    print(f"Scan reader result:\n{result.stdout.decode('utf-8')}")


def test_scan_reader_spark_engine_and_run_pagerank():
    """
    Just call:
    /spark/bin/spark-submit \
        --jars /root/download/nebula-algo.jar \
        /root/run/algo.py
    in container: master_spark
    assert the return value is 0
    """

    result = subprocess.run(
        "docker exec master_spark /spark/bin/spark-submit "
        "--jars /root/download/nebula-algo.jar "
        "/root/run/algo.py",
        shell=True,
        check=True,
        capture_output=True,
    )

    assert result.returncode == 0, f"ERROR during run algo.py: {result}"
    print(f"Scan reader result:\n{result.stdout.decode('utf-8')}")


def test_query_reader_spark_engine():
    """
    Just call:
    /spark/bin/spark-submit \
        --jars /root/download/nebula-algo.jar \
        /root/run/query_reader.py
    in container: master_spark
    assert the return value is 0
    """

    result = subprocess.run(
        "docker exec master_spark /spark/bin/spark-submit "
        "--jars /root/download/nebula-algo.jar "
        "/root/run/query_reader.py",
        shell=True,
        check=True,
        capture_output=True,
    )

    assert result.returncode == 0, f"ERROR during run query_reader.py: {result}"
    print(f"Query reader result:\n{result.stdout.decode('utf-8')}")


def test_label_propagation_spark_engine_writer():
    """
    Just call:
    /spark/bin/spark-submit \
        --jars /root/download/nebula-algo.jar \
        /root/run/writer.py
    in container: master_spark
    assert the return value is 0
    Then query NebulaGraph on tag: label_propagation
    assert the result is correct
    """

    result = subprocess.run(
        "docker exec master_spark /spark/bin/spark-submit "
        "--jars /root/download/nebula-algo.jar "
        "/root/run/writer.py",
        shell=True,
        check=True,
        capture_output=True,
    )

    assert result.returncode == 0, f"ERROR during run writer.py: {result}"
    print(f"Label propagation result:\n{result.stdout.decode('utf-8')}")

    nebula_config = Config()
    connection_pool = ConnectionPool()
    connection_pool.init([("127.0.0.1", 39669)], nebula_config)

    with connection_pool.session_context("root", "nebula") as session:
        session.execute("USE basketballplayer")
        result = session.execute(
            "MATCH (v:player) RETURN v.label_propagation.cluster_id LIMIT 1"
        )
        print(result)
    connection_pool.close()

    assert result.is_succeeded(), f"ERROR during query NebulaGraph: {result}"
    assert (
        not result.is_empty()
    ), f"label_propagation not written to NebulaGraph result: {result}"
    assert (
        result.column_values("v.label_propagation.cluster_id")[0]
        .cast()
        .startswith("player")
    ), f"label_propagation value is not correct result: {result}"
    print(f"Label propagation result:\n{result}")
