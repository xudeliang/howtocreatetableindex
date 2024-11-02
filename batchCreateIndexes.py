import os
import re

def find_sql_statements(filepath):
    """扫描文件中的所有行，查找包含 SQL 关键词的行。"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()
    
    sql_statements = []
    for line in lines:
        line_lower = line.strip().lower()
        if "from" in line_lower or "update" in line_lower:
            sql_statements.append(line.strip())
    return sql_statements

def extract_table_and_fields(sql):
    """从 SQL 语句中提取表名和 WHERE 子句中的字段。"""
    # 匹配 FROM <table> WHERE <conditions> 或 UPDATE <table> SET ... WHERE <conditions>
    from_where_pattern = re.compile(r"from\s+(\w+)\s+where\s+(.+)", re.IGNORECASE)
    update_where_pattern = re.compile(r"update\s+(\w+)\s+set\s+.*\s+where\s+(.+)", re.IGNORECASE)

    match = from_where_pattern.search(sql) or update_where_pattern.search(sql)
    if not match:
        return None, None

    table_name = match.group(1)
    where_clause = match.group(2)

    # 从 WHERE 子句中提取字段
    fields = re.findall(r"\b(\w+)\s*=", where_clause)
    return table_name, fields

def create_index_statements(table_fields_map):
    """为每个表和字段组合生成联合索引的 SQL 语句。"""
    index_statements = set()  # 使用集合去重
    for table, fields_set in table_fields_map.items():
        fields_list = list(fields_set)
        if len(fields_list) > 1:
            # 创建联合索引
            index_name = f"{table}_{'_'.join(fields_list)}_idx"
            fields_str = ', '.join(fields_list)
            index_statements.add(f"CREATE INDEX {index_name} ON {table} ({fields_str});")
    return index_statements

def main():
    # 存储表和其对应的 WHERE 子句字段
    table_fields_map = {}

    # 遍历当前目录和子目录中的所有 .php 和 .java 文件
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.php') or file.endswith('.java'):
                filepath = os.path.join(root, file)
                sql_statements = find_sql_statements(filepath)
                
                for sql in sql_statements:
                    table, fields = extract_table_and_fields(sql)
                    if table and fields:
                        if table not in table_fields_map:
                            table_fields_map[table] = set()
                        table_fields_map[table].update(fields)

    # 创建去重后的索引语句
    index_statements = create_index_statements(table_fields_map)
    
    # 将索引语句写入文件
    with open('indexOut.txt', 'w', encoding='utf-8') as output_file:
        output_file.write("\n".join(index_statements))
    
    print("索引语句已写入 indexOut.txt 文件。")

if __name__ == "__main__":
    main()
