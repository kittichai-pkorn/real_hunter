import os
import sys
import json
import time
from shlex import quote
from datetime import datetime

def put_slip(seq, payload, token):
    payload_json = quote(json.dumps(payload))
    
    # print(f"PAYLOAD: {payload_json}")
    command = f"echo {payload_json} | \
        http POST https://chudjenbet.com/api/game/lotto/speed_vip\
        authorization:'Bearer {token}' \
        cache-control:no-cache \
        content-type:application/json \
        postman-token:62ebddd0-8916-27dd-5506-788f78631d11" 

    #print(f"{command}")
    #print(f"{seq}")
    stream = os.popen(command)
    output = stream.read()
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{timestamp} [{seq}]: {output}")
    #print(f"{timestamp} - slip: {seq}")

def log(message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{timestamp} {message}")

def me(token):
    command = f"http GET https://chudjenbet.com/auth/me \
  authorization:'Bearer {token}' \
  cache-control:no-cache" 

    stream = os.popen(command)
    output = stream.read()
    # print(f'output: {output}')
    if 'E_JWT_TOKEN_EXPIRED' in output:
        raise Exception("Please login again!")
    rs = json.loads(output)
    return rs

def read_jsonfile(path):
    with open(path) as json_file:
        return json.load(json_file)

if __name__ == "__main__":
   token = sys.argv[2]
   seq = int(sys.argv[1])
   print(token, seq)
   payload = read_jsonfile("payload_tripple.json")

   max_size = 8
   for i in range(1, max_size):
      itme = me(token)
      real_credit = itme["data"]["real_credit"]
      log(f"[credit]: {real_credit}")
      payload["lotto_id"] = seq
      put_slip(seq, payload, token)
      time.sleep(12)
      seq = seq + 1

