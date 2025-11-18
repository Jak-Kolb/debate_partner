
cc_library(
    name = "llm",
    srcs = ["llm.cc"],
    hdrs = ["llm.hpp"],
    deps = ["@cpp-httplib//:httplib", "@nlohmann_json//:json"],
)

cc_library(
    name = "message", 
    srcs = ["message.cc"],
    hdrs = ["message.hpp"],
)

cc_binary(
    name = "main",
    srcs = ["main.cc"],
    deps = [
        ":llm",
        ":message",
        "//utils:dotenv",
    ],
    data = ["//:env_file"],
)