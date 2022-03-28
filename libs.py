import json
import sys
import os
import time
import random
import math
from shlex import quote
from datetime import datetime, timedelta


def log(message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f'{timestamp} {message}')

def auth(username, password):
    payload = { "username": username, "password": password }
    payload_json = quote(json.dumps(payload))
    command = f"echo {payload_json} | \
        http POST https://chudjenbet.com/auth/login \
        cache-control:no-cache \
        content-type:application/json \
        postman-token:5953a0a8-e6c9-69d3-998d-588e5b97c2be"

    stream = os.popen(command)
    output = stream.read()
    rs = json.loads(output)
    return rs

def read_jsonfile(path):
    with open(path) as json_file:
        return json.load(json_file)

def write_jsonfile(path, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile)

def get_speedvip_stakes(token):
    command = f"http GET https://chudjenbet.com/api/game/lotto/speed_vip? \
  authorization:'Bearer {token}' \
  cache-control:no-cache" 

    stream = os.popen(command)
    output = stream.read()
    return json.loads(output)

def get_lotto_item(id, lotto):
    for key in lotto:
        if int(key) == int(id):
            return lotto[key]
    return None

def check_twotop(two_top, attribute):
    for attr in attribute:
        if attr['number'] == two_top:
            return True
    return False

def check_stake_win(speedvip_data):
    stakes = speedvip_data['stake']
    lotto = speedvip_data['lotto']
    is_win = False

    for stake in stakes:
        lotto_id = stake["lotto_id"]
        lotto_item = get_lotto_item(lotto_id, lotto)

        if lotto_item is not None and lotto_item['status'] == 'PAYOUT_COMPLETED':
            attribute = stake["attribute"]
            two_top = lotto_item['result']['two_top']
            is_win = check_twotop(two_top, attribute)
            log(f'[stake]: {stake["id"]} - {lotto_id}, {lotto_item["title"]}')
            return is_win

    return is_win

def logout(token):
    command = f"http GET https://chudjenbet.com/auth/logout \
  authorization:'Bearer {token}' \
  cache-control:no-cache" 

    stream = os.popen(command)
    output = stream.read()
    return json.loads(output)

def mee(token):
    command = f"http GET https://chudjenbet.com/auth/me \
  authorization:'Bearer {token}' \
  cache-control:no-cache" 

    stream = os.popen(command)
    output = stream.read()
    # print(f'output: {output}')
    #if 'E_JWT_TOKEN_EXPIRED' in output:
    #    raise Exception("Please login again!")
    return output

def refreshauth(username, password, token):
    c = 0
    while c <= 3:
        try:
            output = mee(token)
            log(f'[refreshauth]: {output}')
            if 'error' not in output:
                return read_jsonfile('user.json')
            return auth(username, password)

        except Exception as ex:
            c = c + 1
            print(ex)
            time.sleep(25)

    raise Exception('LOGIN TIMEOUT!!!')

def get_speedvip(token):
    command = f"http GET https://chudjenbet.com/api/member/lotto \
    authorization:'Bearer {token}' \
    cache-control:no-cache"
    
    stream = os.popen(command)
    output = stream.read()
    data = json.loads(output)
    records = data['records']
    speedvip = list(filter(lambda x: x['type'] == 'speed_vip' and x['is_finished'] == 0, records))
    return speedvip

if __name__ == "__main__":
    username = "minimal_mons"
    password = "Secret1234"
    #user = refreshauth(username, password)
    #print(user['data']['token'])
    #token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjIyMTg2ODUsImRhdGEiOnt9LCJpYXQiOjE2NDc4ODk4NjIsImV4cCI6MTY0Nzk3NjI2Mn0.12k3Wo61kxPnRIhHEFllbKIZUY7EAu-Nz6G1FY8V0p0'
    #recs = get_speedvip(token)
    #print(recs[1])
    #print(len(recs))
    #print(load_payload('payload.json'))
    #write_jsonfile('me.json', { "OK": 22 })
    user = read_jsonfile('user.json')
    print(user, type(user))

    token = user['data']['token']
    stakes = get_speedvip_stakes(token)
    is_win = check_stake_win(stakes)
    log(is_win)

