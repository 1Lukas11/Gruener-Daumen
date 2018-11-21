from grove_rgb_lcd import *
import time
import grovepi
import math
import json


# LCD init
setText("Hallo Gruenfinger\nLCD init")
setRGB(0,128,64)

# Analog Sensoren
sensorMois = 2
sensorLight = 0

# Digital Sensoren
sensorDHT = 3


# DHT Sensor typ:
blue = 0

grovepi.pinMode(sensorLight, "INPUT")

# Timer
wartezeit = 30

# Grenzwerte
mois_min = 300
mois_max = 700
light_min = 250
temp_min = 22
temp_max = 26

# Schalter fuer Fehler
bool_trocken = False
bool_nass = False
bool_feuchtigkeit = False # wenn trocken oder nass = true
bool_kalt = False
bool_warm = False
bool_temperatur = False # wenn kalt oder warm = true
bool_helligkeit = False
bool_ok = True


# Ausgaben
print_trocken = "zu trocken"
print_nass = "zu nass"
print_kalt = "zu kalt"
print_warm = "zu warm"
print_dunkel = "zu dunkel"

# RGB
rot = 153,0,0
gruen = 53,153,0

def ausgabe_panel():
    zeiteinheit = wartezeit / 3
    if bool_ok == True:
        setRGB(53,153,0)
        setText("Alles OK")
        time.sleep(wartezeit)
    elif bool_ok == False:
        setRGB(153,0,0)
        if bool_temperatur == True: # sleep einfuegen
            if bool_warm == True:
                setText("Temperatur:\n"+print_warm)
            elif bool_kalt == True:
                setText("Temperatur:\n"+print_kalt)
            time.sleep(zeiteinheit)
        if bool_feuchtigkeit == True:  # sleep einfuegen
            if bool_nass == True:
                setText("Feuchtigkeit:\n"+print_nass)
            elif bool_trocken == True:
                setText("Feuchtigkeit\n"+print_trocken)
            time.sleep(zeiteinheit)
        if bool_helligkeit == True:
            setText("Licht:\n"+print_dunkel)
            time.sleep(zeiteinheit)
    setRGB(0,0,0)
    setText("Wartend...")

# Funktionen
# Sensordata to JSON
def toJson(sensor_value_timestamp,sensor_value_mois, sensor_value_light, sensor_value_temp, sensor_value_humi):
    data = {}
    data['Timestamp'] = sensor_value_timestamp
    data['sensor_value_moisture'] = sensor_value_mois
    data['sensor_value_light'] = sensor_value_light
    data['sensor_value_temp'] = sensor_value_temp
    data['sensor_value_humi'] = sensor_value_humi
    json_data = json.dumps(data)
    print(sensor_value_timestamp)
    
    fobj_out = open("/var/www/html/current_data.txt","w")
    fobj_out.write(json_data)
    # fobj_out.write(sensor_value_timestamp +";"+ str(sensor_value_mois) + ";" + str(bool_feuchtigkeit) +";" + str(sensor_value_light) +";"+str(bool_helligkeit)+";"+ str(sensor_value_temp) +";"+str(bool_temperatur)+ ";" + str(sensor_value_humi ))
    fobj_out.close()
    
while True:
    try:
        # Zeitstempel
        timestamp = time.strftime("%d.%m.%Y %H:%M:%S")
        print(timestamp)
        # Moisture Sensor auslesen und ausgeben
        sensor_value_mois = grovepi.analogRead(sensorMois)
        print("sensor_value_mois = %d" %(sensor_value_mois))
        # Lichtsensor auslesen und ausgeben
        sensor_value_light = grovepi.analogRead(sensorLight)
        print("sensor_value_light = %d" %(sensor_value_light))
        # DHT auslesen und ausgeben
        [temp,humidity] = grovepi.dht(sensorDHT,blue)
        if math.isnan(temp) == False and math.isnan(humidity) == False:
            print("sensor_value_temp = %.02f C sensor_value_humi = %.02f%%"%(temp, humidity))

        # Feuchtigkeit
        if sensor_value_mois > mois_max:
            print(print_nass)
            bool_nass = True
            bool_feuchtigkeit = True
            #setRGB(153,0,0)
            
        elif sensor_value_mois < mois_min:
            print(print_trocken)
            bool_trocken = True
            bool_feuchtigkeit = True
            #setRGB(153,0,0)
            
        # Licht
        if sensor_value_light < light_min:
            print(print_dunkel)
            bool_helligkeit = True
            #setRGB(153,0,0)
            
        # Temperatur
        if temp > temp_max:
            print(print_warm)
            bool_warm = True
            bool_temperatur = True
            #setRGB(128,0,0)
            
        elif temp < temp_min:
            print(print_kalt)
            bool_kalt = True
            bool_temperatur = True
            #setRGB(128,0,0)
            
        
        # pause
        if bool_feuchtigkeit == False and bool_temperatur == False and bool_temperatur == False:
            bool_ok = True
        else:
            bool_ok = False
        toJson(timestamp, sensor_value_mois, sensor_value_light, temp, humidity)    
        ausgabe_panel()
        
        time.sleep(wartezeit)

    except KeyboardInterrupt:
        break

    except IOError:
        print("Error")
    