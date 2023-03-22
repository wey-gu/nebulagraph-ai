from ng_ai import NebulaGraphConfig, NebulaReader

# read data with spark engine, query mode
config_dict = {
    "graphd_hosts": "graphd:9669",
    "metad_hosts": "metad0:9559",
    "user": "root",
    "password": "nebula",
    "space": "basketballplayer",
}
config = NebulaGraphConfig(**config_dict)
reader = NebulaReader(engine="spark", config=config)
query = """
    MATCH ()-[e:follow]->()
    RETURN e LIMIT 100000
"""
reader.query(query=query, edge="follow", props="degree")
df = reader.read()

"""
/spark/bin/spark-submit \
    --jars /root/download/nebula-algo.jar \
    /root/run/query_reader.py
"""
