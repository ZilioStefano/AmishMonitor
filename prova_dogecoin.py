import urllib.request, json

URL = 'http://192.168.10.218/mcb/cgminer?cgminercmd=devs'


with urllib.request.urlopen(URL) as url:
    data = json.load(url)
    print(data)




