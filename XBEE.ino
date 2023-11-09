// 20200428 update 
// v.1.2
/************************************
*            2020/04/05             *
*  1. fix receive data string       *
*  1.1 fix indata[7] = gain         *
*  1.2 fix indata[8] = total        *
*  2. fix getADC function           *
************************************/

/******************************************************************************************
void freshHMI(void)      // 每秒更新HMI (1 Second Average)畫面一次
void sendResult(void)    // 每分更新HMI (1 Minute Average)畫面一次 , 並使用 SoftwareSerial 的 Xbee上傳資料到APC
void resetTimer(void)    // 系統每經過 rstTime 的時間後 , 進行Reset Arduino及HMI
void serialFlush()       // 清空UART BUFFER的資料
void PAN_write(void)     // 透過SoftwareSerial 進行 Xbee資料寫入
void EndCmd(void)        // 傳送HMI命令的前後 , 須加上EndCmd , 即連續傳送 0xFF 0xFF 0xFF
void getADC(void)        // 讀取ADS1115各Channel的數值
int receiveSetting(void) // 讀取RX Buffer , 並判斷收到的資料與命令為何
*****************************************************************************************/

#include <Wire.h>
#include <math.h>
#include <SoftwareSerial.h>
#include <Adafruit_ADS1015.h>

SoftwareSerial xbeeSerial(2,3);  //RX,TX

Adafruit_ADS1115 ads1(0x48);
Adafruit_ADS1115 ads2(0x49);

//const unsigned long rstTime = 86400000;
const unsigned long rstTime = 86400000;  
unsigned long tmpInt;
int strCnt ;
char buf[12];
char buf2[12];
char buf3[12];
double aa;
unsigned long newInt;
    
unsigned long timerSec ;
unsigned long timerMin ;
unsigned long timerRst ;
int cntMin ;
int cntSec ;

int16_t adc1[4] ;
int16_t adc2[4] ;
int16_t adc[8];

unsigned long adcSumSec[8];
float currentSec[8];
float currentMin[8];
float powerMin[8];
int tmp;

// garbage , PAN ID , Voltage1 , Voltage2 , Voltage3 , Voltage4 , Voltage5 , Voltage6 , Voltage7 , Voltage8 , CT Type1 , CT Type2 , CT Type3 , CT Type4 , CT Type5 , CT Type6 , CT Type7 , CT Type8 , CT Number , MAC Address , Phase , Gain1 , Gain2 , Gain3 ,  Gain4 ,  Gain5 ,  Gain6 ,  Gain7 ,  Gain8  , Total
//    0    ,    1   ,    2    ,     3    ,     4    ,      5     ,   6     ,    7     ,    8     ,    9     ,     10   ,     11   ,     12   ,    13    ,    14    ,    15    ,    16    ,    17    ,    18     ,     19      ,   20  ,   21  ,   22  ,   23  ,    24  ,    25  ,    26  ,    27  ,    28   ,  29                                                                                      
String indata[30];  

//------- APC Xbee Define ---------
String mac_addr = "0013A2000013A200";
const char STX = 0x02;
const char ETX = 0x03;
const char CR = 0x13;
const char LF = 0x10;
//------- APC Xbee Define ---------

int panID ;
int voltage[8];
int ctType[8];
int ctNum;
int phase ;
float phaseValue;
float gain[8];   // gain of current


void(* resetFunc) (void) = 0; //reset command

void setup()
{     
   Wire.begin();
   xbeeSerial.begin(9600); 
   Serial.begin(9600);
   delay(50);
   Serial.println(F("Booting"));
   serialFlush();
    
   ads1.begin();
   ads2.begin();

   while(1) {   // 直到接收到HMI 回傳的參數
       if(receiveSetting()==1)  { 
           break;
       }
       delay(10);  
    } //while(1)
    
    Serial.println(F("Received Setting !")) ;    
    EndCmd();  
 
    panID = indata[1].toInt();
    
    for (int i=0;i<8;i++)
    {
      voltage[i] = indata[i+2].toInt();
    }


    for (int i=0;i<8;i++)
    {
      ctType[i] = indata[i+10].toInt();
    }


    ctNum  = indata[18].toInt();   
    mac_addr= indata[19];
    phase = indata[20].toInt();


    for (int i=0;i<8;i++)
    {
      gain[i] = indata[i+21].toInt()/ 100.0;
    }

    

    if (phase == 3){
        phaseValue = 1.723;
    }else {
        phaseValue = 1.0;  
    }
    
    Serial.println();
    Serial.print(F("PanID : "));     Serial.println(panID);
    Serial.print(F("CT Number: "));  Serial.println(ctNum);
    Serial.print(F("MAC Address: "));Serial.println(mac_addr);
    Serial.print(F("Phase : "));     Serial.println(phase);
    
    PAN_write();  // write panID to Xbee by SoftwareSerial

    ads1.begin();
    ads2.begin();

    for (int i = 0 ; i < 4 ; i++){
        adc1[i]=0 ;
        adc2[i]=0 ;
        currentSec[i]=0.0;
        currentMin[i]=0.0;
        currentSec[i+4]=0.0;
        currentMin[i+4]=0.0;
        adcSumSec[i];
        adcSumSec[i+4];      
    }

    cntMin = 0;
    cntSec = 0  ;
    timerSec = millis();
    timerMin = millis();
    timerRst = millis();
}

