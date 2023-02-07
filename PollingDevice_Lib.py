#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 16:21:26 2023

@author: pi
"""
import warnings
warnings.filterwarnings("ignore")
import configparser
import time
import socket
import requests

def checkPolling(mac,Arraydata):
    config = configparser.ConfigParser()    
    config.read('PollingSet.ini')
    WaitPublicData = {}
    PublicSet = {}
    for PLCIO in config:
        buff = {}
        for key in config.items(PLCIO):
            buff[key[0]] = key[1]
        PublicSet[PLCIO] = buff
    for data in PublicSet:
        
        
        
        try:
            Mac = PublicSet[data]['mac']
            if Mac == mac:
                eqpid,PLCPin = data.split('_')
                Mac = PublicSet[data]['mac']
                X1 = int(PublicSet[data]['x1'])
                Y1 = int(PublicSet[data]['y1'])
                X2 = int(PublicSet[data]['x2'])
                Y2 = int(PublicSet[data]['y2'])
                P0 = Arraydata[X1:X2,Y1:Y2]
                WaitPublicData[PLCPin] = str(int(float(Fmax(P0))*10))
        except:
            pass
    return {eqpid:WaitPublicData}
    
def sendPolling(data):
    for hostname in data:
        dic = data[hostname]
        serve_ip = socket.gethostbyname(hostname)#hostname='ABANI700-0A'
        print(serve_ip)
        web = 'http://%s:8080/'%serve_ip
        return_Code = requests.get(web)
        print(return_Code.status_code) #首先確認一下從Polling Device傳回的狀態碼，顯示 200 就代表正常
        url = web + '/api/setPLCDeviceDataRandom'
        #url = web + '/api/setPLCDeviceDataBatch'
        for di in dic:
            key = di
            value = ValuetoHex(dic[key]).upper()
            string1= '{"device_addresses":["%s"],"device_data":["%s"],"network_no":0,"station_no":255} '%(key,value)
            #string1= '{"device_type":"D","start_address":"%s","device_count":1,"device_data":"%s","network_no":0,"station_no":255} '%(key,value)
            print(string1)
            response = requests.get(url, params={"argument":string1})
            print(response.text,key,value)
            time.sleep(2)

def Fmax(data):
    mm = -999
    for ii in data:
        d1 = float(max(ii))
        if mm <= d1:
            mm = d1
    return mm

def ValuetoHex(value = 999):
    v0 = str(hex(int(value))[2:])
    sl = 4-len(v0)
    for c in range(sl):
#        print(i)
        v0 = '0' + v0
    return v0

if __name__ == '__man__':
    print('go;')