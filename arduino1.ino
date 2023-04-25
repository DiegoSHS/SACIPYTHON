#include <Ticker.h>
#include <DHT.h>
#include <DHT_U.h>

#include <SoftwareSerial.h>
//******Aire
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

int UVOUT = A0;   // Output from the sensor
int REF_3V3 = A1; // 3.3V power on the Arduino board

//*****************Manual
// malla
int malla = 7;
// bomba
const int bomba = 6;
const int Trigger = 2; // Pin digital 2 para el Trigger del sensor
const int Echo = 3;
// aspersor
const int aspersor = 5;

//*******************Automatico

const int alturaRecipiente = 83;
const int alturaMaxima = 60;
int dis;
int estado = 3;

const int mini = 20;

void tinacoAutomatico(int minimo, int estado, int distancia)
{
    if (estado == 1)
    {
        Serial.println(distancia);
        if (distancia <= minimo)
        {
            digitalWrite(bomba, LOW);
        }
        else if (distancia >= 100)
        {
            digitalWrite(bomba, HIGH);
        }
    }
    else
    {
    }
}

void distanTinaco()
{
    long t; // timepo que demora en llegar el eco
    long d; // distancia en centimetros

    digitalWrite(Trigger, HIGH);
    delayMicroseconds(10); // Enviamos un pulso de 10us
    digitalWrite(Trigger, LOW);

    t = pulseIn(Echo, HIGH); // obtenemos el ancho del pulso
    d = t / 59;              // escalamos el tiempo a una distancia en cm

    dis = ((alturaRecipiente - d) * 100) / alturaMaxima;

    if (isnan(dis))
    {
    }
    else
    {
        // Serial.println(dis);
    }

    tinacoAutomatico(mini, estado, dis);
    delay(1000);
}

//**************************************************************************************************************
void setup()
{
    Serial.begin(9600);     // Iniciar la comunicación serial a una velocidad de 9600 bps
    pinMode(malla, OUTPUT); // Configurar el pin del malla como salida
    digitalWrite(malla, HIGH);

    pinMode(bomba, OUTPUT); // Configurar el pin del bomba como salida
    digitalWrite(bomba, HIGH);
    pinMode(Trigger, OUTPUT);   // pin como salida
    pinMode(Echo, INPUT);       // pin como entrada
    digitalWrite(Trigger, LOW); // Inicializamos el pin con 0

    pinMode(aspersor, OUTPUT); // Configurar el pin del aspersor como salida
    digitalWrite(aspersor, HIGH);
    //****AIre
    pinMode(UVOUT, INPUT);
    pinMode(REF_3V3, INPUT);
    dht.begin();
}

void loop()
{
    distanTinaco();

    if (Serial.available() > 0)
    { // Si hay datos disponibles en la comunicación serial

        int relevador = Serial.parseInt(); // Leer el identificador enviado desde Python
        int state = Serial.parseInt();

        if (relevador == 7)
        {
            digitalWrite(malla, state);
            delay(1000);
            digitalWrite(malla, 1);
        }
        else if (relevador == 6)
        {
            digitalWrite(bomba, state);
        }
        else if (relevador == 5)
        {
            digitalWrite(aspersor, state);
        }
        else if (relevador == 4)
        {
            if (isnan(dis))
            {
            }
            else
            {
                estado = state;
            }
        }
    }

    int uvLevel = averageAnalogRead(UVOUT);
    int refLevel = averageAnalogRead(REF_3V3);

    // Use the 3.3V power pin as a reference to get a very accurate output value from sensor
    float outputVoltage = 3.3 / refLevel * uvLevel;

    float uvIntensity = mapfloat(outputVoltage, 0.99, 2.8, 0.0, 15.0) * 30; // Convert the voltage to a UV intensity level

    // Leemos la humedad relativa
    float h = dht.readHumidity();
    // Leemos la temperatura en grados centígrados (por defecto)
    float t = dht.readTemperature();
    // Leemos la temperatura en grados Fahreheit
    float f = dht.readTemperature(true);

    // Comprobamos si ha habido algún error en la lectura

    // Calcular el índice de calor en Fahreheit
    float hif = dht.computeHeatIndex(f, h);
    // Calcular el índice de calor en grados centígrados
    float hic = dht.computeHeatIndex(t, h, false);

    Serial.println("{\"Humedad\":" + String(h) + ", \"Temperatura\":" + String(t) + ", \"Intensidad\":" + String(uvIntensity) + ", \"Distancia\":" + String(dis) + "}");

    delay(1000);
}

// Returns the average
int averageAnalogRead(int pinToRead)
{
    byte numberOfReadings = 8;
    unsigned int runningValue = 0;

    for (int x = 0; x < numberOfReadings; x++)
        runningValue += analogRead(pinToRead);
    runningValue /= numberOfReadings;

    return (runningValue);
}

float mapfloat(float x, float in_min, float in_max, float out_min, float out_max)
{
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
