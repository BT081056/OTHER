#-- coding:utf-8 --**

import sys
import os
sys.path.append(os.getcwd())
import warnings
warnings.filterwarnings("ignore")

from flask import Flask, render_template ,request, jsonify


import numpy as np
import json
from Lib import SQLite
from Lib import ReadDB
from Lib import PollingDevice_Lib
import multiprocessing

app = Flask(__name__)

@app.route('/')
def index():
#    return render_template('HotmapYA.html')
    return render_template('HotmapYA_plus.html')



@app.route('/Mac2Name',methods=['GET'])
def Maclist():
    mac_list = ReadDB.All_mac()
#    source = { "mac":["asd555","asd666","asd888"] , "name" : ["EQ01","EQ02","EQ03"]}
    return jsonify(mac_list)



@app.route('/Mac2Name_Save',methods=['GET','POST']) #IP:5000/ABC 路由API
def Mac2Name_Save():
    print('--------------------------------------')
    data=json.loads(request.get_data(as_text=True)) #<<<收到資料
    Js = { "mac":"asd888" , "name" : "EQ01"}
    if '[' in data['name'] or '[' in data['mac']:
        return jsonify('Pleace Drop []')
    else:
        SQLite.InsertDataTabel('MacNo',data)### save to db    
        return jsonify(data['mac'])


@app.route('/Spc_Save',methods=['GET','POST']) #IP:5000/ABC 路由API
def Spc_Save():
    print('--------------------------------------')
    data=json.loads(request.get_data(as_text=True)) #<<<收到資料
    Js = { "mac":"asd888" ,"parameter":"Max", "value" : "10"}
    print(data['mac'])
    SQLite.InsertDataTabel('MacSpc',data)### save to db    
    return jsonify(data['mac'])
    
@app.route('/GetMacData',methods=['GET','POST']) #IP:5000/ABC 路由API
def GetMacData():
    print('--------------------------------------')
    data=json.loads(request.get_data(as_text=True)) #<<<收到資料
    MacNo=data['mac']
    print('-------',MacNo)
    data,json_df = ReadDB.SENSOR_TopN(MacNo,30)
    dts,tempMaxs,tempMins,tempAvgs = ReadDB.Mixtemp(data)
    SPC = ReadDB.FindMacSpc(MacNo)
    print('*******************************************')
    

    IrData = ReadDB.GetIRdata(MacNo)
    source = {"HotMap":IrData , "dt" : dts,
              "Max":tempMaxs,"Avg":tempAvgs,"Min":tempMins,"SpcMax":SPC['Max'],"SpcAvg":SPC['Avg'],"SpcMin":SPC['Min']}
    return jsonify(source)

@app.route('/GetMacDataplus',methods=['GET','POST']) #IP:5000/ABC 路由API
def GetMacDataplus():
    print('--------------------------------------')
    data=json.loads(request.get_data(as_text=True)) #<<<收到資料
    MacNo=data['mac']
    print('-------',MacNo)
    data,json_df = ReadDB.SENSOR_TopN(MacNo,30)
    dts,tempMaxs,tempMins,tempAvgs = ReadDB.Mixtemp(data)
    SPC = ReadDB.FindMacSpc(MacNo)
    print('*******************************************')
    

    IrData = ReadDB.GetIRdata_plus(MacNo)
    source = {"HotMap":IrData , "dt" : dts,
              "Max":tempMaxs,"Avg":tempAvgs,"Min":tempMins,"SpcMax":SPC['Max'],"SpcAvg":SPC['Avg'],"SpcMin":SPC['Min']}
    return jsonify(source)
@app.route('/GetMacData_a',methods=['GET','POST']) #IP:5000/ABC 路由API
def GetMacData_a():
    print('--------------------------------------')
    data=json.loads(request.get_data(as_text=True)) #<<<收到資料
    MacNo=data['mac']
    
    IrData = ReadDB.GetIRdata__(MacNo)
    source = {"HotMap":IrData}
    return jsonify(source)


@app.route('/sensor_data2',methods=['GET','POST']) #IP:5000/ABC 路由API
def sensor_data():
    print('get')
    data=json.loads(request.get_data(as_text=True)) #<<<收到資料
    SQLite.InsertDataTabel('sensor_data2',data)### save to db
#    json_string = SQLiteLogicalInstruction.SENSOR_Top2('sensor_data2')
    sensor = data['sensor_value'].split(',')
    mac = data['sensor_no']
    Eth_init()
    Arraydata = np.reshape(sensor,(24,32))
    print(f'{"INFO":*^30}')
    wait2Polling = PollingDevice_Lib.checkPolling(mac,Arraydata)
    
#    PollingDevice_Lib.sendPolling(eqpid,WaitPublicData)
    p = multiprocessing.Process(target = PollingDevice_Lib.sendPolling, args = (wait2Polling,))
    p.start()
    return jsonify({"Result":"OK"})

def Eth_init():
    os.system('sudo ifmetric eth0 300')
    os.system('sudo ifmetric wlan0 300')


if __name__ == '__main__':
    Eth_init()
    app.run(debug=True,host='0.0.0.0')
