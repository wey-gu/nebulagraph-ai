/* Copyright (c) 2023 vesoft inc. All rights reserved.
 *
 * This source code is licensed under Apache 2.0 License.
 */

// ng_ai is a function to take arguments and call remote ng_ai-api functions in thriftrpc:
// "127.0.0.1:9999"

#ifndef UDF_ng_ai_H
#define UDF_ng_ai_H

#include "../src/common/function/GraphFunction.h"

// Example of a UDF function that calls ng_ai-api functions

// > YIELD ng_ai("pagerank", ["follow"], ["degree"])

class ng_ai : public GraphFunction {
 public:
  char *name() override;

  std::vector<std::vector<nebula::Value::Type>> inputType() override;

  nebula::Value::Type returnType() override;

  size_t minArity() override;

  size_t maxArity() override;

  bool isPure() override;

  nebula::Value body(const std::vector<std::reference_wrapper<const nebula::Value>> &args) override;

  // call_ng_ai_api
  nebula::Value call_ng_ai_api(const std::vector<std::reference_wrapper<const nebula::Value>> &args);
  // sendPostRequest
  std::string sendPostRequest(const std::string &url,
                              const std::vector<std::string> &headers,
                              const std::string &body_str);
};

#endif  // UDF_ng_ai_H
