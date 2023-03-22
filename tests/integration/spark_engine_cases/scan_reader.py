from ng_ai import NebulaGraphConfig, NebulaReader

config_dict = {
    "graphd_hosts": "graphd:9669",
    "metad_hosts": "metad0:9559",
    "user": "root",
    "password": "nebula",
    "space": "basketballplayer",
}
config = NebulaGraphConfig(**config_dict)
reader = NebulaReader(engine="spark", config=config)
reader.scan(edge="follow", props="degree")
df = reader.read()
df.show(2)

"""
/spark/bin/spark-submit \
    --jars /root/download/nebula-algo.jar \
    /root/run/scan_reader.py
"""
