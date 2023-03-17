/* Copyright (c) 2023 vesoft inc. All rights reserved.
 *
 * This source code is licensed under Apache 2.0 License.
 */

// ngdi is a function to take arguments and call remote ngdi-api functions in thriftrpc:
// "127.0.0.1:9999"

#ifndef UDF_NGDI_H
#define UDF_NGDI_H

#include "../src/common/function/GraphFunction.h"

// Example of a UDF function that calls ngdi-api functions

// > YIELD ngdi("pagerank", ["follow"], ["degree"])

class ngdi : public GraphFunction {
 public:
  char *name() override;

  std::vector<std::vector<nebula::Value::Type>> inputType() override;

  nebula::Value::Type returnType() override;

  size_t minArity() override;

  size_t maxArity() override;

  bool isPure() override;

  nebula::Value body(const std::vector<std::reference_wrapper<const nebula::Value>> &args) override;

  // call_ngdi_api
  nebula::Value call_ngdi_api(const std::vector<std::reference_wrapper<const nebula::Value>> &args);
  // sendPostRequest
  std::string sendPostRequest(const std::string &url,
                              const std::vector<std::string> &headers,
                              const std::string &body_str);
};

#endif  // UDF_NGDI_H
