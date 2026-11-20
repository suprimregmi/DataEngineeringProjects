from datetime import date
import redshift_connector
import re
import pandas as pd
from datetime import date
import redshift_connector
import re
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse
import pyperclip



## Stage 0

def stage_0run(**kwargs):
    file_path = kwargs.get("file_path")
    has_header = kwargs.get("has_header")
    database = kwargs.get("database")
    delimiter = kwargs.get("delimiter")
    input_fields = kwargs.get("input_fields")


    layout_name = None
    database_name = None  # initialize

    if file_path:
        # Case 1: already correct
        if file_path.startswith("s3://dasscrubinput") or file_path.startswith("s3://dev-dasscrubinput"):
            normalized_path = file_path

        # Case 2: incoming file path, leave as-is
        elif file_path.startswith("s3://incoming"):
            normalized_path = file_path

        # Case 3: stage0 relative path
        elif file_path.startswith("stage0/"):
            parts = [p for p in file_path.strip("/").split("/") if p]

            # stage0/abc_abc/cigna/...
            if len(parts) > 1:
                var = parts[1].upper()
                normalized_path = f"s3://dasscrubinput/{var}/PA/{file_path.lstrip('/')}"
            else:
                normalized_path = file_path

        else:
            normalized_path = file_path

        file_path = normalized_path

        # Parse path components
        if file_path.startswith("s3://"):
            parsed = urlparse(file_path)
            path_part = parsed.path.strip("/")
        else:
            path_part = file_path.strip("/")

        parts = [p for p in path_part.split("/") if p]

        # Last path component
        layout_name = parts[-1] if parts else None

        # Derive database name from stage0 path
        if database_name is None and "stage0" in parts:
            idx = parts.index("stage0")
            if idx + 1 < len(parts):
                database_name = parts[idx + 1][0].lower()
        else:
                database_name = database.lower()

        print("Datbase name is :     ", database_name)
        

    print(f"file_path={file_path}")
    print(f"layout_name={layout_name}")
    print(f"database={database_name}")
    print(f"header={has_header}")
    print(f"input_fields={input_fields}")

    today = date.today().strftime("%Y%m%d")
    schema_name = f"raw_sregmi_"
    #client_name = ''
    path  =file_path
    header_info = 'Y' if has_header ==True else 'N'
    layout_type = delimiter
    if layout_type =='f':
        layout_type = 'fixed'
    print(f"\nEntered Informations are: \nDatabase_Name = {database_name}, \nPath = {path},  \nToday's_Date = {today}, \nschema_name: {schema_name}, \nheader_info: {header_info} \nlayout_type:{layout_type} \nlayout_name:{layout_name}")

    print("\n Field Inputs \n")
    # def get_multiline_input():
    #     lines = []
    #     print("Enter your input (press Enter on an empty line to finish):")
    #     while True:
    #         line = input()
    #         if line:
    #             lines.append(line)
    #         else:
    #             break
    #     return '\n'.join(lines)

    #field_namesu = '\n'.join(input_fields.split())
    field_namesu = '\n'.join(
    field.strip()
    for field in input_fields
    if field.strip()
    )

    # DB Conn
    conn = redshift_connector.connect(
        host='redshift-hostaddress.amazonaws.com',
        database = database_name,
        user='suprim_regmi',
        password='test_password'
    )
    cursor = conn.cursor()
    conn.rollback()
    conn.autocommit = True
    conn.run("VACUUM")
    cursor = conn.cursor()

    print("\n\n\n***---- DB Connected --***\n")

    def Query_Executor(queries_lists):
        for queries in queries_lists:
            cursor = conn.cursor()
            cursor.execute(queries)
            cursor.close()
    sql  = f"select create_schema('{today}','{schema_name}','')"
    print(sql)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.execute(sql)
    result = cursor.fetchall()
    input_string = result
    queries = []
    for query_string in input_string[0]:
        matches = re.findall(r'(create.*?;)', query_string, re.IGNORECASE | re.DOTALL)
        queries.extend(matches)

    for i, query in enumerate(queries, start=1):
        print(f"Query {i}: {query}")
    query_1 = queries[0]
    query_2 = queries[1]

    clean_query = query_1.strip().replace("\n", " ")
    Create_Ext_Schema = clean_query.split(";")[0] + ";"
    clean_query2 = query_2.strip().replace("\n", " ")
    Create_Schema = clean_query2.split(";")[0] + ";" 
    Create_Schema = (re.sub(' +',' ',Create_Schema))
    Create_Ext_Schema = (re.sub(' +',' ',Create_Ext_Schema))
    Query1 = [Create_Schema,Create_Ext_Schema]
    file_path =file_path+'/'

    # Creating Schema
    Query_Executor(Query1)
    print("\n***---- Schema Created --***\n")
    sql2 = f"SELECT raw_import_qa('{today}','{schema_name}','{layout_name}','{layout_type}','{header_info}','{file_path}', \n'{field_namesu}')";
    print("\n Next Query: ", sql2)

    # Function to execute SQL queries and extract individual queries
    def extract_queries(cursor, sql_query):
        cursor.execute(sql_query)
        result = cursor.fetchall()
        input_string = result[0] if result else []  # Extracting first element if result is not empty
        queries = []
        for query_string in input_string:
            matches = re.findall(r'(.*?;)', query_string, re.IGNORECASE | re.DOTALL)
            queries.extend(matches)
        return queries[:5]  # Take the first 5 queries

    Query_Lists = extract_queries(cursor, sql2)
    # Trim spaces and remove extra lines
    query_0 = '\n'.join(line.strip() for line in Query_Lists[0].strip().split('\n') if line.strip())
    query_1 = Query_Lists[1]
    query_2 = '\n'.join(line.strip() for line in Query_Lists[2].strip().split('\n') if line.strip())
    query_3 = '\n'.join(line.strip() for line in Query_Lists[3].strip().split('\n') if line.strip())
    query_4 = '\n'.join(line.strip() for line in Query_Lists[4].strip().split('\n') if line.strip())
    FoolNFinal = [query_0, query_1, query_2, query_3,query_4]

    print("\n***---- Final Queries Executing --***\n")
    cursor = conn.cursor()
    cursor.execute(query_0)
    cursor.execute(query_1)
    cursor.execute(query_2)
    cursor.execute(query_3)
    cursor.execute(query_4)


    print("\n***---- View Created --***\n")
    raw_table  = f"select * from {schema_name}_{today}.{layout_name} limit 20;"
    cursor.execute(raw_table)
    result: pd.DataFrame = cursor.fetch_dataframe()
    print(result.head(1))
    # cursor.execute(raw_table)
    # result: pd.DataFrame = cursor.fetch_dataframe()
    # print(result.tail(2))


    print("\n Viewing Sample Data:\n")

    cursor.execute(raw_table)
    result: tuple = cursor.fetchall()
    print(result)

    cursor.close()
    conn.close()
    print("\n***---- Connection Closed --***\n")

    # sql_script = '\n'.join([Create_Schema, Create_Ext_Schema,sql2,FoolNFinal[0],FoolNFinal[1], FoolNFinal[2],FoolNFinal[3], FoolNFinal[4] ])
    # filename = f"RawScripts/Sql_Script__{schema_name}_{today}.txt"
    print("Raw Table:  \t", raw_table)
    # Writing to file
    # with open(filename, 'w') as file:
    #     file.write(sql_script)

    # print("\n***---- Queries Printed to --***\n:", filename)

    # your logic here
    #result = f"Stage0 processed: {input_value}"
    return raw_table

