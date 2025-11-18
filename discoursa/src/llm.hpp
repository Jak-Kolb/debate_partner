
#ifndef LLM_H

#define LLM_H

#define CPPHTTPLIB_OPENSSL_SUPPORT

#include <string>
#include <map>
#include <iostream>
#include <sstream>
#include <vector>
#include <fstream>
#include <nlohmann/json.hpp>
#include <httplib.h>

using json = nlohmann::json;


class LLM_RESPONSE {
    public:
        // std::string response_text;
        // std::string parse_json()
        void set_model_params(const std::string &model, double temperature) {
            this->model = model;
            this->temperature = temperature;
        }

        std::string llm_request(const std::string &request_content, const std::string &api_key);

    private:
        std::string api_key;
        std::string model;
        double temperature;
        // std::vector<std::string> parse_message_text(std::string response_text);
        json build_request(const std::string &request_content, const std::string &model, double temperature);
        // std::string llm_request(const json &request_json, const std::string &api_key);
};

#endif // LLM_H