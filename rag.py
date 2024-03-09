#!/usr/bin/env python3
import os
import requests
import json

from operator import itemgetter
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_community.embeddings import QianfanEmbeddingsEndpoint

from langchain.globals import set_verbose
set_verbose(True)

API_KEY = "xxxxxxxxxxxxxxxxxxx"
SECRET_KEY = "xxxxxxxxxxxxxxxxxxx"

os.environ["QIANFAN_AK"] = API_KEY
os.environ["QIANFAN_SK"] = SECRET_KEY

qianfan_chat_llm =QianfanChatEndpoint(streaming=True,model="ERNIE-Bot-8k")

#https://cloud.baidu.com/qianfandev/topic/267934
# 看一下百度的文档哈

# QianfanEmbeddings = QianfanEmbeddingsEndpoint(model="ERNIE-Bot-8k")

# 第一步：做好词嵌入
# pip install faiss-cpu
vectorstore = FAISS.from_texts(
    ["法萨卢斯战役(battle of Pharsalus)，又称法尔萨鲁斯战役。是公元前48年，以盖乌斯•尤利乌斯•恺撒为首的平民派军队和以格奈乌斯•庞培•马格努斯为首的贵族共和派军队之间展开的罗马内战的决定性战役。恺撒在此役的获胜使其成为罗马共和国的实际最高统治者，罗马开始由共和国向帝国转变，而庞培则败逃埃及，继而被杀。这也是凯撒一生最重要的战役。",
    "凯撒对十一税的改革，迅速抹平了对意大利本土半岛以及行省之间的差距，这充分体现了凯撒在经济领域的才学"]
    , embedding=QianfanEmbeddingsEndpoint(model="bge-large-zh")
)
retriever = vectorstore.as_retriever()
# https://python.langchain.com/docs/integrations/vectorstores/faiss
# Facebook AI Similarity Search (Faiss) is a library for efficient similarity search 
# and clustering of dense vectors. It contains algorithms that search in sets of 
# vectors of any size, up to ones that possibly do not fit in RAM. 
# It also contains supporting code for evaluation and parameter tuning.


# 第二步：构造好llm的问答
template = """
你是盖乌斯·尤利乌斯·恺撒，
你将循循善诱得回答对话者的所有问题。

Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

model = qianfan_chat_llm

# 第三步： 构造链
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# 第四步：调用链条
result = chain.invoke("您对罗马经济的贡献有哪些？")
print(result)
