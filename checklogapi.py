from datetime import datetime
import requests
from pathlib import Path
import os

def write_log(datalog):
    waktulog = datetime.now()
    dirpathlog = f"LOG/API/{waktulog.strftime('%Y')}/{waktulog.strftime('%m')}"
    os.makedirs(dirpathlog, exist_ok=True)
    pathlog = f"{waktulog.strftime('%d%m%Y')}.log"
    file_path = Path(f"{dirpathlog}/{pathlog}")
    if not file_path.is_file():
        file_path.write_text(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}\n")
    else :
        fb = open(f"{dirpathlog}/{pathlog}", "a")
        fb.write(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}\n")
        fb.close
    
    print(f"{waktulog.strftime('%d-%m-%Y %H:%M:%S')} - {datalog}")

f = open("TIMEREQAPI", "r")
isi = f.read()
f.close()

waktu = datetime.now()
lastapi = datetime.strptime(isi, '%d-%m-%Y %H:%M:%S')
diff = waktu - lastapi

if diff.seconds >= 180 :
    url = 'http://127.0.0.1:8000/avc/ping'
    headers = {'accept': 'application/json'}

    response = requests.get(url, headers=headers, timeout=3)
    res_code = response.status_code
    if int(res_code / 100) == 5 :
        write_log("Server Error | Circuit Breaking | Reload Server")
        f = open("SERVER", "w")
        f.write(str(datetime.now()))
        f.close()
    else :
        write_log(f"Checking Routine Local API | Res Code {res_code}")