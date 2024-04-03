from fastapi import Depends, FastAPI, HTTPException, status, Form, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import uvicorn
import logging
import calendar
import time
import os
from datetime import datetime
import pymysql
from pathlib import Path

from pydantic import BaseModel
import base64
from io import BytesIO
from PIL import Image
import os

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

import sys

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"])

class ImageData(BaseModel):
    base64_data: str
    golongan: str
    golongan_koreksi: str
    waktu: str
    tipe_cam: str


##path_image adalah nama file
##path_cam1-cam4 based on folder di raspberry
##waktu adalah waktu deteksi
class Update_to_db(BaseModel):
    path_image: str
    golongan: str
    golongan_koreksi: str
    waktu: str

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

def insertcmd(cmd): 
    try :
        query = f"INSERT INTO command_log (cmd_id) VALUES ('{cmd}')"
        write_log(query)
        cur.execute(query) 
        conn.commit()
    except Exception as e:
        write_log(f"Insert command error {str(e)}")
        exit()

def insertpresent(idgardu,golongan,waktu,imgpath): 
    try :
        if golongan == '0' :
            golongan = '1'
        query = f"INSERT INTO present_avc (gardu_id, golongan_avc, detect_time, path_image) VALUES ('{idgardu}', '{golongan}', '{waktu}', '{imgpath}')"
        write_log(query)
        cur.execute(query) 
        conn.commit()

        query = f"select id from present_avc where detect_time = '{waktu}' and golongan_avc = '{golongan}'"
        cur.execute(query)
        MyDBResult = cur.fetchall()
        for x in MyDBResult :
            return x[0]
        
        return 0
    except Exception as e:
        write_log(f"Insert present error {str(e)}")
        exit()
        return 0

def updatepresent(nama_image, path_cam1, path_cam2, path_cam3, path_cam4, waktu) : 
    try :
        query = f"UPDATE present_avc set path_cam1 = '{path_cam1}', path_cam2 = '{path_cam2}', path_cam3 = '{path_cam3}', path_cam4 = '{path_cam4}'  where detect_time = '{waktu}' and path_image = '{nama_image}' order by id desc limit 1"
        write_log(query)
        cur.execute(query) 
        conn.commit()
    except Exception as e:
        write_log(f"update present error {str(e)}")
        exit()


@app.post("/avc/present/")
async def avc_presents(idgardu: str, golongan: str, waktu: str , imgpath: str):
    try :
        insertcmd(CMD_PRESENT)
        idavc = insertpresent(idgardu,golongan,waktu,imgpath)
        if idavc == 0 :
            exit()
        write_log(f'Post Data {idgardu} | {golongan} | {waktu} | {imgpath}')
        if not golongan.isnumeric() :
            return {"status":401,"msg":"Golongan (" + golongan + ") is Not Valid"}
        if nogardu != int(idgardu) :
            return {"status":402,"msg":"Gardu (" + idgardu + ") is Not Match"}

        # f = open("AVC", "w")
        # f.write(f'{idavc}|{golongan}')
        # f.close()

        return {"status":200,"msg":"OK","golongan": golongan}
    except Exception as e:
        write_log(f"api avc present error {str(e)}")
        return {"status":501,"msg":f"Server Error {str(e)}"}

@app.post("/avc/present2/")
async def avc_presents2(idgardu: str, golongan: str, waktu: str , imgpath: str):
    try :
        insertcmd(CMD_PRESENT)
        idavc = insertpresent(idgardu,golongan,waktu,imgpath)
        if idavc == 0 :
            exit()
        write_log(f'Post Data {idgardu} | {golongan} | {waktu} | {imgpath}')
        if not golongan.isnumeric() :
            return {"status":401,"msg":"Golongan (" + golongan + ") is Not Valid"}
        if nogardu != int(idgardu) :
            return {"status":402,"msg":"Gardu (" + idgardu + ") is Not Match"}

        f = open("AVC", "w")
        f.write(f'{idavc}|{golongan}')
        f.close()

        return {"status":200,"msg":"OK","golongan": golongan}
    except Exception as e:
        write_log(f"api avc present error {str(e)}")
        return {"status":501,"msg":f"Server Error {str(e)}"}

