#!/usr/bin/env python3
'''key doer'''
################################################################################
__status__ = "development"
__maintainer__ = "josh highet"
__email__ = "josh.highet@theta.co.nz"
################################################################################
import os
import json
import pyotp
import logging
import datetime
import azure.functions as func
import urllib.parse as urlparse
from urllib.parse import parse_qs
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
################################################################################
kvname = os.environ["KEY_VAULT_NAME"]
kvfqdn = f"https://{kvname}.vault.azure.net"
credential = DefaultAzureCredential()
kv = SecretClient(vault_url=kvfqdn, credential=credential)
################################################################################
sacc_key = os.environ["STORAGE_ACCOUNT_KEY"]
tables = TableService(account_name='saprodaemfaforall', account_key=sacc_key)
################################################################################
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('http trigger function processed request.')
    accounts = tables.query_entities('mfaforall', filter="PartitionKey eq 'mfaseed'") #, select='AccountName'
    data = {}
    apps = {}
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