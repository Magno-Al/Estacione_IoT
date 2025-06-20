# modules/hardware_control.py
# import RPi.GPIO as GPIO # Comentado para teste sem hardware
import time
import config

def setup():
    """Configura o módulo de hardware para o modo de simulação."""
    print("MÓDULO HARDWARE: Modo de simulação ativado (sem controle de GPIO).")

def open_gate():
    """Simula a ação de abrir a cancela."""
    print("SIMULAÇÃO HARDWARE: Abrindo cancela...")
    print("SIMULAÇÃO HARDWARE: LED Verde LIGADO / LED Vermelho DESLIGADO")
    time.sleep(1) # Simula um tempo para a ação ocorrer
    print("SIMULAÇÃO HARDWARE: Cancela estaria aberta.")

def close_gate():
    """Simula a ação de fechar a cancela."""
    print("SIMULAÇÃO HARDWARE: Fechando cancela...")
    print("SIMULAÇÃO HARDWARE: LED Verde DESLIGADO / LED Vermelho LIGADO")

def block_passage():
    """Simula a ação de bloquear a passagem."""
    print("SIMULAÇÃO HARDWARE: Passagem bloqueada (LED Vermelho LIGADO).")

def cleanup():
    """Simula a limpeza dos recursos da GPIO."""
    print("MÓDULO HARDWARE: Simulação de limpeza da GPIO finalizada.")