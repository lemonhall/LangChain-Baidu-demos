#!/usr/bin/env python3
from typing import List, Tuple

from langchain.chains import ConversationChain
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_models import QianfanChatEndpoint

from log_callback_handler import NiceGuiLogElementCallbackHandler

#https://python.langchain.com/docs/integrations/toolkits/sql_database
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.sql_database import SQLDatabase

import os
import requests
import json

API_KEY = "PDj0ZLSGne8uapRnjrtIoG0p"
SECRET_KEY = "LpFFFfGRVdWvbeP10c7UidQMadkVxCta"

os.environ["QIANFAN_AK"] = API_KEY
os.environ["QIANFAN_SK"] = SECRET_KEY
qianfan_chat_llm =QianfanChatEndpoint(streaming=True,model="ERNIE-Bot-8k")

# sqlite> PRAGMA table_info(notes);
# 0|created_on|DATETIME|1||0
# 1|changed_on|DATETIME|1||0
# 2|id|INTEGER|1||1
# 3|title|VARCHAR(256)|0||0
# 4|content|TEXT|0||0
# 5|created_by_fk|INTEGER|1||0
# 6|changed_by_fk|INTEGER|1||0
# sqlite> 
db = SQLDatabase.from_uri("sqlite:///app.db")
#toolkit = SQLDatabaseToolkit(db=db)

agent_executor = create_sql_agent(
    llm=qianfan_chat_llm,
    db=db,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

# agent_executor.invoke("请列出notes表里从标题来分类，你觉得有可能是菜谱的记录")
agent_executor.invoke("""首先请取出notes表100个记录的title字段，
之后输出你经过手工分析过的所有的你感觉到的可能是菜谱的记录。
请在输出Action Input时尽可能不要解释自己的SQL语句""")
