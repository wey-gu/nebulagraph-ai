/* Copyright (c) 2023 vesoft inc. All rights reserved.
 *
 * This source code is licensed under Apache 2.0 License.
 */

#include "ngdi.h"

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <folly/json.h>
#include <vector>

#include "../src/common/datatypes/List.h"
#include "../src/common/datatypes/Map.h"
#include "http_client.h"

extern "C" GraphFunction *create() {
  return new ngdi;
}
extern "C" void destroy(GraphFunction *function) {
  delete function;
}

char *ngdi::name() {
  const char *name = "ngdi";
  return const_cast<char *>(name);
}

std::vector<std::vector<nebula::Value::Type>> ngdi::inputType() {
  // ngdi("pagerank", ["follow"], ["degree"], "spark", {space: "basketballplayer", max_iter: 10}, {write_mode: "insert"})
  std::vector<nebula::Value::Type> scan_type_pattern_0 = {
      nebula::Value::Type::STRING, nebula::Value::Type::LIST, nebula::Value::Type::LIST};
  std::vector<nebula::Value::Type> scan_type_pattern_1 = {nebula::Value::Type::STRING,
                                                          nebula::Value::Type::LIST,
                                                          nebula::Value::Type::LIST,
                                                          nebula::Value::Type::STRING};
  std::vector<nebula::Value::Type> scan_type_pattern_2 = {nebula::Value::Type::STRING,
                                                          nebula::Value::Type::LIST,
                                                          nebula::Value::Type::LIST,
                                                          nebula::Value::Type::STRING,
                                                          nebula::Value::Type::MAP};
  std::vector<nebula::Value::Type> scan_type_pattern_3 = {nebula::Value::Type::STRING,
                                                          nebula::Value::Type::LIST,
                                                          nebula::Value::Type::LIST,
                                                          nebula::Value::Type::STRING,
                                                          nebula::Value::Type::MAP,
                                                          nebula::Value::Type::MAP};
  // ngdi("pagerank", $-.query, "spark", {space: "basketballplayer", max_iter: 10}, {write_mode: "insert"})
  std::vector<nebula::Value::Type> query_type_pattern_0 = {nebula::Value::Type::STRING,
                                                           nebula::Value::Type::STRING};
  std::vector<nebula::Value::Type> query_type_pattern_1 = {
      nebula::Value::Type::STRING, nebula::Value::Type::STRING, nebula::Value::Type::STRING};
  std::vector<nebula::Value::Type> query_type_pattern_2 = {nebula::Value::Type::STRING,
                                                           nebula::Value::Type::STRING,
                                                           nebula::Value::Type::STRING,
                                                           nebula::Value::Type::MAP};
  std::vector<nebula::Value::Type> query_type_pattern_3 = {nebula::Value::Type::STRING,
                                                           nebula::Value::Type::STRING,
                                                           nebula::Value::Type::STRING,
                                                           nebula::Value::Type::MAP,
                                                           nebula::Value::Type::MAP};

  std::vector<std::vector<nebula::Value::Type>> vvtp = {scan_type_pattern_0,
                                                        scan_type_pattern_1,
                                                        scan_type_pattern_2,
                                                        scan_type_pattern_3,
                                                        query_type_pattern_0,
                                                        query_type_pattern_1,
                                                        query_type_pattern_2,
                                                        query_type_pattern_3};
  return vvtp;
}

nebula::Value::Type ngdi::returnType() {
  return nebula::Value::Type::MAP;
}

size_t ngdi::minArity() {
  return 2;
}

size_t ngdi::maxArity() {
  return 6;
}

bool ngdi::isPure() {
  return true;
}