// ----------------------------------------------------------------------------

void loop()
{   
    resetTimer();       // reset arduino everyday
    receiveSetting();   // receive USART command
    getADC();           // Loading ADC value

    //--------------------------  1 second avg ------------------------
    if ((millis() - timerSec) > 1000 ){
        freshHMI(); 
        for (int i = 0 ; i < 8 ; i ++) {          
            // 讀取ADC1115輸入加總 , 計算每秒平均電流
            currentSec[i] = (adcSumSec[i] / cntSec * 0.1875) /1000.0 *ctType[i] /5.0 * gain[i] ;             
            // 每分鐘平均電流儲存於 currentMin
            currentMin[i] = currentMin[i]+currentSec[i];
            adcSumSec[i] = 0;
        } 
        cntMin++;
        cntSec = 0 ;
        timerSec = millis();
    }
    //----------------------  1 minute avg --------------------------------
    else if ((millis() - timerMin) > 60000 ){        
        for (int i = 0 ; i < 8 ; i ++) {  
            currentMin[i] = currentMin[i] / cntMin;
        }
        sendResult();        
        cntMin = 0 ;
        for (int i = 0 ; i < 8 ; i ++) {
            currentMin[i]=0;
        }
        timerMin = millis();             
    }    
}  //void loop()

//--------------------------------------------------------------------------

int receiveSetting(void){
    int flag;
    flag =0;
    strCnt = 0 ; 
    
    for (int i = 0 ; i < 30 ; i++) {
        indata[i]="";
    }        

    while (Serial.available()) {
        char c = Serial.read();
        // if(c!='\n'){
        // 如果沒有讀到\n (0x0A)  而且也沒讀到逗號 , (0x2C) , 那就持續讀字串
        if(c!='\n' && c!=0x2C){  // 0x2C ==> ,
            indata[29] += c;         
        }
        // 如果有讀到逗點 , (0x2C)  那就存成下一筆
        else if(c==0x2C) {
            indata[strCnt] = indata[29] ;
            indata[29] = "" ;  
            strCnt++;
        }
        delay(5);    // 沒有延遲的話 UART 串口速度會跟不上Arduino的速度，會導致資料不完整
    }      

    // 判斷是否收到 HMI 的重啟請求
    // 如果 indata[1] 收到 rest命令 , 便傳送 rest命令給 HMI 要求重啟
    // 並將 Arduino 本體進行 reset
    if (indata[1] == "rest"){  // 確定有讀到rest再進行 rest
        Serial.println(F("Reset"));
        for (int i = 0 ; i < 3 ; i++){
            delay(50);
            EndCmd();             
            Serial.write("rest");
            EndCmd();
            delay(50);                
        }
        resetFunc();        
    }

    // 判斷是否收到增益值
    // 如 indata[2] 收到 101 , 代表為 1.01 , 需除以100
    if (indata[1]=="GAIN"){
      if (indata[2]=="1")
      {
        gain[0] = indata[3].toInt()/100.0;    
        Serial.println(gain[0]);
      }
      else if (indata[2]=="2")
      {
        gain[1] = indata[3].toInt()/100.0;    
        Serial.println(gain[1]);
      }
      else if (indata[2]=="3")
      {
        gain[2] = indata[3].toInt()/100.0;    
        Serial.println(gain[2]);
      }
      else if (indata[2]=="4")
      {
        gain[3] = indata[3].toInt()/100.0;    
        Serial.println(gain[3]);
      }
      else if (indata[2]=="5")
      {
        gain[4] = indata[3].toInt()/100.0;    
        Serial.println(gain[4]);
      }
      else if (indata[2]=="6")
      {
        gain[5] = indata[3].toInt()/100.0;    
        Serial.println(gain[5]);
      }
      else if (indata[2]=="7")
      {
        gain[6] = indata[3].toInt()/100.0;    
        Serial.println(gain[6]);
      }
      else if (indata[2]=="8")
      {
        gain[7] = indata[3].toInt()/100.0;    
        Serial.println(gain[7]);
      }         
    }
    
    if (indata[1] != ""){  // 確定有讀到命令再進行 print
        for (int i = 0 ; i < 30 ; i++) {
            if(indata[i] != "") {
                Serial.print(F("indata["));
                Serial.print(i);
                Serial.print(F("] = "));
                Serial.println(indata[i]);            
            }        
            strCnt =0;
        }      
    }
        
    for(int i = 0 ; i < 29 ; i++){
        if (indata[i]==""){
            flag=0;                   
        }else
            flag=1;
    }
    indata[29]="";
    return flag;
}

