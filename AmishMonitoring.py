import time
import pyodbc
from dogecoin_utilities import read_DC
from iceriver_utilities import read_IR
import pandas as pd
from ftplib import FTP
from datetime import datetime, timedelta


def read_data(cnxn, cursor):
    read_DC(cursor, cnxn)
    read_IR(cursor, cnxn)


def process_last_24(ips, ftp):

    for ip in ips:
        Now = datetime.now()
        Yesterday = Now - timedelta(days=1)

        tab = f"SELECT * FROM {ip}"
        table = pd.read_sql(tab, conn)
        table = table.sort_values(by="time_stamp")

        last_hr = table["hashrate"].iloc[-1]
        last_timestamp = table["time_stamp"].iloc[-1]

        if ip < 220:
            last_T = table["Temp"].iloc[-1]
        else:
            last_T = table["T1"].iloc[-1]

        if last_timestamp < Yesterday:
            last_hr = 0

        df = pd.DataFrame({
            "timestamp": last_timestamp,
            "hr": last_hr,
            "T": last_T
        }, index=[0])

        ftp.cwd('/' + str(ip))
        df.to_csv("last_vals.csv", index=False)
        file_name = "last_vals.csv"
        file = open(file_name, "rb")
        ftp.storbinary(f"STOR " + file_name, file)

        df_last24 = table[table["time_stamp"] >= Yesterday]
        df_last24.to_csv("last_24_hr.csv", index=False)
        file_name = "last_24_hr.csv"
        file = open(file_name, "rb")
        ftp.storbinary(f"STOR " + file_name, file)


def process_daily_mean(ips, ftp, cursor):
    media_string = "_media_giornaliera"
    for ip in ips:
        print(ip)
        if ip == 228:
            A = 2

        tab = f"SELECT * FROM {ip}{media_string}"
        table = pd.read_sql(tab, conn)
        last_data_day = table["time_stamp"].iloc[-1]
        tab = f"SELECT * FROM {ip}"
        table_all = pd.read_sql(tab, conn)

        # calcolo la media di oggi
        # aggiungo al database se è la prima che calcolo
        # aggiorno il valore se c'è già presente un valore

        now = datetime.now()
        starting_day = datetime(now.year, now.month, now.day)

        today_table = table_all[table_all["time_stamp"]>=starting_day]
        today_table['hashrate'] = today_table['hashrate'].str.replace(",",".").astype(float)

        means = today_table.mean()
        means.fillna("NULL")

        if last_data_day < starting_day:
            # aggiungo il nuovo score
            if ip > 220:
                insert_string = (f"INSERT INTO {ip}{media_string} (time_stamp, hashrate, T1, T2, Fan_1, Fan_2) VALUES ('{starting_day}',"
                                 f"{means['hashrate']},{means['T1']},{means['T2']},{means['Fan_1']},{means['Fan_2']});")

            else:
                insert_string = (
                    f"INSERT INTO {ip}{media_string} (time_stamp, hashrate, Temp, powerplan, fanspeed, hw_error_ratio)"
                    f" VALUES ('{starting_day}', '{means['hashrate']}', '{means['Temp']}','{means['powerplan']}','{means['fanspeed']}',"
                    f"'{means['hw_error_ratio']}');")

        else:
            last_id = table["ID"].iloc[-1]

            if ip > 220:
                insert_string = (f"UPDATE {ip}{media_string} SET hashrate = '{float(means["hashrate"].replace(",","."))}', T1 = '{means["T1"]}', T2 = '{means["T2"]}', Fan_1 = '{means["Fan_1"]}', Fan_2 = '{means["Fan_2"]}'  WHERE ID={str(last_id)};"
                )
            else:
                insert_string = (
                    f"UPDATE {ip}{media_string} SET hashrate = '{means["hashrate"]}', Temp = '{means["Temp"]}',"
                    f"powerplan = '{means["powerplan"]}', fanspeed = '{means["fanspeed"]}', hw_error_ratio = '{means["hw_error_ratio"]}'"
                    f" WHERE ID={str(last_id)};"
                )

        cursor.execute(insert_string)
        conn.commit()
            # modifico il precedente
            # estraendo l'identificativo della riga


            # modificando con UPDATE

        Now = datetime.now()
        ftp.cwd('/' + str(ip))

        tab = f"SELECT * FROM {ip}{media_string}"
        table = pd.read_sql(tab, conn)
        table.to_csv("daily_means.csv", index=False)
        file_name = "daily_means.csv"
        file = open(file_name, "rb")
        ftp.storbinary(f"STOR " + file_name, file)


def process_data(conn, cursor):

    ips = [218, 219, 222, 223, 224, 227, 228]
    ftp = FTP("192.168.10.229", timeout=60)
    ftp.login('user', '1234')

    process_last_24(ips, ftp)
    process_daily_mean(ips, ftp, cursor)
    ftp.close()


if __name__ == "__main__":
    # conn = pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\Sviluppo_Software_ZG"
    #                       r"\Desktop\AmishMonitor2\MiningData.accdb;")
    conn = pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\Stefano Trevisan\Desktop"
                          r"\2. Progetti da continuare\139. Prova lettura dati IP\AMISH\Amish Monitor"
                          r"\MiningData.accdb;")

    cur = conn.cursor()

    dt = 5*60

    while True:
        try:
            read_data(conn, cur)
            process_data(conn, cur)
            # send_data(data)
            # conn.close()
        except Exception as err:
            print(err)

        time.sleep(dt)
