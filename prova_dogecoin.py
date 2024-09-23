import urllib.request, json
from datetime import datetime
import pandas as pd

def extract_data(ip):
    URL = 'http://192.168.10.' + str(ip) + '/mcb/cgminer?cgminercmd=devs'

    with urllib.request.urlopen(URL) as url:
        data = json.load(url)

    data = pd.DataFrame(data["data"])
    fanspeed_string = data["fanspeed"][0]
    fanspeed_array = fanspeed_string.split('/')
    fanspeed_now_string = fanspeed_array[0]
    fanspeed_now = float(fanspeed_now_string.replace('rpm', ''))
    fanspeed_lim_string = fanspeed_array[1]
    fanspeed_lim = float(fanspeed_lim_string.replace('rpm', ''))
    temp_value = float(data["temp"][0].replace('°C', ''))

    hr = data["hashrate"][0]

    df = {
        "timestamp": datetime.now(),
        "hashrate": hr,
        "powerplan": data["powerplan"][0],
        "fanspeed": fanspeed_now,
        "fanspeed_limit": fanspeed_lim,
        "hw_error_ratio": data["hwerr_ration"][0],
        "Temp": temp_value
    }

    df = pd.DataFrame(df, index=[0])

    return df


def read_DC(cursor, conn):

    ips = [218, 219]

    for ip in ips:
        print("Processing " + str(ip))
        df = extract_data(ip)

        date = datetime.strftime(df["timestamp"][0], "%Y-%m-%d %H:%M:%S")
        insert_string = f"INSERT INTO {ip} (time_stamp, hashrate, powerplan, fanspeed, fanspeed_limit, hw_error_ratio, Temp) VALUES ('{date}', {df['hashrate'][0]}, {df['powerplan'][0]},{df['fanspeed'][0]},{df['fanspeed_limit'][0]},{df['hw_error_ratio'][0]},{df['Temp'][0]});"
        cursor.execute(insert_string)
        conn.commit()