//--------------------------------------------------------------------------

void getADC(void)
{ 
  cntSec++; 
  for (int i = 0 ; i < 4 ; i++){
      adc[i]   = ads1.readADC_SingleEnded(i);
      adc[i+4] = ads2.readADC_SingleEnded(i);
      if(adc[i]  < 0) { adc[i]  =0;}
      if(adc[i+4]< 0) { adc[i+4]=0;}
  }
  for (int i = 0 ; i < 8 ; i++){  
      adcSumSec[i] = adcSumSec[i] + adc[i];
  }
}

//--------------------------------------------------------------------------

void EndCmd(void)   {
    Serial.write(0xFF);
    Serial.write(0xFF);
    Serial.write(0xFF);    
}

//--------------------------------------------------------------------------
 
void PAN_write(void) {
    delay(1000);
    xbeeSerial.print("+++")  ;
    delay(1100);
    xbeeSerial.println();
    xbeeSerial.print("ATID ");
    xbeeSerial.println(panID);
    delay(1000);
    xbeeSerial.print("ATJV ");
    xbeeSerial.println(1);
    delay(1000);
    xbeeSerial.println("ATWR");
    delay(1000);
    xbeeSerial.println("ATAC");
    delay(1000);
    xbeeSerial.println("ATCN");
    delay(2000);      
    Serial.println(F("PAN Setting Done"));
}  

//--------------------------------------------------------------------------

void serialFlush(){
    while(Serial.available() > 0) {
      char t = Serial.read();
    }
}   

//--------------------------------------------------------------------------

void resetTimer(void){
    // reset Arduino & HMI everyday
    // 1 Day = 86,400 Seconds = 86,400,000 mini Seconds
    if ((millis() - timerRst) > rstTime) {
        serialFlush();
        for(int i = 0 ; i < 5 ; i++){
            EndCmd();
            Serial.write("rest");
            EndCmd();
            delay(100);  
            }
     resetFunc();
     }
}

//---------------------------------------------------------------------------
// update avg data every second
void freshHMI(void)
{
    //----- Average Current in 1 Second ----

    aa = currentSec[0]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);    
    indata[6] = "x11.val=";
    indata[6].toCharArray(buf2,30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf); 
    EndCmd();
    Serial.write(buf3);
    EndCmd();      
    
    aa = currentSec[1]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);    
    indata[6] = "x21.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf); 
    EndCmd();
    Serial.write(buf3);
    EndCmd();  

    aa = currentSec[2]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);    
    indata[6] = "x31.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf); 
    EndCmd();
    Serial.write(buf3);
    EndCmd();  

    aa = currentSec[3]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);    
    indata[6] = "x41.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf); 
    EndCmd();
    Serial.write(buf3);
    EndCmd();

    aa = currentSec[4]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);    
    indata[6] = "x51.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf); 
    EndCmd();
    Serial.write(buf3);
    EndCmd();

    aa = currentSec[5]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);    
    indata[6] = "x61.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf); 
    EndCmd();
    Serial.write(buf3);
    EndCmd();

    aa = currentSec[6]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);    
    indata[6] = "x71.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf); 
    EndCmd();
    Serial.write(buf3);
    EndCmd();

    aa = currentSec[7]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);    
    indata[6] = "x81.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf); 
    EndCmd();
    Serial.write(buf3);
    EndCmd();


    //-------------------------------- Average Power in 1 Second ------------------------------ 
    delay(20) ; 

    aa = currentSec[0]*100*voltage[0]*phaseValue/1000;
    newInt = long(aa);
    ltoa(newInt , buf , 10);    
    indata[6] = "x12.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd();   
    

    aa = currentSec[1]*100*voltage[1]*phaseValue/1000;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x22.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd();   

    aa = currentSec[2]*100*voltage[2]*phaseValue/1000;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x32.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd();  

    aa = currentSec[3]*100*voltage[3]*phaseValue/1000;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x42.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd();  

    aa = currentSec[4]*100*voltage[4]*phaseValue/1000;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x52.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd();  

    aa = currentSec[5]*100*voltage[5]*phaseValue/1000;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x62.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd();  

    aa = currentSec[6]*100*voltage[6]*phaseValue/1000;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x72.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd();  

    aa = currentSec[7]*100*voltage[7]*phaseValue/1000;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x82.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd();  


    Serial.println();
}

