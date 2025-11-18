#include "llm.hpp"

// -- LLM_RESPONSE --

using json = nlohmann::json;


json LLM_RESPONSE::build_request(const std::string &request_content, const std::string &model, double temperature) {

    json request_json = {
      {"model", model},
      {"temperature", temperature},
      {"messages", json::array({
        {
          {"role", "user"},
          {"content", request_content}
        }
      })}
    };
    return request_json;
}

std::string LLM_RESPONSE::llm_request(const std::string &request_content, const std::string &api_key) {
    // Implement the API request logic here
    // This is a placeholder implementation
    json request_json = build_request(request_content, model, temperature);

    httplib::SSLClient cli("api.openai.com", 443);

    cli.enable_server_certificate_verification(true);
    cli.set_default_headers({{"Content-Type", "application/json"},
                            {"Authorization", "Bearer " + api_key}});
    // std::cout << prompt_str << std::endl;
    auto res = cli.Post("/v1/chat/completions", request_json.dump(), "application/json");
    // std::cout << "Send\n\n\n: " << std::endl;

    if (!res)
    {
      std::cerr << "Post request failed";
      return "";
    }

    if (res->status != 200){
      std::cerr << "API Error #:" << res->status << std::endl;
      std::cerr << "Response:" << res->body << std::endl;
      return "";
    }

    auto parsed_json = json::parse(res->body);
    std::string response_text = parsed_json["choices"][0]["message"]["content"];

    // std::string response_text = "Mock response from LLM";

    return response_text;
}