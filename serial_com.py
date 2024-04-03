import serial
import time
import io
import zlib
import base64
import rpyc
from rpyc.utils.server import ThreadedServer
from pathlib import Path
from datetime import datetime
import os
import pymysql
import binascii
from datetime import datetime
import sys

#Global Vars
noresi = 0
gardu_id = 3
ispresent = False

#GLOBAL COMMAND 
CMD_HEADER = b'\x69\x6f\x74'
CMD_SERICU = b'\xd2\x04\x00\x00'
CMD_ACK = b'\x02'

#GTO COMMAND
CMD_GTOINIT = b'\x00'
CMD_GTOSTORE = b'\x01'
CMD_GTODETECT = b'\x03'
CMD_GTOSTATRES = b'\x04'
CMD_GTORESET = b'\x06'

#CU COMMAND
CMD_CUPRESENT = b'\x01'
CMD_CUREQSTAT = b'\x04'
CMD_CUCANCEL = b'\x05'

#LENGHT COMMAND
LCMD_ACK = 5
LCMD_GTOINIT = 19
LCMD_GTOSTORE = 78
LCMD_GTODETECT = 45
LCMD_GTOSTATRES = 5
LCMD_GTORESET = 4
LCMD_CUPRESENT = 13
LCMD_CUREQSTAT = 4
LCMD_CUCANCEL = 14

#PARAM GTO
class GTO:
  def __init__(self, shift, perioda, resi, kspt, pultol, tipe):
    self.shift = shift
    self.perioda = perioda
    self.resi = resi
    self.kspt = kspt
    self.pultol = pultol
    self.tipe = tipe

class TRANS:
  def __init__(self, nosericu, stattrx, golavc, goletoll, goltrx, 
        entdatetime, extdatetime, rptday, rptmonth, rptyear, 
        ruas, shift, perioda, resi, kspt, pultol, rupiah, nokartu, statdetect, adddata) :

    self.nosericu = nosericu
    self.stattrx = stattrx
    self.golavc = golavc
    self.goletoll = goletoll
    self.goltrx = goltrx
    self.entdatetime = entdatetime
    self.extdatetime = extdatetime
    self.rptday = rptday
    self.rptmonth = rptmonth
    self.rptyear = rptyear
    self.ruas = ruas
    self.shift = shift
    self.perioda = perioda
    self.resi = resi
    self.kspt = kspt
    self.pultol = pultol
    self.rupiah = rupiah
    self.nokartu = nokartu
    self.statdetect = statdetect
    self.adddata = adddata

def write_log(datalog):
    waktulog = datetime.now()
    dirpathlog = f"LOG/Serial/{waktulog.strftime('%Y')}/{waktulog.strftime('%m')}"
    os.makedirs(dirpathlog, exist_ok=True)
    pathlog = f"{waktulog.strftime('%d%m%Y')}.log"
    file_path = Path(f"{dirpathlog}/{pathlog}")
    if not file_path.is_file():
        file_path.write_text(f"{waktulog.strftime('%Y-%m-%d %H:%M:%S')} - {datalog}\n")
    else :
        fb = open(f"{dirpathlog}/{pathlog}", "a")
        fb.write(f"{waktulog.strftime('%Y-%m-%d %H:%M:%S')} - {datalog}\n")
        fb.close
    
    print(f"{waktulog.strftime('%Y-%m-%d %H:%M:%S')} - {datalog}")

def checkCrc32(serHeader, serCMD, serData, serCrc32) :
    rawCMD = serHeader + serCMD + serData + serCrc32
    write_log(f"RAW Serial | {rawCMD.hex()}")
    valid = False
    getCrc32 = serHeader + serCMD + serData
    crc32 = zlib.crc32(getCrc32)
    if crc32 == int.from_bytes(serCrc32, byteorder='little') :
        valid = True
    
    return valid

def sendAck(status) :
    if status == 1 :
        dataAck = CMD_HEADER + CMD_ACK + b'\x01'
    else :
        dataAck = CMD_HEADER + CMD_ACK + b'\x00'

    crc32 = zlib.crc32(dataAck)
    dataAck = dataAck + crc32.to_bytes(4, byteorder='little')
    ser.flushOutput()
    ser.write(dataAck)

