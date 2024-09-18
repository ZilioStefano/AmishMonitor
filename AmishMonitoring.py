import time
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pyodbc


def extract_data(ip, username, password):
    url = f"http://{ip}/user/login"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        username_field = driver.find_element(By.NAME, "user")
        password_field = driver.find_element(By.NAME, "pwd")
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button = driver.find_element(By.CLASS_NAME, "loginBtn")
        login_button.click()
        time.sleep(3)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        timestamp = soup.find('span', class_='algocss3').get_text()
        timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        fiveminshashrate = soup.find('span', class_='content2radiuscss content2radiusGreencss speedcss').get_text(
            strip=True) if soup.find('span',
                                     class_='content2radiuscss content2radiusGreencss speedcss') else "Non trouvé"
        networkstatus = soup.find('span', class_='content2radiuscss content2radiusGreencss netstatuscss').get_text(
            strip=True) if soup.find('span',
                                     class_='content2radiuscss content2radiusGreencss netstatuscss') else "Non trouvé"
        fanspeed = soup.find('span', class_='content2radiuscss content2radiusGreencss volcss').get_text(
            strip=True) if soup.find('span', class_='content2radiuscss content2radiusGreencss volcss') else "Non trouvé"
        minertemperature = soup.find('span', class_='content2radiuscss content2radiusGreencss temcss').get_text(
            strip=True) if soup.find('span', class_='content2radiuscss content2radiusGreencss temcss') else "Non trouvé"
        fiveminshashrate_value = soup.find('span', class_='nowspeedcss').get_text(strip=True) if soup.find('span',
                                                                                                           class_='nowspeedcss') else "Non trouvé"
        thirtyminshashrate_value = soup.find('span', class_='svgspeedcss').get_text(strip=True) if soup.find('span',
                                                                                                             class_='svgspeedcss') else "Non trouvé"

        #test

        # tabella POOL
        POOL_TAB = soup.find('table', class_='table table-hover boardcss')
        Soap = BeautifulSoup(str(POOL_TAB))
        Temp_table = Soap.find('tbody').find_all('td')
        Temp_table_1 = Temp_table[2]
        T1_str = Temp_table_1.contents[0]
        T1 = float(T1_str[0:-2])
        Temp_table_2 = Temp_table[3]
        T2_str = Temp_table_2.contents[0]
        T2 = float(T2_str[0:-2])

        # tabella Ventole
        FANS_TAB = soup.find('table', class_='table table-hover fancss')
        Soap = BeautifulSoup(str(FANS_TAB))
        Fan_table = Soap.find('tbody').find_all('td')
        Fan_table_1 = Fan_table[1]
        Fan_1_str = Fan_table_1.contents[0]
        Fan_1 = float(Fan_1_str)
        Fan_table_2 = Fan_table[2]
        Fan_2_str = Fan_table_2.contents[0]
        Fan_2 = float(Fan_2_str)


    except Exception as e:
        print(f"Erreur lors de la connexion au mineur {ip}: {e}")
        disconnected_colored = colorize("Disconnected", False)  # False pour coloriser en rouge
        return [ip, 'Erreur', 'No Network', 'Unknown', 'Unknown', '0 GH/s', '0 GH/s', '0d 0h 0m 0s',
                disconnected_colored]

    finally:
        driver.quit()

    first_raw = {"timestamp": timestamp, "hashrate": fiveminshashrate_value, "T1":T1, "T2":T2, "Fan 1": Fan_1, "Fan 2": Fan_2}
    df = pd.DataFrame(first_raw,index=[0])

    return df


def read_data(conn, cursor):

    username = "admin"
    password = "12345678"

    ip_last_values = ['222', '223', '224', '227', '228']
    base_ip = "192.168.10"

    for ip in ip_last_values:
        curr_ip = base_ip + "." + ip
        print("Processing "+curr_ip)
        df = extract_data(curr_ip, username, password)

        date = datetime.strftime(df["timestamp"][0], "%Y-%m-%d %H:%M:%S")
        insert_string = f"INSERT INTO {ip} (time_stamp, hashrate, T1, T2, Fan_1, Fan_2) VALUES ('{date}', {df['hashrate'][0]}, {df['T1'][0]},{df['T2'][0]},{df['Fan 1'][0]},{df['Fan 2'][0]});"
        cursor.execute(insert_string)
        conn.commit()


if __name__=="__main__":

    conn = pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
                          r"DBQ=C:\Users\Stefano Trevisan\Desktop\2. Progetti da continuare\139. Prova lettura dati IP\AMISH\Amish Monitor\MiningData.accdb;")
    cur = conn.cursor()

    dt = 5*60

    while True:
        read_data(conn, cur)
        time.sleep(dt)

