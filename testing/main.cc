#include <iostream>
// #include <vector>
// #include "person.h"
// #include "debate.hpp"
#include "message.hpp"

int main()
{
    std::vector<std::string> paths;
    paths.push_back("articles/article0.txt");
    paths.push_back("articles/article1.txt");
    paths.push_back("articles/article2.txt");

    Message message;
    message.initializeContext(paths, 3);
    
    std::cout << "DONE"; 
    return EXIT_SUCCESS;
}