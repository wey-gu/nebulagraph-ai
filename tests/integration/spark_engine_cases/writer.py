from ng_ai import NebulaReader, NebulaWriter
from ng_ai.config import NebulaGraphConfig

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

df_result = df.algo.label_propagation()

writer = NebulaWriter(
    data=df_result, sink="nebulagraph_vertex", config=config, engine="spark"
)

# map column louvain into property cluster_id
properties = {"lpa": "cluster_id"}

writer.set_options(
    tag="label_propagation",
    vid_field="_id",
    properties=properties,
    batch_size=256,
    write_mode="insert",
)
# write back to NebulaGraph
writer.write()

"""
/spark/bin/spark-submit \
    --jars /root/download/nebula-algo.jar \
    /root/run/writer.py
"""

# edge writer

df_result = df.algo.jaccard()

writer = NebulaWriter(
    data=df_result, sink="nebulagraph_vertex", config=config, engine="spark"
)

# map column louvain into property cluster_id
properties = {"similarity": "similarity"}

writer.set_options(
    space="basketballplayer",
    type="edge",
    edge_type="jaccard_similarity",
    src_id="srcId",
    dst_id="dstId",
    src_id_policy="",
    dst_id_policy="",
    properties=properties,
    batch_size=256,
    write_mode="insert",
)

# write back to NebulaGraph
writer.write()