//--------------------------------------------------------------------------------------------

void sendResult(void)  // send to Xbee & refresh hmi
{
    Serial.println();
    //-------------------------- Average Current in 1 Minute -----------------------
    aa = currentMin[0]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x13.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd();    

    aa = currentMin[1]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x23.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 

    aa = currentMin[2]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x33.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 


    aa = currentMin[3]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x43.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 

    aa = currentMin[4]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x53.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 


    aa = currentMin[5]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x63.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 

    aa = currentMin[6]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x73.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 

    aa = currentMin[7]*100;
    newInt = long(aa);
    ltoa(newInt , buf , 10);
    indata[6] = "x83.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 


    
    //----------------------------- Average Power in 1 Minute ------------------------------ 
    delay(20) ; 
    powerMin[0] = currentMin[0]*100*voltage[0]*phaseValue/1000;
    newInt = long(powerMin[0]);
    ltoa(newInt , buf , 10);
    indata[6] = "x14.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd();    

    powerMin[1] = currentMin[1]*100*voltage[1]*phaseValue/1000;
    newInt = long(powerMin[1]);
    ltoa(newInt , buf , 10);
    indata[6] = "x24.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 

    powerMin[2] = currentMin[2]*100*voltage[2]*phaseValue/1000;
    newInt = long(powerMin[2]);
    ltoa(newInt , buf , 10);
    indata[6] = "x34.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 

    powerMin[3] = currentMin[3]*100*voltage[3]*phaseValue/1000;
    newInt = long(powerMin[3]);
    ltoa(newInt , buf , 10);
    indata[6] = "x44.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 

    powerMin[4] = currentMin[4]*100*voltage[4]*phaseValue/1000;
    newInt = long(powerMin[4]);
    ltoa(newInt , buf , 10);
    indata[6] = "x54.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 

    powerMin[5] = currentMin[5]*100*voltage[5]*phaseValue/1000;
    newInt = long(powerMin[5]);
    ltoa(newInt , buf , 10);
    indata[6] = "x64.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 

    powerMin[6] = currentMin[6]*100*voltage[6]*phaseValue/1000;
    newInt = long(powerMin[6]);
    ltoa(newInt , buf , 10);
    indata[6] = "x74.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 

    powerMin[7] = currentMin[7]*100*voltage[7]*phaseValue/1000;
    newInt = long(powerMin[7]);
    
    ltoa(newInt , buf , 10);
    indata[6] = "x84.val=";
    indata[6].toCharArray(buf2 , 30); 
    strcpy(buf3 , buf2);
    strcpy(buf3 + strlen(buf2) , buf);              // 合併字串 
    EndCmd();
    Serial.write(buf3);
    EndCmd(); 
    Serial.println();
    

    indata[6]= String(mac_addr) + ",";
    indata[7]= String(ctNum);
    Serial.print(indata[6]);
    Serial.print(indata[7]);
    for (int i = 0 ; i < ctNum ; i++){
        Serial.print(","+ String(currentMin[i]));    
    }    
    Serial.println();



    
    xbeeSerial.print(STX);     
    xbeeSerial.print(indata[6]);
    xbeeSerial.print(indata[7]);
    for (int i = 0 ; i < ctNum ; i++){
        //xbeeSerial.print(","+ String(currentMin[i]*voltage[i]*phaseValue/1000));// APC輸出功率 KW
        xbeeSerial.print(","+ String(currentMin[i]));// APC僅電流輸出
    }    
    xbeeSerial.print(ETX);
    xbeeSerial.print(CR);
    xbeeSerial.print(LF);
    xbeeSerial.println();    
}