## Stage 1


def stage_1run(**kwargs):
    s1dump_path = kwargs.get("s1dump_path")
    a_value = kwargs.get("query_mode")
    path = s1dump_path

    database_name = None  # initialize
    parts = path.split('/')
    client_name = None
    for i, part in enumerate(parts):
        if "dasscruboutput-intermediate" in part:
            client_name = parts[i+1]
            break
    for i, part in enumerate(parts):
        if "PA" in part or "CM" in part:
            schema_name = parts[i+1]+"_stage1srst"
            break
    database_name = (client_name[0]).lower()
    split_path = path.split('dasscruboutput-intermediate/')
    op_var = 's3://dasscruboutput-intermediate/'
    today = date.today().strftime("%Y%m%d")
    var = split_path[1]
    print(f"\nEntered Informations are: \nDatabase_Name = {database_name}, \nExtractedPath = {var}, \nClient_Name = {client_name}, \nToday's_Date = {today}, \nschema_name: {schema_name}")


    # DB Conn
    conn = redshift_connector.connect(
        host='redshift.amazonaws.com',
        database = database_name,
        user='suprim_regmi',
        password='test_password'
    )
    cursor = conn.cursor()
    conn.rollback()
    conn.autocommit = True
    conn.run("VACUUM")
    cursor = conn.cursor()

    print("***---- DB Connected --***")


    def Query_Executor(queries_lists):
        for queries in queries_lists:
            cursor = conn.cursor()
            cursor.execute(queries)
            cursor.close()

    sql  = f"select create_schema('{today}','{schema_name}','{'s3://dasscruboutput-intermediate/'+var}')"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.execute(sql)
    result = cursor.fetchall()
    input_string = result
    queries = []
    for query_string in input_string[0]:
        matches = re.findall(r'(create.*?;)', query_string, re.IGNORECASE | re.DOTALL)
        queries.extend(matches)

    for i, query in enumerate(queries, start=1):
        print(f"Query {i}: {query}")
    query_1 = queries[0]
    query_2 = queries[1]

    clean_query = query_1.strip().replace("\n", " ")
    Create_Ext_Schema = clean_query.split(";")[0] + ";"  
    clean_query2 = query_2.strip().replace("\n", " ")
    Create_Schema = clean_query2.split(";")[0] + ";" 
    Create_Schema = (re.sub(' +',' ',Create_Schema))
    Create_Ext_Schema = (re.sub(' +',' ',Create_Ext_Schema))
    Query1 = [Create_Schema,Create_Ext_Schema]

    # Creating Schema
    Query_Executor(Query1)

    print("\n **------ Schema Created Now Enter The Data Type---------**\n")

    # Define file variables
    e, m, p, pa, b, l, h, pr, c, v, di, ve = (
        "eligibility.csv",
        "medical.csv",
        "pharmacy.csv",
        "participation.csv",
        "biometric.csv",
        "lab.csv",
        "hra.csv",
        "provider.csv",
        "contentagnostic.csv",
        "vision.csv",
        "disability.csv",
        "vendor.csv"
    )

    file_mapping = {
        'd': ['Eligibility.csv', 'Medical.csv', 'Pharmacy.csv'],
        'e': e,
        'm': m,
        'p': p,
        'pa': pa,
        'b': b,
        'l': l,
        'h': h,
        'pr': pr,
        'c': c,
        'v': v,
        'di': di,
        've': ve
    }
    query_mode = 'd' if a_value is None or a_value == '' else a_value.lower()
    print("Available modes specific e, m, p, pa, b, l, h, pr, c, v, di, ve or d  ")
    print("Current Mode: ",query_mode)
    #query_mode = input("Enter datatype default d, specific e, m, p, pa, b, l, h, pr, c, v, di, ve: ").lower()
    Elig_Query,Med_Query, Rx_Query,Final_Query_SpecificCase  ,Elig_queries, Med_queries, Rx_queries= '', '', '', '' ,'','',''# for exporting purpose

    # Assign files based on query mode
    files = file_mapping.get(query_mode, [])
    # print("The values in files are:", files)

    # Define query builder function
    def query_builder(today, schema, op_var, file_path, files):
        queries = {}
        for value in files if isinstance(files, list) else [files]:
            name = value[:-4].lower()  # Extracting name without extension
            query_suffix = '_530' #if value != 'Contentagnostic.csv' else '_content_530'
            queries[name] = f"Select perm_stage1_{name}{query_suffix}('{today}','{schema}','{op_var+file_path+name}/')"
        return queries

    # Call query builder function
    result_queries = query_builder(today, schema_name, op_var, var, files)
    Global_Queries = [] #init empty lists
    # Assign queries to variables based on query mode
    if query_mode == 'd':
        Eligibility_Query = result_queries.get('eligibility', '')
        Medical_Query = result_queries.get('medical', '')
        Pharmacy_Query = result_queries.get('pharmacy', '')
        Global_Queries  = [Eligibility_Query, Medical_Query, Pharmacy_Query]
    else:
        Specific_Query = []  
        for query_name, query in result_queries.items():
            globals()[query_name + '_Query'] = query  # Assign query to respective variable
            Specific_Query.append(query)  # Append query to Global_Queries

    QueryLists = []


    # Print queries and append them to QueryLists
    for query_name, query in result_queries.items():
        print(f"{query_name}_Query: {query}")
        QueryLists.append(query)

    #print("QueryLists:", QueryLists)
    Final_Queries = Specific_Query if not Global_Queries else Global_Queries



    # Function to execute SQL queries and extract individual queries
    def extract_queries(cursor, sql_query):
        cursor.execute(sql_query)
        result = cursor.fetchall()
        input_string = result[0] if result else []  # Extracting first element if result is not empty
        queries = []
        for query_string in input_string:
            matches = re.findall(r'(.*?;)', query_string, re.IGNORECASE | re.DOTALL)
            queries.extend(matches)
        return queries[:5]  # Take the first 5 queries



    if Global_Queries != []:
        Elig_Query = Final_Queries[0]
        Med_Query = Final_Queries[1]
        Rx_Query = Final_Queries[2]
        Elig_queries = extract_queries(cursor, Elig_Query)
        Med_queries = extract_queries(cursor, Med_Query)
        Rx_queries = extract_queries(cursor, Rx_Query)
        Query_Executor(Elig_queries)
        Query_Executor(Med_queries)
        Query_Executor(Rx_queries)
        
    else:
        Final_Query_SpecificCase = extract_queries(cursor, Specific_Query[0])
        Query_Executor(Final_Query_SpecificCase)


    variable_name = file_mapping.get(query_mode)
    if query_mode:
        dtype = variable_name[:-4]
        print("Extracted name:", dtype)
    else:
        print("Invalid input. Please enter a valid letter.")

    if Global_Queries != []:
        Elig_Select = f"select * from {schema_name}_{today}.perm_stage1_eligibility limit 20;"
        Med_Select = f"select * from {schema_name}_{today}.perm_stage1_medical limit 20;"
        Rx_Select = f"select * from {schema_name}_{today}.perm_stage1_pharmacy limit 20;"
        concatenated_text = Elig_Select + '\n' + Med_Select + '\n' + Rx_Select
        pyperclip.copy(concatenated_text)
        print("Select Statements:\n", concatenated_text)
        sql  = Elig_Select
        cursor.execute(sql)
        result: pd.DataFrame = cursor.fetch_dataframe()
        print(result.head(1))
        # cursor.execute(sql)
        # result: pd.DataFrame = cursor.fetch_dataframe()
        # print(result.tail(2))
        print("/n/ ---Elig----")
        sql  = Med_Select
        cursor.execute(sql)
        result: pd.DataFrame = cursor.fetch_dataframe()
        print(result.head(1))
        # cursor.execute(sql)
        # result: pd.DataFrame = cursor.fetch_dataframe()
        # print(result.tail(1))
        print("/n/ ---Med----")
        sql  = Rx_Select
        cursor.execute(sql)
        result: pd.DataFrame = cursor.fetch_dataframe()
        print(result.head(1))
        # cursor.execute(sql)
        # result: pd.DataFrame = cursor.fetch_dataframe()
        # print(result.tail(1))
        print("/n/ ----Rx---")
    else:
        Custom_Select = f"select * from {schema_name}_{today}.perm_stage1_{dtype} limit 20;"
        pyperclip.copy(Custom_Select)
        print("Select Statements:\n", Custom_Select)

        sql  = Custom_Select
        cursor.execute(sql)
        result: pd.DataFrame = cursor.fetch_dataframe()
        print(result.head(5))
        cursor.execute(sql)
        result: pd.DataFrame = cursor.fetch_dataframe()
        print(result.tail(5))
        print("/n/ ----Rx---")


    # Convert lists to strings (if necessary)
    if isinstance(Create_Schema, list):
        Create_Schema = '\n'.join(Create_Schema)

    if isinstance(Create_Ext_Schema, list):
        Create_Ext_Schema = '\n'.join(Create_Ext_Schema)

    if isinstance(Elig_Query, list):
        Elig_Query = '\n'.join(Elig_Query)

    if isinstance(Med_Query, list):
        Med_Query = '\n'.join(Med_Query)

    if isinstance(Rx_Query, list):
        Rx_Query = '\n'.join(Rx_Query)

    if isinstance(Final_Query_SpecificCase, list):
        Final_Query_SpecificCase = '\n'.join(Final_Query_SpecificCase)

    if isinstance(Elig_queries, list):
        Elig_queries = '\n'.join(Elig_queries)

    if isinstance(Med_queries, list):
        Med_queries = '\n'.join(Med_queries)

    if isinstance(Rx_queries, list):
        Rx_queries = '\n'.join(Rx_queries)
    # Concatenate the strings with newline characters
    #sql_script = '\n'.join([Create_Schema, Create_Ext_Schema, Elig_Query, Med_Query, Rx_Query, Final_Query_SpecificCase, Elig_queries, Med_queries, Rx_queries])
    return concatenated_text


