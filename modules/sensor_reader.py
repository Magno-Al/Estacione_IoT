# modules/sensor_reader.py
from gpiozero import DistanceSensor
# --- ADICIONE ESTAS 3 LINHAS PARA MELHORAR A PRECISÃO ---
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Device
Device.pin_factory = PiGPIOFactory()
# --- FIM DA ADIÇÃO ---
import config

sensor = DistanceSensor(echo=config.SENSOR_ECHO_PIN, trigger=config.SENSOR_TRIGGER_PIN)

def get_distance_cm():
    """Retorna a distância medida pelo sensor em centímetros."""
    return sensor.distance * 100