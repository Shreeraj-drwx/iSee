
import time
 
from seeed_dht import DHT
from grove.display.jhd1802 import JHD1802
from upm import pyupm_buzzer as upmBuzzer


 
def main():

	# Grove - Temperature&Humidity Sensor connected to port D5
    sensor = DHT('11', 5)

	part_type = input('What body part is being stored in your controlled ice-box , options : kidney, heart,   \n')


	if part_type == 'kidney':
		threshold_lower = 4
		threshold_higher = 8
		t = 36
	elif part_type == 'heart':
		threshold_lower = 4
		threshold_higher = 8
		t = 6
	elif part_type == 'lungs':
		threshold_lower = 4
		threshold_higher = 10
		t = 4

	while True:
		humi,temp = sensor.read()

		if temp <= threshold_higher and temp >= threshold_lower:
			conditon = 'stable'
		#-2 and +2 done to have the temperatue 2 C above and below good temperature
		elif temp <= threshold_higher + 2 and temp >= threshold_lower - 2:
			condition = 'slighly unstable'
		else:
			condition = 'servely unstable'
			
			while conditon == 'serverly unstable':
				buzzer = upmBuzzer.Buzzer(getGpioLookup('GPIO12'))
 
			    CHORDS = [upmBuzzer.BUZZER_DO, upmBuzzer.BUZZER_RE, upmBuzzer.BUZZER_MI, 
			        upmBuzzer.BUZZER_FA, upmBuzzer.BUZZER_SOL, upmBuzzer.BUZZER_LA, 
			        upmBuzzer.BUZZER_SI]
			    for i in range(0, len(CHORDS)):
			        buzzer.playSound(CHORDS[i], 500000)
			        time.sleep(0.1)
 
if __name__ == '__main__':
    main()
