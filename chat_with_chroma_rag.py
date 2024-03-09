#!/usr/bin/env python3
import os
import requests
import json

# 做类型检查用的几个类型
from typing import List, Tuple,Optional

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
# 专门给更新文档的时候用的，LangChain这边又包装了一下
from langchain_core.documents.base import Document


# 用来把chromadb的Collection类型引用进来，做类型检查的
from chromadb.api.models.Collection import Collection
# 这应该是langchain对Chroma的包装类了
from langchain_community.vectorstores.chroma import Chroma

from log_callback_handler import NiceGuiLogElementCallbackHandler

from nicegui import context, ui

from langchain.globals import set_verbose
set_verbose(True)

import chromadb
from chromadb.config import Settings

API_KEY = "PDj0ZLSGne8uapRnjrtIoG0p"
SECRET_KEY = "LpFFFfGRVdWvbeP10c7UidQMadkVxCta"

os.environ["QIANFAN_AK"] = API_KEY
os.environ["QIANFAN_SK"] = SECRET_KEY

qianfan_chat_llm =QianfanChatEndpoint(streaming=True,model="ERNIE-Bot-8k")
qianfan_Embeddings = QianfanEmbeddingsEndpoint(model="bge-large-zh")

# 拿一个client出来
chroma_client = chromadb.PersistentClient(path="./")

# 拿数据库
collection = chroma_client.get_or_create_collection(name="rag_collection")

# 当前的文档设置好
current_selected_collection = collection

# tell LangChain to use our client and collection name
db4 = Chroma(
    client=chroma_client,
    collection_name="rag_collection",
    embedding_function=qianfan_Embeddings,
)

# db4.add_texts(["法萨卢斯战役(battle of Pharsalus)，又称法尔萨鲁斯战役。是公元前48年，以盖乌斯•尤利乌斯•恺撒为首的平民派军队和以格奈乌斯•庞培•马格努斯为首的贵族共和派军队之间展开的罗马内战的决定性战役。恺撒在此役的获胜使其成为罗马共和国的实际最高统治者，罗马开始由共和国向帝国转变，而庞培则败逃埃及，继而被杀。这也是凯撒一生最重要的战役。"],
# None,["1"])

# query = "庞培"
# docs = db4.similarity_search(query)
# chromadb.errors.InvalidDimensionException: Embedding dimension 1024 does not match collection dimensionality 384
# 看来存储的维度和查询的维度如果不一致会糟
# print(docs[0].page_content)

#https://cloud.baidu.com/qianfandev/topic/267934
# 看一下百度的文档哈

# QianfanEmbeddings = QianfanEmbeddingsEndpoint(model="ERNIE-Bot-8k")

# 第一步：做好词嵌入
# pip install faiss-cpu
# vectorstore = FAISS.from_texts(
#     ["法萨卢斯战役(battle of Pharsalus)，又称法尔萨鲁斯战役。是公元前48年，以盖乌斯•尤利乌斯•恺撒为首的平民派军队和以格奈乌斯•庞培•马格努斯为首的贵族共和派军队之间展开的罗马内战的决定性战役。恺撒在此役的获胜使其成为罗马共和国的实际最高统治者，罗马开始由共和国向帝国转变，而庞培则败逃埃及，继而被杀。这也是凯撒一生最重要的战役。",
#     "凯撒对十一税的改革，迅速抹平了对意大利本土半岛以及行省之间的差距，这充分体现了凯撒在经济领域的才学"]
#     , embedding= qianfan_Embeddings
# )
# 这是老的faiss-cpu的语句
# retriever = vectorstore.as_retriever()


