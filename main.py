from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
import logging
import calendar
import time
import os
from datetime import datetime
import pymysql
from pathlib import Path

app = FastAPI()

#declare variable
nogardu = 3

# COMMAND LIST
CMD_STARTUP = 0
CMD_PING = 1
CMD_PRESENT = 2

conn = pymysql.connect( 
    host='127.0.0.1', 
    user='avc',  
    password = "jmt02022!", 
    db='db_avc', 
    ) 
    
cur = conn.cursor()
query = f"INSERT INTO command_log (cmd_id) VALUES ('{CMD_STARTUP}')"
cur.execute(query) 
conn.commit() 

def write_log(datalog):
    waktulog = datetime.now()
    dirpathlog = f"LOG/API"
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

def insertcmd(cmd): 
    query = f"INSERT INTO command_log (cmd_id) VALUES ('{cmd}')"
    write_log(query)
    cur.execute(query) 
    conn.commit()

def insertpresent(idgardu,golongan,waktu,imgpath): 
    query = f"INSERT INTO present_avc (gardu_id, golongan_avc, detect_time, path_image) VALUES ('{idgardu}', '{golongan}', '{waktu}', '{imgpath}')"
    write_log(query)
    cur.execute(query) 
    conn.commit()

@app.post("/avc/present/")
async def avc_presents(idgardu: str, golongan: str, waktu: str , imgpath: str):
    insertcmd(CMD_PRESENT)
    insertpresent(idgardu,golongan,waktu,imgpath)
    write_log(f'Post Data {idgardu} | {golongan} | {waktu} | {imgpath}')
    if not golongan.isnumeric() :
        return {"status":401,"msg":"Golongan (" + golongan + ") is Not Valid"}
    if nogardu != int(idgardu) :
        return {"status":402,"msg":"Gardu (" + idgardu + ") is Not Match"}

    f = open("AVC", "w")
    f.write(golongan)
    f.close()

    return {"status":200,"msg":"OK","golongan": golongan}

@app.get("/avc/ping")
async def avc_ping():
    timestamp = calendar.timegm(time.gmtime())
    insertcmd(CMD_PING)
    write_log(f'Get Data PING')
    return {"status":200,"msg":"OK","gateid": nogardu,"timestamp":timestamp}

if __name__ == '__main__':
    f = open("AVC", "w")
    f.write("-")
    f.close()

    uvicorn.run("main:app", host="0.0.0.0", port=8000 ,reload=True)
