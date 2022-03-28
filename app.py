import json
import sys
import os
import time
import random
import math
import hashlib
from shlex import quote
from datetime import datetime, timedelta

from sqlalchemy import create_engine, delete, text
from sqlalchemy.orm import Session, sessionmaker
from model import Base, Result
from put_tripple import log
from libs import refreshauth, get_speedvip, logout, check_stake_win, get_speedvip_stakes

DATABASE_URL="mysql://doadmin:xh37lahz4lkkbm1y@db-mysql-sgp1-85509-do-user-4098479-0.db.ondigitalocean.com:25060/chudjenbet?"

engine = create_engine(DATABASE_URL, echo=False)
Base.prepare(engine, reflect=True)
DBSession = sessionmaker(bind=engine)
session = DBSession()

STAKE=5
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjIyMTg2ODUsImRhdGEiOnt9LCJpYXQiOjE2NDc2ODY1NTgsImV4cCI6MTY0Nzc3Mjk1OH0.bRyK4eV0v6T36hB1PYjlvu1A7Xs1FcHvHTByjzhHnWo'

#TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjExMzg3MDMsImRhdGEiOnt9LCJpYXQiOjE2NDc1MzM4NDUsImV4cCI6MTY0NzYyMDI0NX0.uEZXhRlDCNgEZI721IP-xScLdCvIiYXKYPJSXYkmnoE'


def me(token):
    command = f"http GET https://chudjenbet.com/auth/me \
  authorization:'Bearer {token}' \
  cache-control:no-cache" 

    stream = os.popen(command)
    output = stream.read()
    # print(f'output: {output}')
    if 'E_JWT_TOKEN_EXPIRED' in output or 'error' in output:
        raise Exception("Please login again!")
    rs = json.loads(output)
    #log(f'[me]: {rs}')
    return rs

def get_result_date(my_date):
    valid_date = datetime.fromisoformat(f'{my_date.year}-{my_date.month:02}-{my_date.day:02}T06:00:00')

    if my_date < valid_date:
        return (my_date - timedelta(days=1)).strftime('%Y-%m-%d')
    return my_date.strftime('%Y-%m-%d')

def get_result():
    today = datetime.fromisoformat(get_result_date(datetime.now()))
    end_day = today.day
    sql = text("""select t.two_top from (
        select id, date, close_time,three_top, two_top, two_under, category
        FROM chudjenbet.Result where extract(year from date) = :year and extract(month from date) = :month
        and extract(day from date) between :end_day and :end_day
        and category = 'speed_vip' and three_top is not null
        order by id desc) as t
        """)

    rs = session.execute(sql, {'year': today.year, 'month': today.month, 'end_day': end_day})
    data = []
    for row in rs:
        data.append(row[0])
    
    rs.close()
    ret = list(dict.fromkeys(data))
    #log(f'[sql]: {sql}')
    log(f'[db]: {ret}')
    data.clear()
    session.commit()

    return ret

def build_stakes(bet_result):
    rs = []
    for two_top in bet_result:
        rs.append({
            "slug": "two_top",
            "number": two_top,
            "price": STAKE,
            "rate": "92"})
    return rs

def build_setAB(setA, setB):
    ret = []
    for a in setA:
        for b in setB:
            ret.append(f'{a}{b}')

    for b in setB:
        for a in setA:
            ret.append(f'{b}{a}')

    return ret

def read_payload(path):
    with open(path) as json_file:
        data = json.load(json_file)
        return data

def test_quote_command(seq, payload, token):
    payload_json = quote(json.dumps(payload))
    
    # print(f"PAYLOAD: {payload_json}")
    command = f"echo {payload_json} | \
        http POST https://chudjenbet.com/api/game/lotto/speed_vip\
        authorization:'Bearer {token}' \
        cache-control:no-cache \
        content-type:application/json"

    print(f"{command}")
    print(f"{seq}")
    #stream = os.popen(command)
    #output = stream.read()
    #print(output)

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
    return output