# 这是换成了chromadb后的，看看会怎样
# https://python.langchain.com/docs/integrations/vectorstores/chroma#retriever-options
retriever = db4.as_retriever(search_type="mmr")

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

    def get_ids(collections)->List[str]:
        """从collection.get()的结果中拿到the list of id"""
        ids = []
        ids = collections['ids']
        return ids

    def get_documents(collections)->List[str]:
        """从collection.get()的结果中拿到the list of documents str"""
        documents_records = []
        documents_records = collections['documents']
        return documents_records

    def build_documents_rows(ids:List[str],documents:List[str])->List[object]:
        documents_rows = []
        for i in range(len(ids)):
            temp_dict = {'id':ids[i],'documents':documents[i]}
            documents_rows.append(temp_dict)
            temp_dict = {}
        return documents_rows

    # 组装好了id和docs
    cccs_result = current_selected_collection.get()
    cccs_result_ids = get_ids(cccs_result)
    cccs_result_documents = get_documents(cccs_result)
    documents_rows = build_documents_rows(cccs_result_ids,cccs_result_documents)

    @ui.refreshable
    def chroma_gui() -> None:
        columns = [
            {'field': 'id','sortable': True,'flex': 1},
            {'headerName':'文档','field': 'documents', 'editable': True,'cellEditor' : 'agLargeTextCellEditor','flex': 4},
        ]
        rows = documents_rows
        def add_row():
            """点击按钮新增时所对应的界面逻辑，直接copy了add_doc的代码，有些欠妥，稍后重构"""
            # 把指针指向当前选择的数据库之上
            collection_point = current_selected_collection
            max_doc_num = collection_point.count()
            print(max_doc_num)
            inc_id = str(max_doc_num + 1)
            rows.append({'id': inc_id, 'documents': 'New doc content'})
            ui.notify(f'Added row with ID {inc_id}')
            # 这是老的逻辑，直接使用了裸的chroma_client
            # collection_point.add(
            #     documents=['New doc content'],ids=[inc_id]
            # )
            # 这里使用了LangChain包装过的数据库操作句柄，这样，就自带嵌入了
            db4.add_texts(["New doc content"],[{"source":"chrome gui"}],[inc_id])
            aggrid.update()

        def update_row_by_id(row):
            """从全局变量当中拿到当前选中的数据库后，以id为参数更新某一条记录"""
            # 这是老的逻辑，直接使用了裸的chroma_client
            # current_selected_collection.update(
            #     ids=[row["id"]],
            #     documents=[row["documents"]],
            # )
            # 这里使用了LangChain包装过的数据库操作句柄，这样，就自带嵌入了
            new_document_temp = Document(row["documents"])
            new_document_temp.metadata = {"source":"chrome gui"}
            db4.update_document(row["id"],new_document_temp)
            # 又报错了，说是木有metadata，行吧，大概明白了，是LangChain这边包装的方法里，调用了Chromadb那边的batch防范
            # 而那个语句里又写了metadata的for语句来遍历，但是我的文档默认就没写这个所谓的metadata，所以导致update失败了，加上了就好了
            # File "/home/lemonhall/chromadb/.venv/lib/python3.10/site-packages/chromadb/api/types.py", line 266, in validate_metadata
            # raise ValueError(f"Expected metadata to be a non-empty dict, got {metadata}")
            

        def handle_cell_value_change(e):
            new_row = e.args['data']
            print("打印的调试信息：From：handle_cell_value_change(e):")
            print(new_row)
            update_row_by_id(new_row)
            ui.notify(f'Updated row to: {e.args["data"]}')
            rows[:] = [row | new_row if row['id'] == new_row['id'] else row for row in rows]

        def delete_by_ids(ids_will_be_deleted:List[str]):
            """从全局变量当中拿到当前选中的数据库后，以ids列表为入参删除对应的记录"""
            # 这是老的逻辑，直接使用了裸的chroma_client
            # current_selected_collection.delete(ids=ids_will_be_deleted)
            # 这里使用了LangChain包装过的数据库操作句柄，这样，就自带嵌入了
            db4.delete(ids_will_be_deleted)

        async def delete_selected():
            selected_id = [row['id'] for row in await aggrid.get_selected_rows()]
            rows[:] = [row for row in rows if row['id'] not in selected_id]
            ui.notify(f'Deleted row with ID {selected_id}')
            delete_by_ids(selected_id)
            aggrid.update()

        aggrid = ui.aggrid({
            'columnDefs': columns,
            'rowData': rows,
            'rowSelection': 'multiple',
            'stopEditingWhenCellsLoseFocus': True,
            'theme':'quartz',
        }).on('cellValueChanged', handle_cell_value_change)
        # balham-dark
        # https://www.ag-grid.com/react-data-grid/getting-started/
        # https://nicegui.io/documentation/aggrid

        ui.button('删除文档', on_click=delete_selected)
        ui.button('新文档', on_click=add_row)

        return None

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
        chroma_tab = ui.tab('Chroma管理界面')
    with ui.tab_panels(tabs, value=chat_tab).classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
        with ui.tab_panel(chat_tab).classes('items-stretch'):
            # chat_messages()在负责具体的聊天的渲染逻辑
            chat_messages()
        with ui.tab_panel(logs_tab):
            log = ui.log().classes('w-full h-full')
        # chrome管理界面的具体显然逻辑
        with ui.tab_panel(chroma_tab):
            chroma_gui()

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
