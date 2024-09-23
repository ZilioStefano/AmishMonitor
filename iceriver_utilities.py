from datetime import datetime
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import pandas as pd


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
        fiveminshashrate_value = soup.find('span', class_='nowspeedcss').get_text(strip=True) if (
            soup.find('span', class_='nowspeedcss')) else "Non trouvé"

        # tabella POOL
        POOL_TAB = soup.find('table', class_='table table-hover boardcss')
        Soap = BeautifulSoup(str(POOL_TAB), 'html.parser')
        Temp_table = Soap.find('tbody').find_all('td')
        Temp_table_1 = Temp_table[2]
        T1_str = Temp_table_1.contents[0]
        T1 = float(T1_str[0:-2])
        Temp_table_2 = Temp_table[3]
        T2_str = Temp_table_2.contents[0]
        T2 = float(T2_str[0:-2])

        # tabella Ventole
        FANS_TAB = soup.find('table', class_='table table-hover fancss')
        Soap = BeautifulSoup(str(FANS_TAB), 'html.parser')
        Fan_table = Soap.find('tbody').find_all('td')
        Fan_table_1 = Fan_table[1]
        Fan_1_str = Fan_table_1.contents[0]
        Fan_1 = float(Fan_1_str)
        Fan_table_2 = Fan_table[2]
        Fan_2_str = Fan_table_2.contents[0]
        Fan_2 = float(Fan_2_str)
        first_raw = {"timestamp": timestamp, "hashrate": fiveminshashrate_value, "T1": T1, "T2": T2, "Fan 1": Fan_1,
                     "Fan 2": Fan_2}
        df = pd.DataFrame(first_raw, index=[0])

    except Exception as e:
        print(f"Error during connection at {ip}: {e}")
        # return [ip, 'Erreur', 'No Network', 'Unknown', 'Unknown', '0 GH/s', '0 GH/s', '0d 0h 0m 0s']

    finally:
        driver.quit()

    return df


def read_IR(cursor, conn):
    username = "admin"
    password = "12345678"

    ip_last_values = ['222', '223', '224', '227', '228']
    base_ip = "192.168.10"

    for ip in ip_last_values:

        try:
            curr_ip = base_ip + "." + ip
            print("Processing Ice River @ "+curr_ip)
            df = extract_data(curr_ip, username, password)

            date = datetime.strftime(df["timestamp"][0], "%Y-%m-%d %H:%M:%S")
            insert_string = (f"INSERT INTO {ip} (time_stamp, hashrate, T1, T2, Fan_1, Fan_2) VALUES ('{date}',"
                             f"{df['hashrate'][0]}, {df['T1'][0]},{df['T2'][0]},{df['Fan 1'][0]},{df['Fan 2'][0]});")
            cursor.execute(insert_string)
            conn.commit()
            print(curr_ip + " processed correctly")
        except Exception as err:
            print(err)