def build_payload(seq, hashed, stakes):
    user = get_user()
    username = user['username']
    text = str(f'{username}{seq}').encode()
    hh = hashlib.md5(text).hexdigest()
    log(f'[hashed]: {hh}')
    payload = {
        "lotto_id": seq,
        "hashed": hh if hashed is None else hased,
        "stakes": stakes }
    return payload

def limit_stakes(offset, stakes):
    size = len(stakes)
    rs = []
    count = 1
    for stake in stakes:
        
        if count > offset and len(rs) <= 70:
            rs.append(stake)
        if len(rs) >= 70:
            break
        count = count +1
        
    print(f"Size: {size}, {len(rs)}")
    return rs 

def main(seq, payload):
    itme = me(TOKEN)

    timestamp = datetime.now().strftime('%H:%M:%S')
    real_credit = int(itme['data']['real_credit'])
    print(f'{timestamp} credit: {real_credit}')
    if real_credit < 140:
        raise Exception("Your credit is not enough!")

    payload['lotto_id'] = seq
    return put_slip(seq, payload, TOKEN)

def random_70():
    data = []
    stake = []
    for i in range(10):
        for j in range(10):
            data.append(f'{i}{j}')

    while len(stake) < 70:
        n = random.randint(0, 99)
        stake.append(data[n])
        stake = list(dict.fromkeys(stake))

    return stake

def read_jsonfile(path):
    with open(path) as json_file:
        return json.load(json_file)

def write_jsonfile(data, path):
    with open(path ,'w') as json_file:
        json.dump(data, json_file)

def pick_nums7(data):
    nums7 = []
    for n in data:
        n = list(n)
        for d in n:
            if d not in nums7:
                nums7.append(d)
        if len(nums7) == 7:
            break
    return nums7

def check_win(mybalance):
    itme = me(TOKEN)
    real_credit = int(itme['data']['real_credit'])
    #print(f'mybalance: {mybalance}, {real_credit}')
    
    return mybalance <= real_credit

def pick_nums8(data, mode):
    #data = list(set(data)) if toggle else data
    if mode == 'SET':
        log(f'[CURRENT MODE]: {mode}')
        data = list(set(data)) 
    else:
        log(f'[CURRENT MODE]: {mode}')
    nums = []
    count = 0
    idx = 0
    log(f'[randint]: {idx}, {mode}')
    data = list(filter(lambda x: len(set(x)) > 1, data))
    for n in data:
        n = list(n)
        if count >= idx:
            for d in n:
                if d not in nums and len(nums) < 8:
                    nums.append(d)

        count = count + 1
    return nums[:8:]

def build_serieswith10(nums):
    series = []
    for i in nums:
        for j in range(10):
            series.append(f'{i}{j}')

    return series

def get_real_credit():
    return int(me(TOKEN)['data']['real_credit'])

def build_series(nums):
    series = []
    for i in nums:
        for j in nums:
            series.append(f'{i}{j}')

    return series

def get_seq(token):
    recs = get_speedvip(TOKEN)
    rec = recs[0]
    seq = rec['id']
    return seq

def get_betconfig():
    return read_jsonfile('betconfig.json')

def get_user():
    return read_jsonfile('me.json')

def is_2ls(acc):
    c = 0
    for i,a in enumerate(acc):
        if i < len(acc) +1:
            for b in acc[i+1::]:
                if a == 'lose' and b == 'lose':
                    return True

    return False

