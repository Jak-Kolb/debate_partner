
#ifndef MESSAGE_H
#define MESSAGE_H

#include <string>
#include <map>
#include <iostream>
#include <sstream>
#include <vector>
#include <fstream>

struct Article { // struct for holding one article
// public:
    size_t idx = 0;
    std::string summary;
    std::string content;
    bool used = false;

    void printArticle() const;
};

struct Evidence { // struct for holding all of the article for one topic
// public: 
    std::string topic;
    int topic_id;
    int num_articles = 0;
    std::vector<Article> articles;

    // void addArticle(size_t idx, std::string summary, std::string content, bool used){ 
    //     evidence.emplace_back(id, summary, content, used);
    // }

    void addArticle(const Article &article);
    std::string getArticleContent(size_t idx);
    Article getArticle(size_t idx);
    bool markUsed(size_t idx);
};

class Message {
    public:
        // Evidence gatherEvidence(){
        // }
        Evidence evidence;

        void initializeContext(std::vector<std::string> paths, size_t numpaths);
    private: 
        Evidence gatherEvidence(std::vector<std::string> paths);
    };

#endif // MESSAGE_H