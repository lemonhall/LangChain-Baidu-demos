https://github.com/zauberzeug/nicegui/tree/main/examples/chat_with_ai

sudo docker run -it --restart always -p 1280:8080 -e PUID=$(id -u) -e PGID=$(id -g) -v $(pwd)/:/app/ zauberzeug/nicegui:latest


2、加上密码
https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/

sudo apt install  apache2-utils 

sudo htpasswd -c /etc/apache2/.htpasswd lemonhall

我设置成了和我主机的lemonhall的主密码一致的一个，否则记不住的

cat /etc/apache2/.htpasswd

location /api {
    auth_basic           "Administrator’s Area";
    auth_basic_user_file /etc/apache2/.htpasswd; 
}

sudo systemctl reload nginx

![30a373045cd2dea7e6f61d1d43d1814](https://github.com/lemonhall/LangChain-Baidu-demos/assets/637919/51688c82-38fa-4cf4-9e82-127df891b766)

3、那个该死的正则表达式：

讲解一下：

第一：(.*?)这就是group1了，这是匹配出来的第一个变量你可以看做是

第二：(.*?)第二个匹配的变量，之前写的有问题，导致匹配出来的就是个鸡毛，我后面加了Observation，来限定

第三：action_match = re.search(regex,text,re.DOTALL)

这句话的意思是，带上所有的字符，包含了所有的换行符

第四：

            action_input = action_input.replace("```sql","")
            action_input = action_input.replace("```","")
            action_input = action_input.strip()
           
这三句是专门用来伺候：

Based on the most recent Observation, we still have not received the actual result of the query. 
Let's check if there was an error executing the query.
Action: sql_db_query
Action Input:
```sql
SELECT * FROM notes LIMIT 1;
```
Observation:
这种SQL输出的，反正LLM的输出前期百怪

第五：其实这个if-else的结构就是这样来解释

如果找到了有Action语句，那就开干，按照你想的去做

如果答案里有Answer，同时没有Aciton，那就输出最后结果，这整个过程就结束了

includes_answer = FINAL_ANSWER_ACTION in text
        regex = (
            r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:\s*(.*?)Observation"
        )
        action_match = re.search(regex,text,re.DOTALL)
        if action_match:
            sth
        elif includes_answer:
            sth

