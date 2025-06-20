# modules/hardware_control.py
import RPi.GPIO as GPIO
import config

def setup():
    """Configura os pinos da GPIO."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(config.LED_GREEN_PIN, GPIO.OUT)
    GPIO.setup(config.LED_RED_PIN, GPIO.OUT)
    print("MÓDULO HARDWARE: GPIO configurada.")
    set_gate_closed() # Garante o estado inicial "fechado"

def set_gate_open():
    """APENAS define o estado da passagem como ABERTA (LED verde aceso)."""
    print("HARDWARE: Passagem liberada (LED Verde LIGADO).")
    GPIO.output(config.LED_RED_PIN, GPIO.LOW)
    GPIO.output(config.LED_GREEN_PIN, GPIO.HIGH)
    # Futuramente, aqui você acionaria o motor da cancela

def set_gate_closed():
    """APENAS define o estado da passagem como FECHADA (LED vermelho aceso)."""
    print("HARDWARE: Passagem bloqueada/fechada (LED Vermelho LIGADO).")
    GPIO.output(config.LED_GREEN_PIN, GPIO.LOW)
    GPIO.output(config.LED_RED_PIN, GPIO.HIGH)

def cleanup():
    """Limpa a configuração da GPIO."""
    print("MÓDULO HARDWARE: Limpando GPIO...")
    GPIO.cleanup()