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
#using the AzWebJobs environment variable, connect to azure table storage
stor_acc_conn_string = os.environ['AzureWebJobsStorage']
tables = TableService(connection_string=stor_acc_conn_string)
################################################################################
def main(req: func.HttpRequest) -> func.HttpResponse:
    '''when an inbound request is recieved, query table
     storage and formulate a json dictionary response'''
    try:
        accounts = tables.query_entities\
        ('apps', filter="PartitionKey eq 'mfaseed'") #, select='AccountName'
    except:
        #handle borks
        return func.HttpResponse('nah')
    #create a structure to host all further applications found (nested)
    toplevel = []
    #for each account returned, formulate a object from table storage and respond
    for account in accounts:
        applications = {}
        app = account.AccountName
        setname = account.CustomName
        uuid = account.RowKey
        applications['uuid'] = uuid
        applications['appname'] = app
        applications['custom'] = setname
        toplevel.append(applications)
    json_data = json.dumps(toplevel)
    return func.HttpResponse(json_data)