nebula::Value ngdi::call_ngdi_api(
    const std::vector<std::reference_wrapper<const nebula::Value>> &args) {
  // function to make http call to ngdi-api-gateway
  // param:
  //  - read_context, Value::Type::MAP
  //  - write_context, Value::Type::MAP
  //  - algo_context, Value::Type::MAP
  //  - mode, Value::Type::STRING, default to "networkx", another valid value for now is "spark"
  // return: Value::Type::MAP

  // get the read_context
  auto read_context = args[0].get().getMap();
  // std::cout << "read_context: " << read_context.toString() << std::endl;
  // get the write_context
  auto write_context = args[1].get().getMap();
  // std::cout << "write_context: " << write_context.toString() << std::endl;
  // get the algo_context
  auto algo_context = args[2].get().getMap();
  // std::cout << "algo_context: " << algo_context.toString() << std::endl;
  // get the mode
  auto mode = args[3].get().getStr();
  // validate the mode value, if not valid, return response MAP with error message: "Invalid mode:
  // {mode}}"
  if (mode != "networkx" && mode != "spark") {
    nebula::Map response;
    response.kvs.emplace("error", nebula::Value("Invalid mode: " + mode));
    response.kvs.emplace("mode", mode);
    return nebula::Value(response);
  }

  // validate the read_mode and other read_context values, if not valid, return response MAP with
  // error message: "Invalid read_context: {read_context}}"
  auto read_mode = read_context.kvs.find("read_mode");
  // when read_mode is "query", there must be a "query" key in read_context, if not, return response
  // MAP with error message: "Invalid read_context: no query found in read_mode: query"
  if (read_mode != read_context.kvs.end() && read_mode->second.getStr() == "query") {
    auto query = read_context.kvs.find("query");
    if (query == read_context.kvs.end()) {
      nebula::Map response;
      response.kvs.emplace(
          "error", nebula::Value("Invalid read_context: no query found in read_mode: query"));
      response.kvs.emplace("read_context", read_context);
      return nebula::Value(response);
    }
    // else when read_mode is "scan", there must be "edges" and "edge_weights" keys in read_context,
    // if not, return response MAP with error message: "Invalid read_context: no edges or
    // edge_weights found in read_mode: scan"
  } else if (read_mode != read_context.kvs.end() && read_mode->second.getStr() == "scan") {
    auto edges = read_context.kvs.find("edge_types");
    auto edge_weights = read_context.kvs.find("edge_weights");
    if (edges == read_context.kvs.end() || edge_weights == read_context.kvs.end()) {
      nebula::Map response;
      response.kvs.emplace(
          "error",
          nebula::Value("Invalid read_context: no edges or edge_weights found in read_mode: scan"));
      response.kvs.emplace("read_context", read_context);
      return nebula::Value(response);
    }
    // else, other invalid read_mode values, return response MAP with error message: "Invalid
    // read_context: {read_context}}"
  } else {
    nebula::Map response;
    response.kvs.emplace("error", nebula::Value("Invalid read_context: " + read_context));
    response.kvs.emplace("read_context", read_context);
    return nebula::Value(response);
  }
  // validate name exists in algo_context, and the value is in ["label_propagation", "louvain",
  // "k_core", "degree_statics", "betweenness_centrality", "coefficient_centrality", "bfs", "hanp",
  // "jaccard", "strong_connected_components", "triangle_coun", "pagerank"] if not valid, return response MAP
  // with error message: "Invalid algo_name: {algo_name}"
  auto algo_name = algo_context.kvs.find("name");
  if (algo_name == algo_context.kvs.end()) {
    nebula::Map response;
    response.kvs.emplace("error", nebula::Value("Invalid algo_context: no algo_name found"));
    // response.kvs.emplace("algo_context", algo_context);
    return nebula::Value(response);
  }
  auto algo_name_value = algo_name->second.getStr();
  if (algo_name_value != "label_propagation" && algo_name_value != "louvain" &&
      algo_name_value != "k_core" && algo_name_value != "degree_statics" &&
      algo_name_value != "betweenness_centrality" && algo_name_value != "coefficient_centrality" &&
      algo_name_value != "bfs" && algo_name_value != "hanp" && algo_name_value != "jaccard" &&
      algo_name_value != "strong_connected_components" && algo_name_value != "triangle_coun" &&
      algo_name_value != "pagerank") {
    nebula::Map response;
    response.kvs.emplace("error", nebula::Value("Invalid algo_name: " + algo_name_value));
    response.kvs.emplace("algo_name", algo_name_value);
    response.kvs.emplace("hint", nebula::Value(
      "Valid algo_name: label_propagation, louvain, k_core, degree_statics, betweenness_centrality, "
      "coefficient_centrality, bfs, hanp, jaccard, strong_connected_components, triangle_coun, "
      "pagerank"));
    return nebula::Value(response);
  }
  // validate the config in algo_context when there is a config key in algo_context, it should be a
  // MAP
  auto config = algo_context.kvs.find("config");
  if (config != algo_context.kvs.end() && config->second.type() != nebula::Value::Type::MAP) {
    nebula::Map response;
    response.kvs.emplace("error", nebula::Value("Invalid algo_context: config should be a MAP"));
    // response.kvs.emplace("algo_context", algo_context);
    return nebula::Value(response);
  }
  // get base_url from env, if not found set to default: http://jupyter:9999
  char* _base_url = getenv("ngdi_gateway_url_prefix");
  const char* base_url;
  if (!_base_url) {
    // std::cout << "The environment variable ngdi_gateway_url_prefix cannot be found.\n"
              //    "Using default:http://jupyter:9999 \n"
              //    "Ensure graphd process comes with it like: \n"
              //    "export ngdi_gateway_url_prefix=http://jupyter:9999"
              // << std::endl;
    base_url = "http://jupyter:9999";
  } else {
    // std::cout << "The environment variable ngdi_gateway_url_prefix is found.\n"
                //  "Using: " << _base_url << std::endl;
    base_url = _base_url;
  }

  // append /api/v0/ to the base_url url_prefix = base_url + "/api/v0/"
  std::string url_prefix;
  url_prefix.append(base_url);
  url_prefix.append("/api/v0/");
  // call the ngdi api gateway with the url_prefix on /api/v0/{mode}/{algo_name}

  // the body is {"read_context": {read_context}, "write_context": {write_context}, "algo_context":
  // {algo_context}} build the body, body is a hashmap
  nebula::Map body;
  body.kvs.emplace("read_context", nebula::Value(read_context));
  body.kvs.emplace("write_context", nebula::Value(write_context));
  body.kvs.emplace("algo_context", nebula::Value(algo_context));

  // convert body to json string
  folly::dynamic json_body = body.toJson();
  std::string str_body = folly::toJson(json_body);

  // std::cout << "str_body: " << str_body << std::endl;

  // build the headers
  std::vector<std::string> headers;
  // set the content-type to application/json
  headers.emplace_back("Content-Type: application/json");

  auto response_str = do_post(url_prefix + mode + "/" + algo_name_value, headers, str_body);

  // build response MAP from response_str and return
  nebula::Map response;
  response.kvs.emplace("response", nebula::Value(response_str));
  response.kvs.emplace("body", nebula::Value(str_body));
  response.kvs.emplace("url", nebula::Value(url_prefix + mode + "/" + algo_name_value));
  response.kvs.emplace("debug", nebula::Value(
    "curl -X POST -H \"Content-Type: application/json\" -d '" + str_body + "' " + url_prefix +
    mode + "/" + algo_name_value));
  return nebula::Value(response);
}

  nebula::Value ngdi::body(const std::vector<std::reference_wrapper<const nebula::Value>> &args) {
    // context MAPs to be passed to ngdi api gateway
    nebula::Map read_context;
    nebula::Map write_context;
    nebula::Map algo_context;
    nebula::Value mode = nebula::Value("networkx");

    // validate the args size, if smaller than 2, return response MAP with error message: "Invalid
    // args size: {args.size()}"
    if (args.size() < 2) {
      nebula::Map response;
      response.kvs.emplace("error",
                           nebula::Value("Invalid args size: " + std::to_string(args.size())));
      return nebula::Value(response);
    } else if (args[0].get().type() != nebula::Value::Type::STRING) {
      // validate the first arg is a string, if not, return response MAP with error message:
      // "Invalid args[0]: {args[0]}"
      nebula::Map response;
      response.kvs.emplace("error", nebula::Value("Invalid args[0]: " + args[0].get()));
      return nebula::Value(response);
    } else if (args[1].get().type() == nebula::Value::Type::LIST) {
      // ----------------------------------------------------------
      // ngdi("pagerank", ["follow"], ["degree"], "spark")
      //
      // # default algo conf and write conf
      //
      // ngdi("pagerank", ["follow"], ["degree"], "spark", {space: "basketballplayer", max_iter: 10}, {write_mode: "insert"})
      // ----------------------------------------------------------
      // if the second arg is a LIST, its read_mode is "scan"
      // validate:
      // 0. the size of the second arg is larger than 0
      // 1. there are third arg
      // 2. the third arg is a LIST
      // 3. the size of the second arg and the third arg are the same all the elements are STRING
      // if not, return response MAP with error message: "Invalid args[1]: edge_types and
      // edge_weights should be a LIST of STRING in same size"

      if (args[1].get().getList().size() == 0) {
        nebula::Map response;
        response.kvs.emplace(
            "error",
            nebula::Value("Invalid args[1]: edge_types should be a LIST of STRING in same size"));
        response.kvs.emplace(
          "hint",
          nebula::Value("edge_types: [\"follow\", \"like\"], edge_weights: [\"degree\", \"degree\"]"));
        return nebula::Value(response);
      }
      if (args.size() < 3) {
        nebula::Map response;
        response.kvs.emplace("error",
                             nebula::Value("Invalid args size: " + std::to_string(args.size())));
        response.kvs.emplace(
            "hint",
            nebula::Value(
                "ngdi(\"pagerank\", [\"follow\"], [\"degree\"], \"spark\"), or with more arguments"));
        return nebula::Value(response);
      }
      if (args[2].get().type() != nebula::Value::Type::LIST) {
        nebula::Map response;
        response.kvs.emplace(
            "error",
            nebula::Value("Invalid args[2]: edge_weights should be a LIST of STRING in same size"));
        response.kvs.emplace(
            "hint",
            nebula::Value("edge_types: ['follow', 'like'], edge_weights: ['degree', 'degree']"));
        return nebula::Value(response);
      }

      if (args[1].get().getList().size() != args[2].get().getList().size()) {
        nebula::Map response;
        response.kvs.emplace(
            "error",
            nebula::Value("Invalid args[1]: edge_types and edge_weights should be a "
                          "LIST of STRING in same size"));
        response.kvs.emplace(
            "hint",
            nebula::Value("edge_types: ['follow', 'like'], edge_weights: ['degree', 'degree']"));
        return nebula::Value(response);
      }
      for (auto i = 0; i < args[1].get().getList().size(); i++) {
        if (args[1].get().getList()[i].type() != nebula::Value::Type::STRING ||
            args[2].get().getList()[i].type() != nebula::Value::Type::STRING) {
          nebula::Map response;
          response.kvs.emplace(
              "error",
              nebula::Value("Invalid args[1]: edge_types and edge_weights should be a "
                            "LIST of STRING in same size"));
          response.kvs.emplace(
              "hint",
              nebula::Value("edge_types: ['follow', 'like'], edge_weights: ['degree', 'degree']"));
          return nebula::Value(response);
        }
      }

      // build the read_context
      read_context.kvs.emplace("read_mode", nebula::Value("scan"));
      read_context.kvs.emplace("edge_types", nebula::Value(args[1].get().getList()));
      read_context.kvs.emplace("edge_weights", nebula::Value(args[2].get().getList()));

      // build mode from the 4th arg if there is one, otherwise use nebula::Value("networkx"))

      if (args.size() >= 4) {
        // validate that mode is string and in ["networkx", "spark"]
        if (args[3].get().type() != nebula::Value::Type::STRING) {
          nebula::Map response;
          response.kvs.emplace("error", nebula::Value("Invalid mode: should be a STRING"));
          response.kvs.emplace("mode", args[3].get().getStr());
          return nebula::Value(response);
        }
        if (args[3].get().getStr() != "networkx" && args[3].get().getStr() != "spark") {
          nebula::Map response;
          response.kvs.emplace("error", nebula::Value("Invalid mode: should be in [networkx, spark]"));
          response.kvs.emplace("mode", args[3].get().getStr());
          return nebula::Value(response);
        }
        mode = args[3].get().getStr();
      } else {
        mode = nebula::Value("networkx");
      }
      // build the algo_context

      // ngdi("pagerank", ["follow"], ["degree"], "spark", {space: "basketballplayer", max_iter: 10}, {write_mode:
      // "insert"}

      if (args.size() >= 5) {
        if (!args[4].get().isMap()) {
          nebula::Map response;
          response.kvs.emplace("error", nebula::Value("Invalid algo_context: should be a MAP"));
          return nebula::Value(response);
        }
        algo_context = args[4].get().getMap();
      } else {
        algo_context = nebula::Map();
      }

      // add the name to algo_context
      algo_context.kvs.emplace("name", nebula::Value(args[0].get().getStr()));

      // build the write_context
      nebula::Map write_context;

      if (args.size() >= 6) {
        if (!args[5].get().isMap()) {
          nebula::Map response;
          response.kvs.emplace("error", nebula::Value("Invalid write_context: should be a MAP"));
          return nebula::Value(response);
        }
        write_context = args[5].get().getMap();
      } else {
        write_context = nebula::Map();
      }

    } else if (args[1].get().type() == nebula::Value::Type::STRING) {
      // ----------------------------------------------------------
      // ngdi("pagerank", $-.query, "spark") # default algo conf and write conf
      // ngdi("pagerank", $-.query, "spark", {space: "basketballplayer", max_iter: 10}, {write_mode: "insert"})
      // ----------------------------------------------------------
      // if the second arg is a STRING, its read_mode is "query"
      // validate it's not empty
      // TBD(wey): need to add edges and edge_weights to query read_mode, too, the edge_weights
      // could have None as item, too.

      if (args[1].get().getStr().empty()) {
        nebula::Map response;
        response.kvs.emplace("error", nebula::Value("Invalid args[1]: query should be a STRING"));
        response.kvs.emplace("hint", nebula::Value("query: 'MATCH ()-[e:follow]->() RETURN e LIMIT 1000'"));
        return nebula::Value(response);
      }

      // build the read_context
      read_context.kvs.emplace("read_mode", nebula::Value("query"));
      read_context.kvs.emplace("query", nebula::Value(args[1].get()));

      // build mode from the 3th arg if there is one, otherwise use nebula::Value("networkx"))
      if (args.size() >= 3) {
        // validate that mode is string and in ["networkx", "spark"]
        if (args[2].get().type() != nebula::Value::Type::STRING) {
          nebula::Map response;
          response.kvs.emplace("error", nebula::Value("Invalid mode: should be a STRING"));
          response.kvs.emplace("hint", nebula::Value("mode: 'networkx' or 'spark'"));
          return nebula::Value(response);
        }
        if (args[2].get().getStr() != "networkx" && args[2].get().getStr() != "spark") {
          nebula::Map response;
          response.kvs.emplace("error", nebula::Value("Invalid mode: should be in [networkx, spark]"));
          response.kvs.emplace("hint", nebula::Value("mode: 'networkx' or 'spark'"));
          return nebula::Value(response);
        }
        mode = args[3].get().getStr();
      } else {
        mode = nebula::Value("networkx");
      }
      // build the algo_context
      if (args.size() >= 4) {
        // validate that algo_context is a MAP
        if (!args[3].get().isMap()) {
          nebula::Map response;
          response.kvs.emplace("error", nebula::Value("Invalid algo_context: should be a MAP"));
          return nebula::Value(response);
        }
        algo_context = args[3].get().getMap();
      } else {
        algo_context = nebula::Map();
      }

      // add the name to algo_context
      algo_context.kvs.emplace("name", nebula::Value(args[0].get().getStr()));

      // build the write_context
      nebula::Map write_context;

      if (args.size() >= 5) {
        // validate that write_context is a MAP
        if (!args[4].get().isMap()) {
          nebula::Map response;
          response.kvs.emplace("error", nebula::Value("Invalid write_context: should be a MAP"));
          response.kvs.emplace("write_context", args[4].get());
          return nebula::Value(response);
        }
        write_context = args[4].get().getMap();
      } else {
        write_context = nebula::Map();
      }

    } else {
      // not supported args pattern
      nebula::Map response;
      response.kvs.emplace("error", nebula::Value("Invalid args[1]: should be a LIST or STRING"));
      response.kvs.emplace("hint", nebula::Value("args[1]: ['follow', 'like'] or 'MATCH ()-[e:follow]->() RETURN e LIMIT 1000'"));
      return nebula::Value(response);
    }

    // if no write_mode is specified, use "insert"
    if (write_context.kvs.find("write_mode") == write_context.kvs.end()) {
      write_context.kvs.emplace("write_mode", nebula::Value("insert"));
    }

    std::vector<nebula::Value> api_args;
    api_args.emplace_back(nebula::Value(read_context));
    api_args.emplace_back(nebula::Value(write_context));
    api_args.emplace_back(nebula::Value(algo_context));
    api_args.emplace_back(nebula::Value(mode));

    std::vector<std::reference_wrapper<const nebula::Value>> ref_api_args;
    for (const auto &arg : api_args) {
      ref_api_args.emplace_back(std::cref(arg));
    }

    auto response = call_ngdi_api(ref_api_args);

    // return the response
    return nebula::Value(response);
}