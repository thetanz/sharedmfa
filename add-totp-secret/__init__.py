#!/usr/bin/env python3
'''handle addition of new totp strings'''

import os
import json
import logging
import urllib.parse as urlparse
from urllib.parse import parse_qs
import uuid
import azure.functions as func
import pyotp
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

#fetch keyvault name from environment variable (function configuration setting)
kvname = os.environ["KEY_VAULT_NAME"]
kvfqdn = f"https://{kvname}.vault.azure.net"

#using managed identities, authenticate to azure keyvault and define as kv
kv = SecretClient(vault_url=kvfqdn, credential=DefaultAzureCredential())

#using the AzWebJobs environment variable, connect to azure table storage
stor_acc_conn_string = os.environ['AzureWebJobsStorage']
tables = TableService(connection_string=stor_acc_conn_string)

def main(req: func.HttpRequest) -> func.HttpResponse:
    """primary function to handle incoming request, processing and response"""
    #generate a random uuid upon a new inbound request
    identifier = str(uuid.uuid4())
    #process url query paramaater and json body
    appname = req.params.get('appname')
    data = req.get_json()
    if not appname:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            appname = req_body.get('appname')
    #if url query & json body are present, proceed
    if appname and data:
        totpclear = data['data']
        #use urlparse to read the QR data (url field otpauth://)
        parser = urlparse.urlparse(totpclear)
        secret = parse_qs(parser.query)['secret'][0]
        issuer = parse_qs(parser.query)['issuer'][0]
        #add the secret to keyvault, referenced by the uuid
        kv.set_secret(identifier, secret)
        #create a table entity and dict of items
        table = Entity()
        table.PartitionKey = 'mfaseed'
        table.AccountName = issuer
        table.RowKey = identifier
        table.CustomName = appname
        #insert dict into azure table
        tables.insert_entity('apps', table)
        #form json response
        data = {}
        data['name'] = issuer
        data['uuid'] = identifier
        #create json object from dictionary, return request
        json_data = json.dumps(data)
        return func.HttpResponse(json_data)
    else:
        return func.HttpResponse(
            "invalid request\n",
            status_code=400
        )
