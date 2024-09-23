import urllib.request, json

URL = 'http://192.168.10.227/44111'


for i in range(5000, 10000):
    URL = 'http://192.168.10.227/'+str(i)

    try:

        with urllib.request.urlopen(URL) as url:
            data = json.load(url)
            print(data)

    except:
        print("Prova "+str(i)+" fallita!")