@app.get("/avc/ping")
async def avc_ping():
    try :
        insertcmd(CMD_PING)
        write_log(f'Get Data PING')
        
        waktuapi = datetime.now()
        f = open("TIMEREQAPI", "w")
        f.write(f"{waktuapi.strftime('%d-%m-%Y %H:%M:%S')}")
        f.close()

        return {"status":200,"msg":"OK","gateid": nogardu,"timestamp":f"{waktuapi.strftime('%d-%m-%Y %H:%M:%S')}"}
    except Exception as e:
        write_log(f"api avc ping error {str(e)}")
        return {"status":501,"msg":f"Server Error {str(e)}"}

@app.post("/avc/upload_image/")
async def upload_image(data: ImageData):
    try :
        golongan=data.golongan
        golongan_koreksi=data.golongan_koreksi
        waktu=data.waktu
        tipe_cam=data.tipe_cam
        base64_data=data.base64_data
        try:
            # Decode Base64 data to bytes
            decoded_image = base64.b64decode(base64_data)

            # Process the decoded image as needed
            image = Image.open(BytesIO(decoded_image))

            cur_dir = os.getcwd()

            waktufile = datetime.now().strftime("%d%m%Y")

            ## Make direktori if not exist
            dirpathgambar = f"image/{golongan_koreksi}/{waktufile}/"
            os.makedirs(dirpathgambar, exist_ok=True)

            ## Select tipe Cam
            if tipe_cam=="1":
                cam_ekstensi="cam1.jpg"
            elif tipe_cam=="2":
                cam_ekstensi="cam2.jpg"
            elif tipe_cam=="3":
                cam_ekstensi="cam3.jpg"
            elif tipe_cam=="4":
                cam_ekstensi="cam4.jpg"

            direktory_gambar=str(cur_dir)+"/"+dirpathgambar
            name_file=str(waktu+"-"+golongan+"-"+golongan_koreksi+"-"+cam_ekstensi)
            filename = os.path.join(direktory_gambar,name_file)
                    
            ## Save the image to the folder
            with open(filename, "wb") as image_file:
                image_file.write(decoded_image)
                write_log("Successed to Save Pict "+direktory_gambar+" "+name_file)
            
            return {"status": "success", "message": "Image uploaded and processed successfully."}
        except Exception as e:
            write_log("Failed to Save Pict "+direktory_gambar+" "+name_file)
            return {"status":403,"msg":f"Fail Save Picture {str(e)}"}
    except Exception as e:
        write_log(f"api avc uploadimg error {str(e)}")
        return {"status":501,"msg":f"Server Error {str(e)}"}

@app.post("/avc/update_img_to_db/")
async def update_img_to_db(data: Update_to_db):   
    try :
        nama_image=data.path_image
        golongan=data.golongan
        golongan_koreksi=data.golongan_koreksi
        waktu_deteksi=data.waktu
        waktufile = datetime.now().strftime("%d%m%Y")

        ## Make direktori if not exist
        dirpathgambar = f"image/{golongan_koreksi}/{waktufile}/"

        path_cam1=dirpathgambar+nama_image+"-cam1.jpg"
        path_cam2=dirpathgambar+nama_image+"-cam2.jpg"
        path_cam3=dirpathgambar+nama_image+"-cam3.jpg"
        path_cam4=dirpathgambar+nama_image+"-cam4.jpg"
        #updatepresent(nama_image, path_cam1, path_cam2, path_cam3, path_cam4, waktu) 
        try:
            updatepresent(nama_image, path_cam1, path_cam2, path_cam3, path_cam4, waktu_deteksi)
            write_log("Succeed to update insert image db")
            return {"status": "success", "message": "database updated insert image."}
        except Exception as e:
            write_log("Failed to update insert image db")
            return {"status":404,"msg":f"Server Error {str(e)}"}
    except Exception as e:
        write_log(f"api avc updateimgdb error {str(e)}")
        return {"status":501,"msg":f"Server Error {str(e)}"}

if __name__ == '__main__':
    f = open("AVC", "w")
    f.write("-")
    f.close()
    
    f = open("SERVER", "w")
    f.write(str(datetime.now()))
    f.close()

    write_log('startup')
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True, reload_includes="SERVER")
