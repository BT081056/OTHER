#include "HX711.h"
#include <LiquidCrystal_PCF8574.h>
//system("\"C:\\Documents and Settings\\user\\Application Data\\Microsoft\\Internet Explorer\\Quick Launch\\Show Desktop.scf\"");
LiquidCrystal_PCF8574 lcd(0x27);  // 設定i2c位址，一般情況就是0x27和0x3F兩種

// 接線
const int DT_PIN = 6;
const int SCK_PIN = 5;

const char mac_addr[] = "0013A20041BEB074";

const char STX = 0x02;

const char ETX = 0x03;

const char CR = 0x13;

const char LF = 0x10;

const int scale_factor = 440; //比例參數，從校正程式中取得

HX711 scale;

void setup() {
  Serial.begin(9600);
  //Serial.println("Initializing the scale");

  scale.begin(DT_PIN, SCK_PIN);
  lcd.begin(16, 2); // 初始化LCD
  lcd.setBacklight(255);
  lcd.clear();

  //Serial.println("Before setting up the scale:"); 
  
  //Serial.println(scale.get_units(5), 0);  //未設定比例參數前的數值

  scale.set_scale(scale_factor);       // 設定比例參數
  scale.tare();               // 歸零

  //Serial.println("After setting up the scale:"); 

  //Serial.println(scale.get_units(5), 0);  //設定比例參數後的數值

  //Serial.println("Readings:");  //在這個訊息之前都不要放東西在電子稱上
}

void loop() {
  
  //Serial.println(scale.get_units(20), 0); 
  lcd.clear();
  lcd.setCursor(0, 0);  //設定游標位置 (字,行)
  lcd.print("Weight: ");
  lcd.setCursor(9, 0);
  float weight = scale.get_units(20);  // 取得20次數值的平均
  float Tension_Volt=weight;
  //避免出現負數
  if(weight<=0){
    weight = 0;
  }
  lcd.print(weight,0);
  lcd.setCursor(13, 0);
  lcd.print("g");
  scale.power_down();             // 進入睡眠模式
  delay(5000);
  scale.power_up();               // 結束睡眠模式

  Serial.print(STX);

  Serial.print(mac_addr);

  Serial.print(",");

  Serial.print("1"); 

  Serial.print(",");   

  Serial.print(Tension_Volt);

  Serial.print(ETX);

  Serial.print(CR);

  Serial.println(LF);
}
