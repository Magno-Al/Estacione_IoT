import RPi.GPIO as GPIO
import config
from gpiozero import Servo
from time import sleep

#pan_servo = None
tilt_servo = None

def setup():
    """Configura os pinos da GPIO."""
    global tilt_servo #, pan_servo
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(config.LED_GREEN_PIN, GPIO.OUT)
    GPIO.setup(config.LED_RED_PIN, GPIO.OUT)
    
    #pan_servo = Servo(config.SERVO_PAN_PIN)
    tilt_servo = Servo(config.SERVO_TILT_PIN)
    
    #pan_servo.mid()
    tilt_servo.mid()
    
    print("MÓDULO HARDWARE: GPIO configurada.")
    set_gate_closed() # Garante o estado inicial "fechado"

def move_servo_slowly(servo, target_angle):
    """Move um servo gradualmente para o ângulo desejado para proteger o cabo."""
    if not servo:
        return
        
    target_value = (target_angle / 90.0) - 1.0
    target_value = max(-1, min(1, target_value))

    current_value = servo.value if servo.value is not None else 0
    
    step = 0.02 
    if current_value > target_value:
        step = -step

    for value in range(int(current_value * 100), int(target_value * 100), int(step * 100)):
        servo.value = value / 100.0
        sleep(0.01)
    
    servo.value = target_value

def set_gate_open():
    """APENAS define o estado da passagem como ABERTA (LED verde aceso)."""
    print("HARDWARE: Passagem liberada (LED Verde LIGADO).")
    GPIO.output(config.LED_RED_PIN, GPIO.LOW)
    GPIO.output(config.LED_GREEN_PIN, GPIO.HIGH)

def set_gate_closed():
    """APENAS define o estado da passagem como FECHADA (LED vermelho aceso)."""
    print("HARDWARE: Passagem bloqueada/fechada (LED Vermelho LIGADO).")
    GPIO.output(config.LED_GREEN_PIN, GPIO.LOW)
    GPIO.output(config.LED_RED_PIN, GPIO.HIGH)

def cleanup():
    """Limpa a configuração da GPIO."""
    print("MÓDULO HARDWARE: Limpando GPIO...")
    if tilt_servo:
        tilt_servo.detach()
    GPIO.cleanup()
