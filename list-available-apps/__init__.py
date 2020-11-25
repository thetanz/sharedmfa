#!/usr/bin/env python3
'''key doer'''
################################################################################
__status__ = "development"
__maintainer__ = "josh highet"
__email__ = "josh.highet@theta.co.nz"
################################################################################
import os
import json
import azure.functions as func
from azure.cosmosdb.table.tableservice import TableService
################################################################################
stor_acc_conn_string = os.environ['AzureWebJobsStorage']
tables = TableService(connection_string=stor_acc_conn_string)
################################################################################
def main(req: func.HttpRequest) -> func.HttpResponse:
    try: accounts = tables.query_entities('apps', filter="PartitionKey eq 'mfaseed'") #, select='AccountName'
    except: return func.HttpResponse('nah')
    toplevel = []
    for account in accounts:
        applications={}
        app = account.AccountName
        setname = account.CustomName
        uuid = account.RowKey
        applications['uuid'] = uuid
        applications['appname'] = app
        applications['custom'] = setname
        toplevel.append(applications)
    json_data = json.dumps(toplevel)
    return func.HttpResponse(json_data)