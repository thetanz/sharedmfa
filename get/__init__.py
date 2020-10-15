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

    uuid = req.params.get('uuid')
    
    if not uuid:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            uuid = req_body.get('uuid')

    if uuid:
        otpauthkv = kv.get_secret(uuid)
        totpseed = otpauthkv.value
        otpgen = pyotp.TOTP(totpseed)
        totp = otpgen.now()
        seconds_left = otpgen.interval - datetime.datetime.now().timestamp() % otpgen.interval
        miliseconds_left = seconds_left * 1000
        
        data = {}
        data['otp'] = totp
        data['expires'] = miliseconds_left
        json_data = json.dumps(data)
        
        return func.HttpResponse(json_data)

    else:
        return func.HttpResponse(
             "no uuid recieved.",
             status_code=400
        )
