# modules/mqtt_client.py
import paho.mqtt.client as mqtt
import config
import json
from modules import hardware_control

def on_message(client, userdata, msg):
    print(f"Comando MQTT recebido no tópico '{msg.topic}': {msg.payload.decode()}")
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        import main # Para acesso à variável de modo

        if topic == "parking/command/system" and "mode" in payload:
            # Lógica de troca de modo (sem alterações)
            new_mode = payload["mode"].upper()
            if new_mode in ['AUTOMATIC', 'MANUAL'] and main.system_mode != new_mode:
                main.system_mode = new_mode
                print(f"\nSISTEMA: Modo alterado para {main.system_mode}")
                publish(client, "system", {"mode": main.system_mode})
                if main.system_mode == 'MANUAL':
                    hardware_control.set_gate_closed()

        elif topic == "parking/command/hardware" and main.system_mode == 'MANUAL':
            # Lógica de hardware (sem alterações)
            if "action" in payload:
                action = payload["action"].upper()
                if action == "OPEN_GATE": hardware_control.set_gate_open()
                elif action == "CLOSE_GATE": hardware_control.set_gate_closed()

        elif topic == "parking/command/camera" and main.system_mode == 'MANUAL':
            component = payload.get("component")
            angle = payload.get("angle")
            print(f"'{component}': {angle}")

            if component is not None and angle is not None:
                if component == "servo_tilt":
                    print(f"Recebido comando manual de câmera: Mover TILT para o ângulo {angle}")
                    hardware_control.move_servo_slowly(hardware_control.tilt_servo, angle)
                    
    except Exception as e:
        print(f"Erro ao processar mensagem MQTT: {e}")

# ... (as funções get_client e publish continuam as mesmas) ...
def get_client(on_message_callback):
    client = mqtt.Client("rpi_parking_client")
    client.on_message = on_message_callback
    try:
        client.connect(config.MQTT_BROKER_ADDRESS, config.MQTT_PORT, 60)
        client.subscribe("parking/command/#")
        client.loop_start()
        print(f"Conectado ao MQTT Broker em {config.MQTT_BROKER_ADDRESS}")
        return client
    except Exception as e:
        print(f"ERRO: Não foi possível conectar ao MQTT Broker: {e}")
        return None

def publish(client, topic_suffix, payload_dict):
    if not client: return
    topic = f"parking/status/{topic_suffix}"
    payload_str = json.dumps(payload_dict)
    client.publish(topic, payload_str)