if __name__ == "__main__":
    offset = 10

    user_json = get_user()
    username = user_json['username']
    password = user_json['password']
    
    auth_data = read_payload('user.json')
    TOKEN = auth_data['data']['token']

    user = refreshauth(username, password, TOKEN)
    TOKEN = user['data']['token']

    write_jsonfile(user, 'user.json')

    betconfig = get_betconfig()
    log(f'[TOKEN]: {TOKEN}')
    log(f'[CONFIG]: {betconfig}')

    ok = True
    is_10 = False
    STAKE=betconfig['STAKE']
    mycredit = get_real_credit() 

    c=0
    n=6
    cc = 0
    ls = 0
    test = False
    is_restart = True
    counter = 0
    w_counter = 0
    w_n = 0
    app_sleep = False
    app_logout = False
    acc = []
    mode = 'LIST'
    #mode = 'SET'

    while 1:
        m = datetime.now().minute
        h = datetime.now().hour

        m_c = int(datetime.now().strftime('%Y%m%d%H%M'))
        #m_start = int(datetime.now().strftime('%Y%m%d%0300'))
        #m_end = int(datetime.now().strftime('%Y%m%d%0610'))
        m_start = int(datetime.now().strftime('%Y%m%d') + '0350')
        m_end = int(datetime.now().strftime('%Y%m%d') + '0720')

        #log(f'{m_start}, {m_end}, {m_c}')
        if m_c >= m_start and m_c <= m_end:
            if not app_sleep:
                print('Relaxing ...')
                app_sleep = True
            continue
            
        app_sleep = False
        try:
            m_sleep = random.choice([55, 25])
            
            """
            if h%2 == 0 and m == m_sleep:
                log(f'[logout]: waiting for 25 sec')
                logout(TOKEN)
                time.sleep(20)

                user = refreshauth(username, password, TOKEN)
                TOKEN = user['data']['token']
                write_jsonfile(user, 'user.json')
                is_restart = True
                w_counter = 0
                w_n = 0
                counter = 0
                continue

            """
            c_2s = is_2ls(acc)
            
            """
            if h%2 == 0 and not app_sleep:
                log(f'[logout]: waiting for a minute; {c_2s}, {counter}')
                time.sleep(60)
                counter = 0
                w_counter = 0
                w_n = 0
                is_restart = True
                app_sleep = True 
                acc.clear()
                continue
            """

            if test or (m%5 == 3 and ok):
                log(f'[sleep]: waiting for 10 secs')
                time.sleep(10)

                log(f"{m}")
                ok = False
                bet_result = get_result()

                speedvip_records = get_speedvip_stakes(TOKEN)
                #if check_stake_win(speedvip_records):
                log(f'[credit]: {mycredit}, {get_real_credit()}')
                if mycredit <= get_real_credit():
                    c = c
                    acc.append('won')
                else:
                    acc.append('lose')
                    log(f'[LOSE]: {acc},{c} -> {mycredit}, {get_real_credit()}')

                if c_2s: 
                    #log(f'[ACC]: {acc}, {c_2s}')
                    log(f'[BF]: {mode}')
                    mode = 'SET' if mode == 'LIST' else 'LIST'
                    acc.clear()

                nums7 = pick_nums8(bet_result, mode)
                series = []
                
                if is_10:
                    series = build_serieswith10(nums7)
                else:
                    series = build_series(nums7)

                m_counter = list(filter(lambda x: x == 'lose', acc[-2::]))
                if len(m_counter) == 1:
                    two_digit = list(set(nums10) - set(nums7))
                    series = build_setAB(two_digit, nums7)
                    log(f'[TRY]: {series}')

                my_stakes = build_stakes(series)
                nums10 = ['0','1', '2', '3', '4','5', '6', '7', '8', '9']

                log(f'[ACC]: {acc}, {c_2s}, {m_counter}, {mode}')
                log(f'[nums8]: {nums7}')
                log(f'[nums8 - sorted]: {sorted(nums7)}')
                log(f'[nums8]: {set(nums10) - set(nums7)}')

                seq = get_seq(TOKEN)
                log(f'[seq]: {seq}')
                plain_text = json.dumps(my_stakes)
                payload = build_payload(seq, None, plain_text)
                mycredit = get_real_credit()

                message = main(seq, payload)
                if 'lotto is timeout' in message:
                    continue

                is_restart = False

            if m%5 != 3:
                ok = True
        except Exception as ex:
            log(f'[error][main]: {str(ex)}')
            if 'login again' in str(ex):
                user = refreshauth(username, password, TOKEN)
                TOKEN = user['data']['token']
                write_jsonfile(user, 'user.json')
                mycredit = get_real_credit()
                log(f'[TOKEN]: {TOKEN}')
            else:
                quit()

    """
    while 1:
        bet_result = get_result()
        nums7 = pick_stg1(bet_result)
        print(nums7)
        time.sleep(20)
    """

    #print(bet_result)
