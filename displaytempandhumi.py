import time
 
from seeed_dht import DHT
from grove.display.jhd1802 import JHD1802
 
def main():
    #API KEY
    myAPI = '3164NMCLPMTI0OI1'

    baseURL = 'https://api.thingspeak.com/update?api_key=3164NMCLPMTI0OI1&field1=0' % myAPI

    # Grove - 16x2 LCD(White on Blue) connected to I2C port
    lcd = JHD1802()
 
    # Grove - Temperature&Humidity Sensor connected to port D5
    sensor = DHT('11', 5)
 
    while True:
        humi, temp = sensor.read()
        print('temperature {}C, humidity {}%'.format(temp, humi))
 
        lcd.setCursor(0, 0)
        lcd.write('temperature: {0:2}C'.format(temp))
 
        lcd.setCursor(1, 0)
        lcd.write('humidity: {0:5}%'.format(humi))

        # Sending the data to thingspeak
        conn = urllib2.urlopen(baseURL + '&field1=%s&field2=%s' % (temp, humi))
        print(conn.read())
        # Closing the connection
        conn.close()
 
        time.sleep(1)
 
if __name__ == '__main__':
    main()