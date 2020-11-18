#!/usr/bin/env python3
'''handle addition of new totp strings'''
################################################################################
__status__ = "development"
__maintainer__ = "josh highet"
__email__ = "josh.highet@theta.co.nz"
################################################################################
import os
import json
import logging
import azure.functions as func
import uuid
import pyotp
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
    identifier = str(uuid.uuid4())
    logging.info('http trigger function processed request.')
    logging.info('uuid: ' +  identifier)
    appname = req.params.get('appname')
    data = req.get_json ()
    
    if not appname:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            appname = req_body.get('appname')

    if appname and data:
        totpclear = data['data']
        parser = urlparse.urlparse(totpclear)
        secret = parse_qs(parser.query)['secret'][0]
        issuer = parse_qs(parser.query)['issuer'][0]
        kv.set_secret(identifier, secret)
        table = Entity()
        table.PartitionKey = 'mfaseed'
        table.AccountName = issuer
        table.RowKey = identifier
        table.CustomName = appname
        tables.insert_entity('mfaforall', table)
        data = {}
        data['meta'] = 'success'
        data['action'] = 'add'
        data['name'] = issuer
        data['uuid'] = identifier
        json_data = json.dumps(data)
        return func.HttpResponse(json_data)
    else:
        return func.HttpResponse(
             "invalid request\n",
             status_code=400
        )