# Stage3 Script


def stage_3run(**kwargs):

    s3dump_path = kwargs.get("s3dump_path")
    a_value = kwargs.get("query_mode")
    path = s3dump_path
  
    parts = s3dump_path.split('/')
    client_name = None
    for i, part in enumerate(parts):
        if "dasscruboutput" in part:
            client_name = parts[i+1]
            break
    for i, part in enumerate(parts):
        if "PA" in part or "CM" in part:
            schema_name = parts[i+1]+'_stg3_srtest' 
            break
    database_name = (client_name[0]).lower()
    split_path = path.split('dasscruboutput/')
    op_var = 's3://dasscruboutput/'
    today = date.today().strftime("%Y%m%d")
    var = split_path[1]
    print(f"\nEntered Informations are: \nDatabase_Name = {database_name}, \nExtractedPath = {var}, \nClient_Name = {client_name}, \nToday's_Date = {today}, \nschema_name: {schema_name}")

    # DB Conn
    conn = redshift_connector.connect(
        host='some host address.amazonaws.com',
        database = database_name,
        user = 'user',
        password = ''
    )
    cursor = conn.cursor()
    conn.rollback()
    conn.autocommit = True
    conn.run("VACUUM")
    cursor = conn.cursor()
    print("\n **------DB Connnected---------**\n")

    def Query_Executor(queries_lists):
        for queries in queries_lists:
            cursor = conn.cursor()
            cursor.execute(queries)
            cursor.close()

    sql  = f"select create_schema('{today}','{schema_name}','{'s3://dasscruboutput/'+var}')"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.execute(sql)
    result = cursor.fetchall()
    input_string = result
    queries = []
    for query_string in input_string[0]:
        matches = re.findall(r'(create.*?;)', query_string, re.IGNORECASE | re.DOTALL)
        queries.extend(matches)

    for i, query in enumerate(queries, start=1):
        print(f"Query {i}: {query}")
    query_1 = queries[0]
    query_2 = queries[1]

    clean_query = query_1.strip().replace("\n", " ")
    Create_Ext_Schema = clean_query.split(";")[0] + ";"  
    clean_query2 = query_2.strip().replace("\n", " ")
    Create_Schema = clean_query2.split(";")[0] + ";" 
    Create_Schema = (re.sub(' +',' ',Create_Schema))
    Create_Ext_Schema = (re.sub(' +',' ',Create_Ext_Schema))
    print("\n **------ Schema Created Now Enter The Data Type---------**\n")
    Query1 = [Create_Schema,Create_Ext_Schema]

    # Creating Schema
    Query_Executor(Query1)

    # Define file variables
    e, m, p, pa, b, l, h, pr, c, v, di, ve = (
        "Eligibility.csv",
        "Medical.csv",
        "Pharmacy.csv",
        "Participation.csv",
        "Biometric.csv",
        "Lab.csv",
        "Hra.csv",
        "Provider.csv",
        "Contentagnostic.csv")