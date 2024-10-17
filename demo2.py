#!pip install git+https://github.com/openai/swarm.git

import os
from google.colab import userdata
os.environ["OPENAI_API_KEY"]=userdata.get('OPENAI_API_KEY')



import requests
from swarm import Swarm, Agent

def get_weather(latitude: float, longitude: float) -> str:
    """
    使用Open-Meteo API获取给定坐标的当前天气。

    参数:
    latitude (float): 纬度
    longitude (float): 经度

    返回:
    str: 包含当前温度和风速的天气信息JSON字符串
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        current = data['current']
        return str(current)  # 返回JSON字符串
    else:
        return '{"error": "无法获取天气数据"}'

def get_coordinates(location: str) -> str:
    """
    获取给定位置名称的坐标。

    参数:
    location (str): 位置名称

    返回:
    str: 包含纬度和经度的JSON字符串
    """
    coordinates = {
        "纽约": (40.7128, -74.0060),
        "伦敦": (51.5074, -0.1278),
        "东京": (35.6762, 139.6503),
        "巴黎": (48.8566, 2.3522),
        "柏林": (52.5200, 13.4050)
    }
    lat, lon = coordinates.get(location.lower(), (0, 0))
    return f'{{"latitude": {lat}, "longitude": {lon}}}'

client = Swarm()

weather_agent = Agent(
    name="天气助手",
    instructions="""
    你是一个有帮助的天气助手。当被问到特定位置的天气时：
    1. 使用get_coordinates函数获取该位置的坐标。
    2. 使用get_weather函数获取天气数据。
    3. 解析返回的JSON数据，提供一个友好的回复，包含天气信息。
    如果无法识别该位置，礼貌地通知用户并建议他们尝试一个主要城市。
    """,
    functions=[get_coordinates, get_weather]
)

def run_weather_query(query: str) -> str:
    """
    运行天气查询并返回结果。

    参数:
    query (str): 用户的天气查询

    返回:
    str: Agent的响应
    """
    messages = [{"role": "user", "content": query}]
    response = client.run(agent=weather_agent, messages=messages)
    return response.messages[-1]["content"]

# 使用示例
print(run_weather_query("纽约的天气怎么样？"))
print(run_weather_query("柏林的天气如何？"))
print(run_weather_query("巴黎的天气如何？"))
print(run_weather_query("伦敦的天气如何？"))
print(run_weather_query("东京的天气怎么样？"))
print(run_weather_query("告诉我小村庄的天气"))





from swarm import Swarm, Agent

client = Swarm()

# 模拟数据库
accounts = {
    123: {"name": "James", "balance": 1000},
    456: {"name": "Emma", "balance": 1500},
}

def instructions(context_variables):
    name = context_variables.get("name", "User")
    return f"You are a helpful banking assistant. Greet {name} and assist with their banking needs."

def check_balance(context_variables: dict):
    user_id = context_variables.get("user_id")
    if user_id in accounts:
        return f"Your current balance is ${accounts[user_id]['balance']:.2f}"
    return "Account not found."

def deposit(context_variables: dict):
    user_id = context_variables.get("user_id")
    amount = context_variables.get("amount", 0)
    if user_id in accounts and amount > 0:
        accounts[user_id]['balance'] += amount
        return f"Deposit of ${amount:.2f} successful. New balance is ${accounts[user_id]['balance']:.2f}"
    return "Deposit failed. Please check your account and amount."

def withdraw(context_variables: dict):
    user_id = context_variables.get("user_id")
    amount = context_variables.get("amount", 0)
    if user_id in accounts and 0 < amount <= accounts[user_id]['balance']:
        accounts[user_id]['balance'] -= amount
        return f"Withdrawal of ${amount:.2f} successful. New balance is ${accounts[user_id]['balance']:.2f}"
    return "Withdrawal failed. Please check your account and amount."

agent = Agent(
    name="BankingAgent",
    instructions=instructions,
    functions=[check_balance, deposit, withdraw],
)

def process_request(user_id, message):
    context_variables = {"user_id": user_id, "name": accounts[user_id]["name"]}
    response = client.run(
        messages=[{"role": "user", "content": message}],
        agent=agent,
        context_variables=context_variables,
    )
    return response.messages[-1]["content"]

# 示例使用
user_id = 123
print(process_request(user_id, "Hi! What's my current balance?"))
print(process_request(user_id, "I'd like to deposit $500"))
context_variables = {"user_id": user_id, "amount": 500}
print(deposit(context_variables))
print(process_request(user_id, "What's my new balance?"))
print(process_request(user_id, "I want to withdraw $200"))
context_variables = {"user_id": user_id, "amount": 200}
print(withdraw(context_variables))
print(process_request(user_id, "What's my final balance?"))












import sqlite3
import re
from swarm import Swarm, Agent
from tabulate import tabulate

# 初始化 Swarm 客户端
client = Swarm()

# 创建内存数据库连接
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# 创建员工表
cursor.execute('''
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    department TEXT,
    salary REAL
)
''')

# 插入20条示例数据
employees = [
    (1, '张伟', 'IT', 75000),
    (2, '王芳', 'HR', 65000),
    (3, '李斯', '销售', 80000),
    (4, '赵辉', '市场', 70000),
    (5, '陈明', 'IT', 72000),
    (6, '杨丽', 'HR', 68000),
    (7, '周浩', '销售', 82000),
    (8, '吴娜', '市场', 71000),
    (9, '刘洋', 'IT', 76000),
    (10, '孙琳', 'HR', 67000),
    (11, '朱峰', '销售', 81000),
    (12, '徐婷', '市场', 72000),
    (13, '郭震', 'IT', 74000),
    (14, '马梅', 'HR', 66000),
    (15, '胡勇', '销售', 83000),
    (16, '林梅', '市场', 73000),
    (17, '韩磊', 'IT', 77000),
    (18, '董芳', 'HR', 69000),
    (19, '萧峰', '销售', 84000),
    (20, '沈丹', '市场', 74000)
]
cursor.executemany('INSERT INTO employees VALUES (?,?,?,?)', employees)
conn.commit()

def instructions(context_variables):
    return """你是一个能够将中文自然语言查询转换为SQL查询的AI助手。
    数据库有一个名为'employees'的表，包含以下列：id, name, department, salary。
    只返回SQL查询，不要包含任何其他文本或解释。支持复杂查询，如比较、排序和聚合函数。"""

def clean_sql_query(sql_query):
    """清理SQL查询，移除可能的Markdown格式和多余空白"""
    cleaned = re.sub(r'```sql\s*|\s*```', '', sql_query).strip()
    return cleaned

def execute_sql(sql_query):
    """执行SQL查询并返回结果"""
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        return f"SQL错误: {e}"

def explain_query(sql_query):
    """提供更具体的SQL查询解释"""
    parts = sql_query.upper().split()
    explanation = "这个查询"
    
    if 'SELECT' in parts:
        select_index = parts.index('SELECT')
        from_index = parts.index('FROM')
        fields = ', '.join(parts[select_index+1:from_index]).lower()
        table = parts[from_index+1].lower()
        explanation += f"从{table}表中获取{fields}"
    
    if 'WHERE' in parts:
        where_index = parts.index('WHERE')
        condition = ' '.join(parts[where_index+1:]).lower()
        explanation += f"，条件是{condition}"
    
    if 'ORDER BY' in parts:
        order_index = parts.index('ORDER')
        order = ' '.join(parts[order_index+2:]).lower()
        explanation += f"，结果按{order}排序"
    
    if 'LIMIT' in parts:
        limit_index = parts.index('LIMIT')
        limit = parts[limit_index+1]
        explanation += f"，只显示前{limit}条结果"
    
    return explanation + "。"

def format_results(results, sql_query):
    """格式化查询结果，添加上下文和单位"""
    if not results or len(results) == 0:
        return "没有找到匹配的结果。"
    
    if isinstance(results, str):  # 错误消息
        return results
    
    headers = [description[0] for description in cursor.description]
    
    # 为薪水添加单位
    if 'salary' in headers:
        salary_index = headers.index('salary')
        results = [list(row) for row in results]
        for row in results:
            row[salary_index] = f"{row[salary_index]}元"
    
    formatted_results = tabulate(results, headers=headers, tablefmt="grid")
    
    # 添加结果上下文
    if len(results) == 1 and 'name' in headers and 'salary' in headers:
        name_index = headers.index('name')
        salary_index = headers.index('salary')
        context = f"{results[0][name_index]}的薪水是{results[0][salary_index]}"
        return f"{context}\n\n{formatted_results}"
    
    return formatted_results

agent = Agent(
    name="SQLAgent",
    instructions=instructions,
)

def process_query(natural_language_query):
    """处理自然语言查询，转换为SQL，执行并返回结果"""
    # 使用 Swarm 将自然语言转换为 SQL
    response = client.run(
        messages=[{"role": "user", "content": natural_language_query}],
        agent=agent,
    )
    sql_query = clean_sql_query(response.messages[-1]["content"])
    
    # 执行 SQL 查询
    results = execute_sql(sql_query)
    
    # 获取查询解释
    explanation = explain_query(sql_query)
    
    # 格式化结果
    formatted_results = format_results(results, sql_query)
    
    return f"SQL查询: {sql_query}\n解释: {explanation}\n结果:\n{formatted_results}"

# 主程序循环
if __name__ == "__main__":
    print("欢迎使用text to SQL系统！代码由AI超元域原创")
    print("输入 'exit' 或 'quit' 退出程序。")
    print("本系统支持复杂查询，如比较、排序和聚合函数。")
    
    while True:
        user_input = input("\n请输入您的查询 (或 'exit' 退出): ")
        if user_input.lower() in ['exit', 'quit']:
            print("谢谢使用，再见！")
            break
        
        print(process_query(user_input))

# 关闭数据库连接
conn.close()











import sqlite3
import re
from swarm import Swarm, Agent
from tabulate import tabulate

# 初始化 Swarm 客户端
client = Swarm()

# 创建内存数据库连接
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# 创建员工表
cursor.execute('''
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    department_id INTEGER,
    salary REAL
)
''')

# 创建部门表
cursor.execute('''
CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name TEXT,
    location TEXT
)
''')

# 插入员工数据
employees = [
    (1, '张伟', 1, 75000),
    (2, '王芳', 2, 65000),
    (3, '李斯', 3, 80000),
    (4, '赵静', 4, 70000),
    (5, '陈明', 1, 72000),
    (6, '杨丽', 2, 68000),
    (7, '周浩', 3, 82000),
    (8, '吴娜', 4, 71000),
    (9, '刘洋', 1, 76000),
    (10, '孙琳', 2, 67000)
]
cursor.executemany('INSERT INTO employees VALUES (?,?,?,?)', employees)

# 插入部门数据
departments = [
    (1, 'IT', '北京'),
    (2, 'HR', '上海'),
    (3, '销售', '广州'),
    (4, '市场', '深圳')
]
cursor.executemany('INSERT INTO departments VALUES (?,?,?)', departments)

conn.commit()

def instructions(context_variables):
    return """你是一个能够将中文自然语言查询转换为SQL查询的AI助手。
    数据库有两个表：
    1. 'employees'表，包含以下列：id, name, department_id, salary
    2. 'departments'表，包含以下列：id, name, location
    只返回SQL查询，不要包含任何其他文本或解释。支持复杂查询，包括多表连接、比较、排序和聚合函数。"""

def clean_sql_query(sql_query):
    """清理SQL查询，移除可能的Markdown格式和多余空白"""
    cleaned = re.sub(r'```sql\s*|\s*```', '', sql_query).strip()
    return cleaned

def execute_sql(sql_query):
    """执行SQL查询并返回结果"""
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        return f"SQL错误: {e}"

def explain_query(sql_query):
    """提供更具体的SQL查询解释，包括多表查询"""
    parts = sql_query.upper().split()
    explanation = "这个查询"
    
    if 'SELECT' in parts:
        select_index = parts.index('SELECT')
        from_index = parts.index('FROM')
        fields = ', '.join(parts[select_index+1:from_index]).lower()
        tables = []
        for i in range(from_index+1, len(parts)):
            if parts[i] in ['WHERE', 'GROUP', 'ORDER', 'LIMIT']:
                break
            if parts[i] not in ['JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'ON', 'AND']:
                tables.append(parts[i].lower())
        tables = ', '.join(tables)
        explanation += f"从{tables}表中获取{fields}"
    
    if 'JOIN' in parts:
        explanation += "，进行了表连接"
    
    if 'WHERE' in parts:
        where_index = parts.index('WHERE')
        condition = ' '.join(parts[where_index+1:]).lower()
        explanation += f"，条件是{condition}"
    
    if 'GROUP BY' in parts:
        group_index = parts.index('GROUP')
        group = ' '.join(parts[group_index+2:]).lower()
        explanation += f"，按{group}进行分组"
    
    if 'ORDER BY' in parts:
        order_index = parts.index('ORDER')
        order = ' '.join(parts[order_index+2:]).lower()
        explanation += f"，结果按{order}排序"
    
    if 'LIMIT' in parts:
        limit_index = parts.index('LIMIT')
        limit = parts[limit_index+1]
        explanation += f"，只显示前{limit}条结果"
    
    return explanation + "。"

def format_results(results, sql_query):
    """格式化查询结果，添加上下文和单位"""
    if not results or len(results) == 0:
        return "没有找到匹配的结果。"
    
    if isinstance(results, str):  # 错误消息
        return results
    
    headers = [description[0] for description in cursor.description]
    
    # 为薪水添加单位
    if 'salary' in headers:
        salary_index = headers.index('salary')
        results = [list(row) for row in results]
        for row in results:
            row[salary_index] = f"{row[salary_index]}元"
    
    formatted_results = tabulate(results, headers=headers, tablefmt="grid")
    
    return formatted_results

agent = Agent(
    name="SQLAgent",
    instructions=instructions,
)

def process_query(natural_language_query):
    """处理自然语言查询，转换为SQL，执行并返回结果"""
    # 使用 Swarm 将自然语言转换为 SQL
    response = client.run(
        messages=[{"role": "user", "content": natural_language_query}],
        agent=agent,
    )
    sql_query = clean_sql_query(response.messages[-1]["content"])
    
    # 执行 SQL 查询
    results = execute_sql(sql_query)
    
    # 获取查询解释
    explanation = explain_query(sql_query)
    
    # 格式化结果
    formatted_results = format_results(results, sql_query)
    
    return f"SQL查询: {sql_query}\n解释: {explanation}\n结果:\n{formatted_results}"

# 主程序循环
if __name__ == "__main__":
    print("欢迎使用支持多表查询的中文自然语言到SQL转换系统！")
    print("输入 'exit' 或 'quit' 退出程序。")
    print("本系统支持复杂查询，包括多表连接、比较、排序和聚合函数。")
    
    while True:
        user_input = input("\n请输入您的查询 (或 'exit' 退出): ")
        if user_input.lower() in ['exit', 'quit']:
            print("谢谢使用，再见！")
            break
        
        print(process_query(user_input))

# 关闭数据库连接
conn.close()









from swarm import Swarm, Agent

# 创建Swarm客户端实例
client = Swarm()

# 定义专门的agents

# 需求分析agent
requirements_agent = Agent(
    name="Requirements Analysis Agent",
    instructions="You are a requirements analysis specialist. Analyze user requirements and create a detailed specification."
)

# 设计agent
design_agent = Agent(
    name="Design Agent",
    instructions="You are a software design specialist. Create a high-level design based on the requirements specification."
)

# 编码agent
coding_agent = Agent(
    name="Coding Agent",
    instructions="You are a coding specialist. Implement the design in clean, efficient code."
)

# 测试agent
testing_agent = Agent(
    name="Testing Agent",
    instructions="You are a software testing specialist. Review the code, identify potential bugs, and suggest improvements."
)

# 文档agent
documentation_agent = Agent(
    name="Documentation Agent",
    instructions="You are a technical documentation specialist. Create clear and comprehensive documentation for the code."
)

def generate_code(user_requirement):
    """
    多阶段代码生成函数
    
    参数:
    user_requirement (str): 用户提供的功能需求
    
    返回:
    dict: 包含需求规格、设计文档、代码和文档的字典
    """

    # 阶段1：需求分析
    req_response = client.run(
        agent=requirements_agent,
        messages=[{"role": "user", "content": f"Analyze these requirements: {user_requirement}"}]
    )
    requirements_spec = req_response.messages[-1]["content"]

    # 阶段2：设计
    design_response = client.run(
        agent=design_agent,
        messages=[{"role": "user", "content": f"Create a design based on this specification: {requirements_spec}"}]
    )
    design_doc = design_response.messages[-1]["content"]

    # 阶段3：编码
    coding_response = client.run(
        agent=coding_agent,
        messages=[{"role": "user", "content": f"Implement this design in code: {design_doc}"}]
    )
    initial_code = coding_response.messages[-1]["content"]

    # 阶段4：测试和优化
    testing_response = client.run(
        agent=testing_agent,
        messages=[{"role": "user", "content": f"Review and suggest improvements for this code: {initial_code}"}]
    )
    test_feedback = testing_response.messages[-1]["content"]

    # 根据测试反馈进行代码优化
    refinement_response = client.run(
        agent=coding_agent,
        messages=[
            {"role": "user", "content": f"Refine the code based on this feedback: {test_feedback}"},
            {"role": "user", "content": f"Original code: {initial_code}"}
        ]
    )
    refined_code = refinement_response.messages[-1]["content"]

    # 阶段5：文档编写
    doc_response = client.run(
        agent=documentation_agent,
        messages=[{"role": "user", "content": f"Create documentation for this code: {refined_code}"}]
    )
    documentation = doc_response.messages[-1]["content"]
     
    # 返回包含所有生成内容的字典
    return {
        "requirements": requirements_spec,
        "design": design_doc,
        "code": refined_code,
        "documentation": documentation
    }

# Example usage
user_requirement = "Create a Python function that calculates the Fibonacci sequence up to a given number, optimized for performance."
result = generate_code(user_requirement)

print("Generated Code:")
print(result["code"])
print("\nDocumentation:")
print(result["documentation"])




# 更新示例使用 - 贪吃蛇游戏
user_requirement = """
创建一个简单的贪吃蛇游戏，具有以下功能：
1. 使用Python的pygame库实现
2. 游戏在一个固定大小的窗口中运行
3. 蛇可以使用方向键控制移动
4. 随机生成食物，蛇吃到食物后长度增加
5. 当蛇撞到自己或边界时游戏结束
6. 显示当前得分（蛇的长度）
7. 实现基本的开始和结束界面
请提供游戏的核心逻辑代码和必要的注释。
"""

result = generate_code(user_requirement)

print("生成的贪吃蛇游戏代码:")
print(result["code"])
print("\n游戏文档:")
print(result["documentation"])
