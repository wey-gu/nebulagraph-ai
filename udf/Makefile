# Copyright (c) 2023 vesoft inc. All rights reserved.
#
# This source code is licensed under Apache 2.0 License.
#

ifneq ($(wildcard ../build/third-party/install),)
  3PP_PATH := ../build/third-party/install
else ifneq ($(wildcard /opt/vesoft/third-party/3.3),)
  3PP_PATH := /opt/vesoft/third-party/3.3
else ifneq ($(wildcard /opt/vesoft/third-party/3.0),)
  3PP_PATH := /opt/vesoft/third-party/3.0
else
  $(error "Cannot find the third-party installation directory")
endif

CXX := g++
CXX_FLAGS := -std=c++17 -c -I ../src/ -I $(3PP_PATH)/include/ -fPIC -static-libstdc++
LIBS := -L$(3PP_PATH)/lib -static-libstdc++ -lglog -lgflags -Wl,-rpath=$(3PP_PATH)/lib -lcurl
UDF ?= ngdi

all: $(UDF).cpp
	$(CXX) $(CXX_FLAGS) $(UDF).cpp -o $(UDF).o
	$(CXX) -shared $(UDF).o $(LIBS) -o $(UDF).so


clean:
	rm ./*.o
	rm ./*.so

.PHONY: help
help:
	@echo "Usage: make UDF=<udf_name>"
	@echo "Example: make UDF=ngdi"
