#include <iostream>
// #include <vector>
// #include "person.h"
// #include "debate.hpp"
#include "message.hpp"
#include "llm.hpp"
#include "utils/dotenv.h"
// g++ -std=c++17 main.cc message.cc -o main
// g++ -std=c++17 main.cc llm.cc -o main

int main()
{
    // std::vector<std::string> paths;
    // paths.push_back("articles/article0.txt");
    // paths.push_back("articles/article1.txt");
    // paths.push_back("articles/article2.txt");

    dotenv env(".env");
    std::string api_key = env.get("DISCOURSA_API_KEY", "");

    if (api_key.empty()) {
        std::cerr << "Error: DISCOURSA_API_KEY environment variable not set." << std::endl;
        return EXIT_FAILURE;
    }

    // Message message;
    // message.initializeContext(paths, 3);
    LLM_RESPONSE llm_response;
    std::string request_content = "Hello, how are you?";
    std::string model = "gpt-5-nano";
    double temperature = 1;
    llm_response.set_model_params(model, temperature);
    

    std::string response = llm_response.llm_request(request_content, api_key);
    std::cout << "LLM Response: " << response << std::endl;

    std::cout << "DONE"; 
    return EXIT_SUCCESS;
}