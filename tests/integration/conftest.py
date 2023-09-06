import os
import subprocess
from time import sleep

import pytest


@pytest.fixture(scope="session", autouse=True)
def prepare_data():
    print("Setup data...")
    subprocess.run(
        "docker run --rm --network setup_ngai-net vesoft/nebula-console:v3"
        ' -addr graphd -port 9669 -u root -p nebula -e " '
        'DROP SPACE basketballplayer;" ',
        shell=True,
        check=True,
    )
    sleep(4)
    result = subprocess.run(
        "docker run --rm --network setup_ngai-net vesoft/nebula-console:v3"
        ' -addr graphd -port 9669 -u root -p nebula -e " '
        ':play basketballplayer" ',
        shell=True,
        check=True,
        capture_output=True,
        timeout=300,
    )
    print(f":play basketballplayer: {result}")

    subprocess.run(
        "docker run --rm --network setup_ngai-net vesoft/nebula-console:v3"
        ' -addr graphd -port 9669 -u root -p nebula -e " '
        'USE basketballplayer; SUBMIT JOB STATS" ',
        shell=True,
        check=True,
        capture_output=True,
    )

    result = subprocess.run(
        "docker run --rm --network setup_ngai-net vesoft/nebula-console:v3"
        ' -addr graphd -port 9669 -u root -p nebula -e " '
        "USE basketballplayer; "
        "CREATE TAG IF NOT EXISTS label_propagation "
        '(cluster_id string NOT NULL);" ',
        shell=True,
        check=True,
        capture_output=True,
    )
    sleep(4)
    assert (
        b"ERROR" not in result.stdout
    ), f"ERROR during create tag: {result.stdout.decode('utf-8')}"

    result = subprocess.run(
        "docker run --rm --network setup_ngai-net vesoft/nebula-console:v3"
        ' -addr graphd -port 9669 -u root -p nebula -e " '
        "USE basketballplayer; "
        "CREATE EDGE IF NOT EXISTS jaccard_similarity "
        '(similarity double);" ',
        shell=True,
        check=True,
        capture_output=True,
    )
    sleep(4)
    assert (
        b"ERROR" not in result.stdout
    ), f"ERROR during create edge: {result.stdout.decode('utf-8')}"

    result = subprocess.run(
        "docker run --rm --network setup_ngai-net vesoft/nebula-console:v3"
        ' -addr graphd -port 9669 -u root -p nebula -e " '
        "USE basketballplayer; "
        'SHOW STATS;" ',
        shell=True,
        check=True,
        capture_output=True,
    )
    print(f"Show stats:\n{result.stdout.decode('utf-8')}")

    os.system("mkdir -p tests/integration/setup/run")
    os.system("rm -rf tests/integration/setup/run/*")

    os.system(
        "cp -r tests/integration/spark_engine_cases/* tests/integration/setup/run/"
    )

    # create louvain schema for networkx engine writer test
    # RUN:
    # CREATE TAG IF NOT EXISTS louvain (
    #     cluster_id string NOT NULL
    # );

    result = subprocess.run(
        "docker run --rm --network setup_ngai-net vesoft/nebula-console:v3"
        ' -addr graphd -port 9669 -u root -p nebula -e " '
        "USE basketballplayer; "
        "CREATE TAG IF NOT EXISTS louvain "
        '(cluster_id string NOT NULL);" ',
        shell=True,
        check=True,
        capture_output=True,
    )
    sleep(10)
    # check the schema existence with DESC TAG louvain:
    result = subprocess.run(
        "docker run --rm --network setup_ngai-net vesoft/nebula-console:v3"
        ' -addr graphd -port 9669 -u root -p nebula -e " '
        "USE basketballplayer; "
        'DESC TAG louvain;" ',
        shell=True,
        check=True,
        capture_output=True,
    )
    print(f"DESC TAG louvain:\n{result.stdout.decode('utf-8')}")
    assert (
        b"ERROR" not in result.stdout
    ), f"ERROR during create tag: {result.stdout.decode('utf-8')}"

    # check the schema existence with DESC EDGE jaccard_similarity:
    result = subprocess.run(
        "docker run --rm --network setup_ngai-net vesoft/nebula-console:v3"
        ' -addr graphd -port 9669 -u root -p nebula -e " '
        "USE basketballplayer; "
        'DESC EDGE jaccard_similarity;" ',
        shell=True,
        check=True,
        capture_output=True,
    )
    print(f"DESC EDGE jaccard_similarity:\n{result.stdout.decode('utf-8')}")
    assert (
        b"ERROR" not in result.stdout
    ), f"ERROR during create edge: {result.stdout.decode('utf-8')}"

    print("Setup data done...")
