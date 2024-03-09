#!/usr/bin/env python3

#https://python.langchain.com/docs/integrations/tools/search_tools

# from langchain.tools import DuckDuckGoSearchRun
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain.globals import set_verbose

set_verbose(True)

import os
import requests
import json

# https://python.langchain.com/docs/expression_language/cookbook/tools
# 对应的cookbook 是这个，但说实话，压根就没成功运行起来的可能性嘛，这文档和代码
# 不同步的厉害，哎，开源的项目你就很无奈

API_KEY = "PDj0ZLSGne8uapRnjrtIoG0p"
SECRET_KEY = "LpFFFfGRVdWvbeP10c7UidQMadkVxCta"

os.environ["QIANFAN_AK"] = API_KEY
os.environ["QIANFAN_SK"] = SECRET_KEY
qianfan_chat_llm =QianfanChatEndpoint(streaming=True,model="ERNIE-Bot-8k")

#https://python.langchain.com/docs/expression_language/cookbook/tools

search = DuckDuckGoSearchRun()

# 这个DuckDuckGo的一个极简的例子
# https://python.langchain.com/docs/integrations/tools/ddg
# result = search.run("Obama's first name?")
#End of 这个DuckDuckGo的一个极简的例子

# template = """turn the following user input into a search query for a search engine:{input}"""
# prompt = ChatPromptTemplate.from_template(template)
# chain = prompt | llm 

# chain.invoke({"input": "I'd like to figure out what games are tonight"})
#现在的第一个坑是，invoke之后，没有什么输出？
#问题也很清晰就是，search之后，这个DuckDuckGoSearchRun不输出，很奇怪。。。哎。。。

# 这里就是一个能成功运行的例子了
# prompt = ChatPromptTemplate.from_template("tell me a short joke about {topic}")
# prompt_value = prompt.invoke({"topic": "ice cream"})
# print(prompt_value)

# model = qianfan_chat_llm

# message = model.invoke(prompt_value)
# print(message)

# output_parser = StrOutputParser()

# chain = prompt | model | output_parser

# chain.invoke({"topic": "ice cream"})

# lemonhall@lemonhallme:~/openai$ python3 search_agent.py 
# messages=[HumanMessage(content='tell me a short joke about ice cream')]
# [INFO] [03-03 18:42:33] openapi_requestor.py:316 [t:140092418664256]: requesting llm api endpoint: /chat/ernie_bot_8k
# [INFO] [03-03 18:42:33] oauth.py:207 [t:140092418664256]: trying to refresh access_token for ak `PDj0ZL***`
# [INFO] [03-03 18:42:33] oauth.py:220 [t:140092418664256]: sucessfully refresh access_token
# content='Why did the ice cream smile?\n\nBecause it was happy!'
# [INFO] [03-03 18:42:35] openapi_requestor.py:316 [t:140092418664256]: requesting llm api endpoint: /chat/ernie_bot_8k

# END OF 这里就是一个能成功运行的例子了

# 以下是一个可以成功运行的搜索的例子
# template = """turn the following user input into a search query for a search engine:{input}"""
# prompt = ChatPromptTemplate.from_template(template)
# prompt_value = prompt.invoke({"input": "哈马斯到底能否赢得2023年底的这场战争？"})
# print("============================== \n print(prompt_value):")
# print(prompt_value)
# print("============================== END of print(prompt_value):")
# model = qianfan_chat_llm
# message = model.invoke(prompt_value)
# print(message)
# result = search.run("哈马斯 2023年底 战争 赢得可能性")
# END OF 以下是一个可以成功运行的搜索的例子

# 这个链式调用就不成功
# template = """turn the following user input into a search query for a search engine:{input}"""
# prompt = ChatPromptTemplate.from_template(template)
# model = qianfan_chat_llm
# chain = prompt | model | StrOutputParser() | search
# chain.invoke({"input": "哈马斯到底能否赢得2023年底的这场战争？"})
# 这个链式调用就不成功

# https://python.langchain.com/docs/expression_language/get_started
# 从LCEL这篇GET STARTED看的话，应该是某一个组件的输出有问题

# 第一段：组装出一个prompt value
# template = """将如下用户输入变为搜索引擎的关键词，回答务必简短，不要大段大段的推演过程，只要关键词的输出:{input}"""
# prompt = ChatPromptTemplate.from_template(template)
# prompt_value = prompt.invoke({"input": "哈马斯到底能否赢得2023年底的这场战争？"})
# print("============================== \n print(prompt_value):")
# print(prompt_value)
# print("============================== END of print(prompt_value):")
# # 第二段：输出给LLM，拿到BaseMessage
# model = qianfan_chat_llm
# llm_result = model.invoke(prompt_value)
# print("============================== \n print(llm_result):这里的返回应该是一个BaseMessage")
# print(llm_result)
# print("============================== END of print(llm_result):")
# # 第三段：把BaseMessage输出给StrOutputParser，拿到纯String
# output_parser = StrOutputParser()
# parser_result = output_parser.invoke(llm_result)
# print("============================== \n print(parser_result):这里的返回应该是一个str")
# print(parser_result)
# print("============================== END of print(parser_result):")
# # 第四段：将纯String输出给DDg，拿到输出
# result = search.run(parser_result)

# 第五段：试图链化
template = """将如下用户输入变为搜索引擎的关键词，回答务必简短，不要大段大段的推演过程，只要关键词的输出:{input}"""
prompt = ChatPromptTemplate.from_template(template)
model = qianfan_chat_llm
output_parser = StrOutputParser()
chain = prompt | model | StrOutputParser() | search
chain.invoke({"input": "亚伦.布什内尔是谁?"})
