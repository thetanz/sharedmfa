#!/bin/bash
# theta.co.nz/cyber

set -e

if [[ -z "${9}" ]] ; then
    printf 'location:' && read LOCATION
    printf 'subscription name:' && read SUB_NAME
    printf 'resource group:' && read RESOURCE_GROUP
    printf 'function app name:' && read FN_APP_NAME
    printf 'storage account:' && read FN_STOR_ACC
else
    LOCATION="${1}"
    SUB_NAME="${4}"
    RESOURCE_GROUP="${5}"
    FN_APP_NAME="${7}"
    FN_STOR_ACC="${8}"
fi

TAG_OWNER=`az ad signed-in-user show --query mailNickname --output tsv`
TAG_PRACTICE=`az ad signed-in-user show --query department --output tsv`
STORAGE_ACCOUNT_ID=`az storage account show --name "${FN_STOR_ACC}" --query id --output tsv`

az functionapp create \
--functions-version 3 \
--consumption-plan-location ${LOCATION} \
--name "${FN_APP_NAME}" \
--os-type Linux \
--resource-group "${RESOURCE_GROUP}" \
--runtime python \
--runtime-version 3.7 \
--storage-account "${STORAGE_ACCOUNT_ID}" \
--tags \
Practice="${TAG_PRACTICE}" \
Owner="${TAG_OWNER}" \
| jq

az functionapp update \
--name "${FN_APP_NAME}" \
--resource-group "${RESOURCE_GROUP}" \
--set httpsOnly=true \
| jq

az webapp config set \
--name "${FN_APP_NAME}" \
--resource-group "${RESOURCE_GROUP}" \
--subscription "${SUB_NAME}" \
--ftps-state FtpsOnly \
| jq
