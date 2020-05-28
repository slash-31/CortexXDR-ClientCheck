#!/usr/bin/python3

# This script requires python3 (version 3.5 or later)
# Required muodules to install: python3 -m pip install requests termcolor
#  - Requests
#  - termcolor

import requests
import json
import argparse
import time
from datetime import datetime, date
from termcolor import colored

# All time objects must be converted to MSEC
time_outdated = ""
time_converted = ""
time_now = ""
time_outdated_range = ""
api_key = ""
api_key_id = ""
fqdn = ""


# Collect Argumenrts from CLI
def get_arguments():
    print(colored("Please type -h for help, need to add API Key (-a) API ID (-i) and FQDN (-f) to run this script", "red"))
    print(colored("Example: python3 test-pull-api.py -a [yourAPIKEYGOESHERE] -i [YOURID] -f [yoursite] -t [Minutes]", "green"))
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--api", dest="api_key", help="API Key")
    parser.add_argument("-i", "--apiID", dest="api_key_id", help="API ID for user account")
    parser.add_argument("-f", "--fqdn", dest="fqdn", help="API FQDN Address {do not enter api-; just enter site name}")
    parser.add_argument("-t", "--time", dest="time_outdated", help="Enter the amount of time in minutes for outdated clients")
    options = parser.parse_args()
    return options

def client_pull(api_key, api_key_id, fqdn, time_outdated):
    time_converted = int(time_outdated) * 60 * 1000 # converts time into milliseconds
    time_now = int(round(time.time() * 1000))
    time_outdated_range = time_now - time_converted
    
    headers = {
        "x-xdr-auth-id":str(api_key_id),
        "Authorization":api_key
    }
    parameters = {
        "request_data": {
            # If you want to filter based on one of the filtering fields, use this example
            # refer to https://docs.paloaltonetworks.com/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-apis/get-endpoints.html
            #"filters":[
            #    {
            #        "field":"group_name",
            #        "operator":"in",
            #        "value":["Windows Workstations"] 
            #    }
            #]
        }#
    }
    res = requests.post(url="https://api-" + fqdn + ".xdr.us.paloaltonetworks.com/public_api/v1/endpoints/get_endpoint", headers = headers, json = parameters)

    if res.status_code == 200:
            ep_count = 0
            ep_outdated_count = 0
            raw_json = json.loads(res.text)
            filter_json = raw_json['reply']
            filter_endpoints = filter_json['endpoints']
            for ep in filter_endpoints:
                #print(f"EndPoint {ep['endpoint_name']}")
                ep_count += 1
                if ep['last_seen'] < time_outdated_range:
                    ep_outdated_count += 1
                    print(f"Outdated Endpoint by {time_outdated} Minutes \t EndPoint Name: {ep['endpoint_name']} \t EndPoint IP: {ep['ip']} \t\t Last Seen: {datetime.fromtimestamp(ep['last_seen']/(1000)).strftime('%Y-%m-%d %H:%M:%S')}")
            print(colored(f"[**] EndPoint Count = {ep_count}", "green"))
            print(colored(f"[!!] Out Dated Endpoint Count = {ep_outdated_count}", "red"))
    if res.status_code == 400:
        print('Bad Request. Got an invalid JSON. Error Code: ' + str(res.status_code))
    if res.status_code == 401:
        print('Unauthorized access. An issue occurred during authentication. This can indicate an incorrect key, id, or other invalid authentication parameters. Error Code: ' + str(res.status_code))
    if res.status_code == 402:
        print('Unauthorized access. User does not have the required license type to run this API. Error Code: ' + str(res.status_code))
    if res.status_code == 403:
        print('Forbidden access. The provided API Key does not have the required RBAC permissions to run this API. Error Code: ' + str(res.status_code))
    if res.status_code == 500:
        print('Internal server error. A unified status for API communication type errors. Error Code: ' + str(res.status_code))
    return res

options = get_arguments()
client_pull(options.api_key, options.api_key_id, options.fqdn, options.time_outdated)