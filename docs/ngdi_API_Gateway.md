
## Calling from ngql

```cypher
RETURN ngdi("pagerank", ["follow"], ["degree"], "compact")
```

## Setup ngdi API Gateway

See: [../examples/ngdi_from_ngql_udf.ipynb](https://github.com/wey-gu/nebulagraph-di/blob/main/examples/ngdi_from_ngql_udf.ipynb)

## UDF build

See https://github.com/wey-gu/nebula/tree/ngdi_udf
