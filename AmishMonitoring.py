import time
import pyodbc
from dogecoin_utilities import read_DC
from iceriver_utilities import read_IR


def read_data(cnxn, cursor):
    read_DC(cursor, cnxn)
    read_IR(cursor, cnxn)


if __name__ == "__main__":
    # conn = pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\Sviluppo_Software_ZG
    # \Desktop\AmishMonitor\MiningData.accdb;")
    conn = pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\Stefano Trevisan\Desktop"
                          r"\2. Progetti da continuare\139. Prova lettura dati IP\AMISH\Amish Monitor"
                          r"\MiningData.accdb;")

    cur = conn.cursor()

    dt = 5*60

    while True:
        try:
            read_data(conn, cur)
            # conn.close()
        except Exception as err:
            print(err)

        time.sleep(dt)
