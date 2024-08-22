# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The NebulaGraph Authors. All rights reserved.

from ng_ai.engines import DGLEngine

class Constraint:
    # Device
    CPU = "cpu"
    CUDA = "cuda"
    # Model
    GRAPHSAGE = "graphsage"
    # Aggregator
    MEAN = "mean"
    LSTM = "lstm"
    GCN = "gcn"
    POOL = "pool"

    # Link Prediction
    LINK_PREDICTION_MODELS = {
        GRAPHSAGE: "HeteroGraphSAGELinkPred",
    }
    LINK_PREDICTION_AGGREGATORS = [
        MEAN,
        LSTM,
        GCN,
        POOL,
    ]


class LinkPredictionModel(object):
    def __init__(self, engine: DGLEngine, model_name: str):
        self.engine = engine
        self.model_name = model_name.lower()

        global torch, dgl
        torch = self.engine.torch
        dgl = self.engine.dgl

    def create_model(self, **kwargs):
        if self.model_name in Constraint.LINK_PREDICTION_MODELS:
            model_class = getattr(self, Constraint.LINK_PREDICTION_MODELS[self.model_name])
            return model_class(**kwargs)
        else:
            raise NotImplementedError(f"Model {self.model_name} is not implemented")

    class HeteroGraphSAGELinkPred(torch.nn.Module):
        def __init__(
            self,
            in_feats: int,
            hidden_features: int,
            out_features: int,
            rel_names: list,
            num_layers: int = 2,
            dropout: float = 0.5,
            aggregator_type: str = Constraint.MEAN,
            device: str = Constraint.CPU,
        ):
            super().__init__()
            self.in_feats = in_feats
            self.hidden_features = hidden_features
            self.out_features = out_features
            self.rel_names = rel_names
            self.num_layers = num_layers
            self.dropout = dropout
            self.aggregator_type = aggregator_type
            self.device = device

            assert self.aggregator_type in Constraint.LINK_PREDICTION_AGGREGATORS, (
                f"Aggregator {self.aggregator_type} is not supported. "
                f"Supported aggregators are {Constraint.LINK_PREDICTION_AGGREGATORS}"
            )

            self.layers = torch.nn.ModuleList()
            for i in range(self.num_layers):
                self.layers.append(self.create_layer(i))

        def create_layer(self, layer_num: int):
            in_feats = self.in_feats if layer_num == 0 else self.hidden_features
            out_feats = self.out_features if layer_num == self.num_layers - 1 else self.hidden_features
            activation = None if layer_num == self.num_layers - 1 else torch.nn.functional.relu

            homo_layer = dgl.nn.SAGEConv(
                in_feats=in_feats,
                out_feats=out_feats,
                aggregator_type=self.aggregator_type,
                feat_drop=self.dropout,
                activation=activation,
            ).to(self.device)

            return dgl.nn.HeteroGraphConv(
                {rel: homo_layer for rel in self.rel_names},
                aggregator="sum"
            )

        def forward(self, blocks, features):
            x = features
            for layer, block in zip(self.layers, blocks):
                x = layer(block, x)
            return x

    # Commented out for future work
    # class HeteroGATLinkPred(torch.nn.Module):
    #     def __init__(self, ...):
    #         ...
    #
    #     def forward(self, blocks, features):
    #         ...

    # Add more model classes as needed