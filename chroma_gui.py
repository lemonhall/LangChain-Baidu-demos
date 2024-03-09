

from typing import Optional,List
from nicegui import ui

import chromadb

# 用来把chromadb的Collection类型引用进来，做类型检查的
from chromadb.api.models.Collection import Collection

# 新建一个自定义的docment类型，来方便后续操作
class MyDoc:
    """新建一个自定义的docment类型，来方便后续操作"""
    def __init__(self, content:Optional[str]):
        self.content = content

# 拿一个client出来
chroma_client = chromadb.PersistentClient(path="./")

# 等于是新建了一个数据库
# collection = chroma_client.create_collection(name="my_collection")

# 拿数据库
collection = chroma_client.get_or_create_collection(name="my_collection")

#新增
# collection.add(
#     documents=["This is a document", "This is another document"],
#     metadatas=[{"source": "my_source"}, {"source": "my_source"}],
#     ids=["id1", "id2"]
# )

# 查询
results = collection.query(
    query_texts=["This is a document"],
    n_results=1
)
def add_doc(collection_point:Collection,doc:MyDoc):
    """给库新增文档，并且ids增加了自增功能"""
    max_doc_num = collection_point.count()
    print(max_doc_num)
    inc_id = str(max_doc_num + 1)
    collection_point.add(
        documents=[doc.content],ids=[inc_id]
    )

print(results)
# 创建一个MyDoc的实例对象new_doc
new_doc = MyDoc("A whole new world")
# 使用点操作符（.）为new_doc添加属性content，值设置为"A whole new world"
add_doc(collection,new_doc)

cccs_result=collection.get()

ui.label('嵌入式向量数据库 chromadb 管理器')

def get_ids(collections)->List[str]:
    """从collection.get()的结果中拿到the list of id"""
    ids = []
    ids = collections['ids']
    return ids

cccs_result_ids = get_ids(cccs_result)

def get_documents(collections)->List[str]:
    """从collection.get()的结果中拿到the list of documents str"""
    documents_records = []
    documents_records = collections['documents']
    return documents_records

cccs_result_documents = get_documents(cccs_result)

def build_documents_rows(ids:List[str],documents:List[str])->List[object]:
    documents_rows = []
    for i in range(len(ids)):
        temp_dict = {'id':ids[i],'documents':documents[i]}
        documents_rows.append(temp_dict)
        temp_dict = {}
    return documents_rows

documents_rows = build_documents_rows(cccs_result_ids,cccs_result_documents)

print(documents_rows)

columns = [
    {'field': 'id','sortable': True,'flex': 1},
    {'headerName':'文档','field': 'documents', 'editable': True,'cellEditor' : 'agLargeTextCellEditor','flex': 4},
]
# rows = [
#     {'id': 0, 'documents': 'Alice', 'age': 18},
#     {'id': 1, 'documents': 'Bob', 'age': 21},
#     {'id': 2, 'documents': 'Carol', 'age': 20},
# ]

rows = documents_rows

current_selected_collection = collection


def add_row():
    """点击按钮新增时所对应的界面逻辑，直接copy了add_doc的代码，有些欠妥，稍后重构"""
    # 把指针指向当前选择的数据库之上
    collection_point = current_selected_collection
    max_doc_num = collection_point.count()
    print(max_doc_num)
    inc_id = str(max_doc_num + 1)
    rows.append({'id': inc_id, 'documents': 'New doc content'})
    ui.notify(f'Added row with ID {inc_id}')
    collection_point.add(
        documents=['New doc content'],ids=[inc_id]
    )
    aggrid.update()

def update_row_by_id(row):
    """从全局变量当中拿到当前选中的数据库后，以id为参数更新某一条记录"""
    current_selected_collection.update(
        ids=[row["id"]],
        documents=[row["documents"]],
    )

def handle_cell_value_change(e):
    new_row = e.args['data']
    print(new_row)
    update_row_by_id(new_row)
    ui.notify(f'Updated row to: {e.args["data"]}')
    rows[:] = [row | new_row if row['id'] == new_row['id'] else row for row in rows]

def delete_by_ids(ids_will_be_deleted:List[str]):
    """从全局变量当中拿到当前选中的数据库后，以ids列表为入参删除对应的记录"""
    current_selected_collection.delete(ids=ids_will_be_deleted)

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

ui.run(title='Chromadb文档管理器',host="127.0.0.1",port=18081,show=False)
