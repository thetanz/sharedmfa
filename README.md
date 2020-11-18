![Deploy to Azure Function on Linux App Service](https://github.com/thetanz/sharedmfa/workflows/Deploy%20to%20Azure%20Function%20on%20Linux%20App%20Service/badge.svg)

<a href="https://www.theta.co.nz/solutions/cyber-security/">
<img src="https://avatars0.githubusercontent.com/u/2897191?s=70&v=4" 
title="Theta Cybersecurity" alt="Theta Cybersecurity">
</a>

<!-- Shared MFA at Theta -->
<!-- josh.highet@theta.co.nz -->
<!-- test/development -->

***Shared TOTP Facilitation for MFA on Shared Accounts***

---

Multi Factor Authentication is a tremendous way to defend an account from takeover due to credential compromise or simple credential brute-forcing.

We've all hopefully become accustomed to using MFA on the occasional personal account, but using MFA on shared accounts and enterprise services is often left behind due to complications around how to share and maintain shared devices to allow for this to be possible.

This project aims to remove these pains by providing a secure, serverless, shared MFA implementation using Python Azure Functions, Azure API Management and Azure Keyvault.

The Python Function will expose 3 endpoints, `/get`, `/add` & `/list`. Each REST endpoint is described below.

## MFA - `Add` Endpoint
This endpoint takes a RFC spec OTP QR data field. Upon recieving input, a UUID is created which is used to reference the object for all future actions. The UUID is used to reference the QR secret value which is placed into Azure Keyvault

An example POST request to this endpoint is avalable below. A URL paraamater and JSON body is required.

## MFA - `List` Endpoint
This endpoint will produce a JSON respoinse to authiorised requrests with a list of UUID's and Application Names to be references by subsequent requests to the Get endpoint.

## MFA - `Get` Endpoint
This endpoint is used to retrieve a code for a given applciation name. A URL paramater of the App Name is required.


## Examples

[Python OTP Module](https://pyotp.readthedocs.io/en/latest/#)

    curl 'https://api.thetasystems.co.nz/mfa/list' \
    --header "cyberkey: XXXX" | jq

    curl 'https://api.thetasystems.co.nz/mfa/get?uuid=XXX' \
    --header "cyberkey: XXXX" | jq

    curl 'https://api.thetasystems.co.nz/mfa/add?appname=XXXX' \
    --data '{ "data": "otpauth://XXXX" }' \
    --header "cyberkey: XXXX" | jq

---

# Local Runtime & Debugging

To run this project localls, `Azure Functions Core Tools` needs to be installed

[Azure Functions Core Tools Download](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=macos%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)

**Clone this repository and enter the directory**

*Run the following command to populate Application Settings*

> This will create a local.settings.json file within the working directory.

> This encrypted file will allow for authentication to services required to make relenvant REST calls.

    func azure functionapp fetch-app-settings fn-ae-prod-mfaforall

**The following command will initiate the function**

    func start --verbose

**To push this to the App Service outside of the build pipeline**
    
    func azure functionapp publish fn-ae-prod-mfaforall --build-native-deps

---
- 2020 <a href="https://www.theta.co.nz" target="_blank">Theta</a>.
