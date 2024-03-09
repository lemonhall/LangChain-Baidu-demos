#!/usr/bin/env python3
import os
import requests
import json

from typing import List, Tuple

from operator import itemgetter
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_community.embeddings import QianfanEmbeddingsEndpoint
from langchain.chains import ConversationChain
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_models.human import HumanMessage

from log_callback_handler import NiceGuiLogElementCallbackHandler

from nicegui import context, ui

from langchain.globals import set_verbose
set_verbose(True)

API_KEY = "PDj0ZLSGne8uapRnjrtIoG0p"
SECRET_KEY = "LpFFFfGRVdWvbeP10c7UidQMadkVxCta"

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
retriever_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
# https://python.langchain.com/docs/use_cases/chatbots/quickstart#retrievers
# 参考以上文档，把retriever和chatbot做一个集成

@ui.page('/')
def main():
    #llm = ConversationChain(llm=ChatOpenAI(model_name='gpt-3.5-turbo', openai_api_key=OPENAI_API_KEY))
    llm = retriever_chain
    messages: List[Tuple[str, str]] = []
    thinking: bool = False

    @ui.refreshable
    def chat_messages() -> None:
        for name, text in messages:
            ui.chat_message(text=text, name=name, sent=name == 'You')
        if thinking:
            ui.spinner(size='3rem').classes('self-center')
        if context.get_client().has_socket_connection:
            ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

    async def send() -> None:
        nonlocal thinking
        message = text.value
        messages.append(('You', text.value))
        thinking = True
        text.value = ''
        chat_messages.refresh()

        response = await llm.ainvoke(message)
        # 这里原来是一个await，但现在直接python报错了，毕竟llm.invoke返回的是一个纯纯的String，这咋解决？
        # https://python.langchain.com/docs/expression_language/interface#async-invoke
        # 查了一下，invoke 有异步化的版本的，所以可以直接调用
        #response = await qianfan_chat_endpoint([HumanMessage(content=message)])
        messages.append(('Bot', response))
        thinking = False
        chat_messages.refresh()

    anchor_style = r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}'
    ui.add_head_html(f'<style>{anchor_style}</style>')

    # the queries below are used to expand the contend down to the footer (content can then use flex-grow to expand)
    ui.query('.q-page').classes('flex')
    ui.query('.nicegui-content').classes('w-full')

    with ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('聊天')
        logs_tab = ui.tab('日志')
    with ui.tab_panels(tabs, value=chat_tab).classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
        with ui.tab_panel(chat_tab).classes('items-stretch'):
            # chat_messages()在负责具体的聊天的渲染逻辑
            chat_messages()
        with ui.tab_panel(logs_tab):
            log = ui.log().classes('w-full h-full')

    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = '请输入消息' if API_KEY != 'not-set' else \
                'Please provide your OPENAI key in the Python script first!'
            #这里用on绑定了send()函数
            text = ui.input(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', send)
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')


ui.run(title='与RAG聊天',port=18087)

# 第四步：调用链条:原来rag的逻辑
# result = chain.invoke("您对罗马经济的贡献有哪些？")
# print(result)
