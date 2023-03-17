/* Copyright (c) 2023 vesoft inc. All rights reserved.
 *
 * This source code is licensed under Apache 2.0 License.
 */

#ifndef UDF_HTTP_CLIENT
#define UDF_HTTP_CLIENT

#include <curl/curl.h>

#include <cctype>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

#include "../src/common/datatypes/List.h"
#include "../src/common/datatypes/Map.h"

size_t write_callback(char* ptr, size_t size, size_t nmemb, void* userdata) {
  std::string* response = static_cast<std::string*>(userdata);
  response->append(ptr, size * nmemb);
  return size * nmemb;
}

std::string do_post(const std::string& url,
                    const std::vector<std::string>& headers,
                    const std::string& body) {
  std::cout << "url=" << url << std::endl;
  std::cout << "body=" << body << std::endl;
  CURL* curl = curl_easy_init();  // 初始化curl
  if (curl) {
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());    // 设置请求URL
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);  // 支持重定向
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION,
                     write_callback);  // 设置回调函数
    std::string response;
    curl_easy_setopt(curl, CURLOPT_WRITEDATA,
                     &response);                               // 设置回调函数参数
    curl_easy_setopt(curl, CURLOPT_POST, 1L);                  // 设置为POST请求
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, body.c_str());  // 设置请求体
    struct curl_slist* header_list = nullptr;
    for (auto& header : headers) {
      header_list = curl_slist_append(header_list, header.c_str());
    }
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, header_list);
    CURLcode result_code = curl_easy_perform(curl);  // 执行请求
    std::cout << "result code=" << result_code << std::endl;
    if (result_code != CURLE_OK) {
      return curl_easy_strerror(result_code);
    } else {
      std::cout << "response=" << response << std::endl;
      return response;
    }
    curl_easy_cleanup(curl);  // 释放curl资源
  }
  return "ERROR: curl init fail.";
}

#endif