def sendGolAvc(golavc, idavc) :
    global noresi
    global ispresent

    if golavc == 1 or golavc == 0:
        byteavc = b'\x01'
    elif golavc == 2 :
        byteavc = b'\x02'
    elif golavc == 3 :
        byteavc = b'\x03'
    elif golavc == 4 :
        byteavc = b'\x04'
    elif golavc == 5 :
        byteavc = b'\x05'
    elif golavc == 6 :
        byteavc = b'\x06'

    seriavc = sericu = idavc
    
    dataAVC = CMD_HEADER + CMD_CUPRESENT + sericu.to_bytes(4, byteorder='little') + seriavc.to_bytes(4, byteorder='little') + byteavc
    crc32 = zlib.crc32(dataAVC)
    dataAVC = dataAVC + crc32.to_bytes(4, byteorder='little')

    write_log(f"RAW DATA Present : {dataAVC.hex()} | Seri CU/AVC {seriavc}")
    ser.flushOutput()
    write_log(f"Send Data AVC Golongan {golavc}")
    ser.write(dataAVC)

    ispresent = True

def getGTOStatus() :
    dataAVC = CMD_HEADER + CMD_CUREQSTAT
    crc32 = zlib.crc32(dataAVC)
    dataAVC = dataAVC + crc32.to_bytes(4, byteorder='little')

    ser.flushOutput()
    write_log(f"Get GTO Status")
    ser.write(dataAVC)

def sendGolCancel(golavc, idavc) :
    global noresi
    global ispresent

    if golavc == 1 or golavc == 0:
        byteavc = b'\x01'
    elif golavc == 2 :
        byteavc = b'\x02'
    elif golavc == 3 :
        byteavc = b'\x03'
    elif golavc == 4 :
        byteavc = b'\x04'
    elif golavc == 5 :
        byteavc = b'\x05'
    elif golavc == 6 :
        byteavc = b'\x06'

    seriavc = sericu = idavc
    
    dataAVC = CMD_HEADER + CMD_CUCANCEL + sericu.to_bytes(4, byteorder='little') + seriavc.to_bytes(4, byteorder='little') + byteavc
    crc32 = zlib.crc32(dataAVC)
    dataAVC = dataAVC + crc32.to_bytes(4, byteorder='little')

    write_log(f"RAW DATA Present : {dataAVC.hex()} | Seri CU/AVC {seriavc}")
    ser.flushOutput()
    write_log(f"Send Data AVC Golongan {golavc}")
    ser.write(dataAVC)

    ispresent = False

#MYSQL
SQL_CMD_STARTUP = 'Startup'
conn = pymysql.connect( 
    host='127.0.0.1', 
    user='avc',  
    password = "jmt02022!", 
    db='db_avc', 
    ) 
    
cur = conn.cursor()
query = f"INSERT INTO serial_log (cmd) VALUES ('{SQL_CMD_STARTUP}')"
cur.execute(query) 
conn.commit() 

def insertcmd(cmd): 
    query = f"INSERT INTO command_log (cmd_) VALUES ('{cmd}')"
    write_log(query)
    cur.execute(query) 
    conn.commit()

def insertupdatepresent(idavc, stattrx, golavc, goltrx, entdatetime, shift, resi, kspt, pultol, rupiah, nokartu) : 
    if str(golavc) == '0' :
        idavc = 0
    query = f"INSERT INTO store_avc (id_present, status, golongan_avc, golongan_gto, waktu_transaksi, shift, resi, kspt, pultol, rupiah, no_kartu, compare_avc) VALUES ('{idavc}', '{stattrx}', '{golavc}', '{goltrx}', '{entdatetime}', '{shift}', '{resi}', '{kspt}', '{pultol}', '{rupiah}', '{nokartu}', '0')"
    return query

def mysqlinsert(query) :
    write_log(query)
    cur.execute(query) 
    conn.commit()

ser = serial.Serial(
        port='/dev/ttyUSB0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 38400,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.5
)

ser.flushInput()
ser.flushOutput()

