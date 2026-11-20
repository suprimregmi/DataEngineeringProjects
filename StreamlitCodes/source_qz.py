import redshift_connector
import redshift_connector
import pandas as pd
from jinja2 import Template
from jinja2 import Template
from datetime import date
import json
import os



# Medical fields: shcema, group filter name, filter_expression,  
# Column names mbr_id as rule1 like thsee

## Source QZ
def med_query_generator(schema_name=None, group_filter=None, group_info =None, additional_filter=None):
#def query_builder(schema_name = None, group_filte =None, additional_filter =None):

    print("entered values",schema_name ,"group_filte: ", group_filter , type(group_filter))
    # Load config
    with open("configs_json.json", "r") as f:
        config = json.load(f)

    # Update only if values are passed
    if schema_name!= '':
        config["table_name"] = schema_name

    if group_filter != '':
        config["table_filter1"] = group_filter

    # Save updated config back to file
    with open("configs_json.json", "w") as f:
        json.dump(config, f, indent=4)
        f.flush()   # force write
        os.fsync(f.fileno())

    # Use values from config
    
    schema_name = config["table_name"]
    group_filter = config["table_filter1"]
    group_info = config["group_filter"]
    table_name = "perm_stage1" if "stage1" in schema_name else schema_name
    print("New values values",schema_name , group_filter )
    print("from Json", config["table_name"],config["table_filter1"] )
    with open("SQLs/source_queries.sql", "r") as f:
        template = Template(f.read())


    print("Inputs:", schema_name, group_filter,group_info,group_info ,additional_filter)

    # reading updated values
    group_filter = config.get("table_filter1")
    schema_name =  config.get("table_name")
    #debug = config.get("debug")
    with open("SQLs/stage_queries.sql", "r") as f:
        template = Template(f.read())

    query = template.render(
        table=table_name,
        schema=schema_name,
        group_filter=group_filter,
        vendor=bool(additional_filter),
        vendor_name=additional_filter
    )
    

    return query
