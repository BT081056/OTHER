#-- coding:utf-8 --**

import sys
import os
sys.path.append(os.getcwd())


from flask import Flask, render_template ,request, jsonify

import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
import json,requests
from Lib import SQLite
from Lib import ReadDB


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
    data=json.loads(request.get_data(as_text=True)) #<<<收到資料
    SQLite.InsertDataTabel('sensor_data2',data)### save to db
    return jsonify({"Result":"OK"})




if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')
