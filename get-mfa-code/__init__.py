#!/usr/bin/env python3
'''get secret from app guid located in keyvault, calculate totp & return'''
################################################################################
__status__ = "development"
__maintainer__ = "josh highet"
__email__ = "josh.highet@theta.co.nz"
################################################################################
import os
import json
import logging
import datetime
import urllib.parse as urlparse
from urllib.parse import parse_qs
import azure.functions as func
import pyotp
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
################################################################################
#fetch keyvault name from environment variable (function configuration setting)
kvname = os.environ["KEY_VAULT_NAME"]
kvfqdn = f"https://{kvname}.vault.azure.net"
#using managed identities, authenticate to azure keyvault and define as kv
kv = SecretClient(vault_url=kvfqdn, credential=DefaultAzureCredential())
################################################################################
#using the AzWebJobs environment variable, connect to azure table storage
stor_acc_conn_string = os.environ['AzureWebJobsStorage']
tables = TableService(connection_string=stor_acc_conn_string)
################################################################################
def main(req: func.HttpRequest) -> func.HttpResponse:
    """fetch uuid from inbound url query parameter"""
    uuid = req.params.get('uuid')
    if not uuid:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            uuid = req_body.get('uuid')
    #if the uuid has been identified
    if uuid:
        #get otp secret object from key vault by reference to uuid
        otpauthkv = kv.get_secret(uuid)
        #get otp secret value from object
        totpseed = otpauthkv.value
        #calculate pin from otp secret
        otpgen = pyotp.TOTP(totpseed)
        totp = otpgen.now()
        #calculate time-to-live of pin (30 second lifespan)
        seconds_left = otpgen.interval - datetime.datetime.now().timestamp() % otpgen.interval
        miliseconds_left = seconds_left * 1000
        #form json response and respond
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
