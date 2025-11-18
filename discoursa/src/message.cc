
#include "message.hpp"


// -- Article -- 

void Article::printArticle() const {
    std::cout << "Content of article" << idx << ":" << content << std::endl;
}


// -- Evidence -- 

void Evidence::addArticle(const Article &article){ 
    // articles.emplace_back(article.idx, article.summary, article.content, article.used);
    articles.push_back(article);
}

std::string Evidence::getArticleContent(size_t idx){
    if (idx >= articles.size()) {
        std::cout << "message.hpp: No article at that index" << std::endl;
        return "";
    }
    std::string content = articles[idx].content;
    return content;
}

Article Evidence::getArticle(size_t idx){ 
    if (idx >= articles.size()) {
        std::cerr << "message.hpp: No article at that index" << std::endl;
        // return false;
    }
    return articles[idx];
}

bool Evidence::markUsed(size_t idx) {
    if (idx >= articles.size()) {
        std::cerr << "message.hpp: No article at that index" << std::endl;
        return false;
    }
    articles[idx].used = true;
    return true;
}



// -- Message --

void Message::initializeContext(std::vector<std::string> paths, size_t numpaths){
    std::ostringstream oss;
    evidence = gatherEvidence(paths);
    for (int i = 0; i < numpaths; i++) {
        oss << "id: " << evidence.articles[i].idx << " summary: " << evidence.articles[i].summary << " content: " << evidence.articles[i].content << "\n";
    }

    std::cout << oss.str() << std::endl;
}

Evidence Message::gatherEvidence(std::vector<std::string> paths){
    // replace with gathering evidence from file 
    Evidence evidence;
    
    for (const auto& path : paths) {

        Article article;
        std::ifstream file(path);

        if (!file) {
            std::cerr << "Couldn't open file: " << path << std::endl;
            // return 1;
        }
        
        std::string line;
        std::getline(file, line, '<');
        article.idx = std::stoi(line);
        std::getline(file, line, '<');
        article.summary = line;
        std::getline(file, line);
        article.content = line;

        // while (std::getline(file, line, '<<')) {
        //     std::vector 
        // } 
        article.printArticle();

        evidence.addArticle(article);
        evidence.num_articles += 1;
    }
    evidence.topic = "carbon tax";
    return evidence;
    // Evidence evidence;
    // evidence.id = rand(1000);
    // evidence.topic = "placeholder for what LLM will fill";
    // evidence.summary = "placeholder for summary that LLM will fill";
    // evidence.info = "placeholder for future article context";
    // return evidence;
}



