# SPDX-License-Identifier: Apache-2.0
# Copyright 2023 The NebulaGraph Authors. All rights reserved.
class NebulaWriter:
    def __init__(self, engine=None, config=None, **kwargs):
        self.engine = engine
        self.config = config

    def write(self, **kwargs):
        raise NotImplementedError
