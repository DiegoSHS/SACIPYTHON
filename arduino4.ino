#include <Ticker.h>
#include <ArduinoJson.hpp>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>
#include "MQ135.h"
#include "GravityTDS.h"
#define pinAire1 A0
#define pinAire2 A1
#define LDRPin GND;
#define TdsSensorPin A2;
const long A = 1000;    //Resistencia en oscuridad en KΩ
const int B = 15;       //Resistencia a la luz (10 Lux) en KΩ
const int Rc = 10; 
GravityTDS gravityTds;

void tdsvalue(){
    gravityTds.setTemperature(temperature);
    gravityTds.update();
    tdsValue = gravityTds.getTdsValue();
    return tdsValue;
}
void lumn(){
    int luminic = digitalRead(LDRPin);
    int ilum = ((long)V*A*10)/((long)B*Rc*(1024-luminic));
    return ilum;
}
void co2(){
    MQ135 gasSensor = MQ135(pinAire1);
    float rzero = gasSensor.getRZero();
    return rzero;
}
void datas()
{
    float rzero = co2();
    int ilum = lumn();
    float tds = tdsvalue();

    String json;
    StaticJsonDocument<300> doc;
    doc["co2"] = String(rzero);
    doc["lum"] = String(ilum);
    doc["tds"] = String(tds);
    serializeJson(doc, json);
    Serial.println(json);
}
Ticker enviarDatos(datas, 500);
void setup()
{
    gravityTds.setPin(TdsSensorPin);
    gravityTds.setAref(5.0);
    gravityTds.setAdcRange(1024);
    gravityTds.begin();
    pinMode(LDRPin, INPUT);
    Serial.begin(9600);
    enviarDatos.start();
}

void loop()
{
    mostrarDatos.update();
}