def main() :
    global ispresent
    countstore = 0
    golavc = 0
    idavc = 0

    gto = GTO(0, 0, 0, 0, 0, 0)
    trans = TRANS(0, 0, 0, 0, 0, '', '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', 0, '')
    ser.close()
    ser.open()
    write_log(f"Serial Status Open : {ser.isOpen()}")

    waktuserial = waktuserver = datetime.now()
    getGTOStatus()
    while ser.isOpen() :
        f = open("AVC", "r")
        isi = f.read()
        f.close()
        
        if len(isi) > 0 and isi[0] != '-' :
            waktuserver = datetime.now()
            # if idavc != 0 :
            #     sendGolCancel(golavc, idavc)
            x = isi.split('|')
            golavc = int(x[1])
            idavc = int(x[0])
            sendGolAvc(golavc, idavc)

        readHeader = ser.read(3)

        if readHeader == CMD_HEADER :
            waktuserial = datetime.now()
            readCMD = ser.read(1)
            if readCMD == CMD_ACK :
                write_log('GTO ACK')
                dataSer = ser.read(LCMD_ACK - 4)
                
                if dataSer == b'\x00' :
                    write_log('ACK OK')
                    if ispresent :
                        try :
                            ispresent = False
                            f = open("AVC", "w")
                            f.write("-")
                            f.close()
                        except :
                            pass
                else :
                    write_log('ACK NOT OK')

                dataCrc32 = ser.read(4)
                if checkCrc32(readHeader, readCMD, dataSer, dataCrc32) :
                    write_log("CRC VALID")
                else :
                    write_log("CRC NOT VALID")
            elif readCMD == CMD_GTOSTATRES :
                write_log('GTO RESPONSE STATUS')
                dataSer = ser.read(LCMD_GTOSTATRES - 4)

                if dataSer == b'\x00' :
                    write_log('GTO READY')
                elif dataSer == b'\x01':
                    write_log('GTO NOT READY')
                elif dataSer == b'\x02':
                    write_log('GTO BUSY')

                dataCrc32 = ser.read(4)
                if checkCrc32(readHeader, readCMD, dataSer, dataCrc32) :
                    write_log("CRC VALID")
                else :
                    write_log("CRC NOT VALID")
            elif readCMD == CMD_GTOINIT :
                write_log('GTO INIT')
                dataSer = ser.read(LCMD_GTOINIT - 4)
                dataCrc32 = ser.read(4)
                gto.shift = int.from_bytes(dataSer[0:1], byteorder='little')
                gto.perioda = int.from_bytes(dataSer[1:2], byteorder='little')
                gto.resi = int.from_bytes(dataSer[2:6], byteorder='little')
                gto.kspt = int.from_bytes(dataSer[6:10], byteorder='little')
                gto.pultol = int.from_bytes(dataSer[10:14], byteorder='little')
                gto.tipe = int.from_bytes(dataSer[14:15], byteorder='little')
                write_log(vars(gto))
                if checkCrc32(readHeader, readCMD, dataSer, dataCrc32) :
                    write_log("CRC VALID")
                    sendAck(0)
                else :
                    write_log("CRC NOT VALID")
                    sendAck(1)
            elif readCMD == CMD_GTOSTORE :
                write_log('GTO STORE')
                dataSer = ser.read(LCMD_GTOSTORE)
                rawtxt = readHeader + readCMD + dataSer
                write_log(f"RAW Serial Tanpa CRC | {rawtxt.hex()}")
                write_log(f"RAW Data Seri CU | {dataSer[0:4].hex()}")
                trans.nosericu = int.from_bytes(dataSer[0:4], byteorder='little')
                trans.stattrx =  int.from_bytes(dataSer[4:5], byteorder='little')
                trans.golavc = int.from_bytes(dataSer[5:6], byteorder='little')
                trans.goletoll = int.from_bytes(dataSer[6:7], byteorder='little')
                trans.goltrx = int.from_bytes(dataSer[7:8], byteorder='little')

                entday = int.from_bytes(dataSer[8:9], byteorder='little')
                entmonth = int.from_bytes(dataSer[9:10], byteorder='little')
                entyear = int.from_bytes(dataSer[10:11], byteorder='little')
                enthour = int.from_bytes(dataSer[11:12], byteorder='little')
                entminute = int.from_bytes(dataSer[12:13], byteorder='little')
                entsecond = int.from_bytes(dataSer[13:14], byteorder='little')
                trans.entdatetime = f'20{entyear}-{entmonth}-{entday} {enthour}:{entminute}:{entsecond}'

                extday = int.from_bytes(dataSer[14:15], byteorder='little')
                extmonth = int.from_bytes(dataSer[15:16], byteorder='little')
                extyear = int.from_bytes(dataSer[16:17], byteorder='little')
                exthour = int.from_bytes(dataSer[17:18], byteorder='little')
                extminute = int.from_bytes(dataSer[18:19], byteorder='little')
                extsecond = int.from_bytes(dataSer[19:20], byteorder='little')
                trans.extdatetime = f'20{extyear}-{extmonth}-{extday} {exthour}:{extminute}:{extsecond}'
                # {'nosericu': 1234, 'stattrx': 0, 'golavc': 1, 'goletoll': 1, 'goltrx': 1, 'entday': 31, 'entmonth': 12, 'entyear': 23, 'enthour': 0, 'entminute': 2, 'entsecond': 27, 'extday': 31, 'extmonth': 12, 'extyear': 23, 'exthour': 0, 'extminute': 2, 'extsecond': 27, 'rptday': 30, 'rptmonth': 12, 'rptyear': 23, 'ruas': 11, 'shift': 3, 'perioda': 3, 'resi': 502842, 'kspt': 190720, 'pultol': 152117, 'statdetect': 0, 'adddata': "b'\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'"} 
                trans.rptday = int.from_bytes(dataSer[20:21], byteorder='little')
                trans.rptmonth = int.from_bytes(dataSer[21:22], byteorder='little')
                trans.rptyear = int.from_bytes(dataSer[22:23], byteorder='little')
                trans.ruas = int.from_bytes(dataSer[23:24], byteorder='little')
                trans.shift = int.from_bytes(dataSer[24:25], byteorder='little')
                trans.perioda = int.from_bytes(dataSer[25:26], byteorder='little')
                trans.resi = int.from_bytes(dataSer[26:30], byteorder='little')
                trans.kspt = int.from_bytes(dataSer[30:34], byteorder='little')
                trans.pultol = int.from_bytes(dataSer[34:38], byteorder='little')
                trans.rupiah = int.from_bytes(dataSer[38:42], byteorder='little')
                bytedata = dataSer[42:74]
                write_log(f"RAW nokartu | {bytedata.hex()}")
                string_data = bytedata.decode('utf-8')
                trans.nokartu = f'{string_data}'
                write_log(vars(trans))
                dataCrc32 = dataSer[74:78]
                write_log(f"RAW CRC | {dataCrc32.hex()}")
                if checkCrc32(readHeader, readCMD, dataSer[0:74], dataCrc32) :
                    write_log("CRC VALID")
                    countstore = countstore + 1
                    print(countstore)
                    sendAck(0)
                    sql = insertupdatepresent(trans.nosericu, trans.stattrx, trans.golavc, trans.goltrx, trans.entdatetime, 
                    trans.shift, trans.resi, trans.kspt, trans.pultol, trans.rupiah, trans.nokartu)
                    mysqlinsert(sql)
                else :
                    write_log("CRC NOT VALID")
                    sendAck(1)
            elif readCMD == CMD_GTODETECT :
                write_log('GTO DETECT')
                
                dataSer = ser.read(LCMD_GTODETECT - 4)
                write_log(dataSer)
                trans.nosericu = int.from_bytes(dataSer[0:4], byteorder='little')
                trans.resi = int.from_bytes(dataSer[4:8], byteorder='little')
                trans.statdetect = int.from_bytes(dataSer[8:9], byteorder='little')
                trans.adddata = str(dataSer[9:41])
                
                write_log(vars(trans))

                dataCrc32 = ser.read(4)
                if checkCrc32(readHeader, readCMD, dataSer, dataCrc32) :
                    write_log("CRC VALID")
                    sendAck(0)
                else :
                    write_log("CRC NOT VALID")
                    sendAck(1)
            elif readCMD == CMD_GTORESET :
                write_log('GTO RESET')
                dataSer = ser.read(LCMD_GTORESET - 4)
                dataCrc32 = ser.read(4)
                if checkCrc32(readHeader, readCMD, dataSer, dataCrc32) :
                    write_log("CRC VALID")
                    sendAck(0)
                else :
                    write_log("CRC NOT VALID")
                    sendAck(1)
            else :
                write_log("COMMAND NOT VALID")
                ser.flushInput()
                ser.flushOutput()
                sendAck(1)

        waktunow = datetime.now()
        diffwaktu = waktunow - waktuserial

        # print(diffwaktu)
        # if abs(diffwaktu.seconds) >= 30 :
        #     getGTOStatus()

    write_log(f"Serial Status {ser.isOpen()}")
    sys.exit()
    ser.close()

if __name__ == "__main__":
    main()
