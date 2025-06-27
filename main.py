import time
import cv2
import re
import json
from picamera2 import Picamera2, Preview, MappedArray
from libcamera import controls

from modules import ocr_reader, api_client, hardware_control, sensor_reader, mqtt_client
import config

system_mode = 'AUTOMATIC'

def on_mqtt_message(client, userdata, msg):
    global system_mode
    
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())

        if topic == "parking/command/system" and "mode" in payload:
            new_mode = payload["mode"].upper()
            if new_mode in ['AUTOMATIC', 'MANUAL']:
                if system_mode != new_mode:
                    system_mode = new_mode
                    print(f"\nSISTEMA: Modo alterado para {system_mode}")
                    mqtt_client.publish(client, "system", {"mode": system_mode})
                    if system_mode == 'MANUAL':
                        hardware_control.set_gate_closed()

        elif topic == "parking/command/hardware" and "action" in payload:
            if system_mode == 'MANUAL':
                action = payload["action"].upper()
                print(f"Recebido comando manual: {action}")
                if action == "OPEN_GATE":
                    hardware_control.set_gate_open()
                elif action == "CLOSE_GATE":
                    hardware_control.set_gate_closed()
            else:
                print("AVISO: Comando manual de hardware ignorado. O sistema está em modo AUTOMÁTICO.")
        
        elif topic == "parking/command/camera" and "component" in payload:
            if system_mode == 'MANUAL':
                component = payload.get("component")
                angle = payload.get("angle")
                print(f"Recebido comando manual de câmera: Mover {component} para o ângulo {angle}")
                if component == "servo_tilt":
                    hardware_control.move_servo_slowly(hardware_control.tilt_servo, angle)
            else:
                print("AVISO: Comando manual de câmera ignorado. O sistema está em modo AUTOMÁTICO.")
        
    except Exception as e:
        print(f"Erro ao processar mensagem MQTT: {e}")

def is_valid_plate_format(plate_text):
    pattern_old = re.compile(r"^[A-Z]{3}\d{4}$")
    pattern_mercosul = re.compile(r"^[A-Z]{3}\d[A-Z]\d{2}$")
    return bool(pattern_old.match(plate_text) or pattern_mercosul.match(plate_text))

def draw_roi_overlay(request):
    with MappedArray(request, "main") as m:
        colour = (0, 255, 0)
        cv2.rectangle(m.array, (config.ROI_X, config.ROI_Y), (config.ROI_X + config.ROI_WIDTH, config.ROI_Y + config.ROI_HEIGHT), colour, 2)

def process_vehicle_event(picam2, mqtt_client_instance):
    print("\n--- Veículo Detectado! Iniciando processamento ---")
    
    ocr_frame = picam2.capture_array()
    roi_image = ocr_frame[config.ROI_Y:config.ROI_Y + config.ROI_HEIGHT, config.ROI_X:config.ROI_X + config.ROI_WIDTH]
    plate_text, processed_image = ocr_reader.perform_ocr(roi_image)
    display_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
    
    result_message = ""
    text_color = (0, 0, 255)
    access_granted = False

    if is_valid_plate_format(plate_text):
        print(f"Placa válida lida: {plate_text}. Consultando API...")
        if not api_client.check_customer_by_plate(plate_text):
            result_message = f"NEGADO: Nao Cadastrado"
            hardware_control.set_gate_closed()
        else:
            print(f"API -> OK: Cliente cadastrado.")
            active_service = api_client.get_active_service(plate_text)
            if active_service is None:
                print(f"API -> Ação: REGISTRAR ENTRADA...")
                if api_client.record_entry(plate_text):
                    result_message = f"ENTRADA OK: {plate_text}"
                    text_color = (0, 255, 0)
                    access_granted = True
                else:
                    result_message = "FALHA: Erro na API"
                    hardware_control.set_gate_closed()
            else:
                is_paid = active_service.get('updated_record', {}).get('is_paid', False)
                if is_paid:
                    print(f"API -> Ação: PROCESSAR SAÍDA...")
                    if api_client.finalize_exit(plate_text):
                        result_message = f"SAIDA OK: {plate_text}"
                        text_color = (0, 255, 0)
                        access_granted = True
                else:
                    fee = active_service.get('calculated_fee', 0)
                    result_message = f"FALHA: Pgmto Pendente"
                    print(f"API -> NEGADO: Pagamento pendente. Valor: R$ {fee:.2f}")
                    hardware_control.set_gate_closed()
    else:
        result_message = f"FALHA (Lido: '{plate_text}')"
        hardware_control.set_gate_closed()

    print(f"Resultado final do processamento: {result_message}")
    if access_granted:
        mqtt_client.publish(mqtt_client_instance, "gate", {"status": "OPEN", "reason": "auto"})
        mqtt_client.publish(mqtt_client_instance, "last_event", {"plate": plate_text, "result": "Access Granted"})
    else:
        mqtt_client.publish(mqtt_client_instance, "gate", {"status": "BLOCKED", "reason": result_message})
        mqtt_client.publish(mqtt_client_instance, "last_event", {"plate": plate_text, "result": "Access Denied"})

    cv2.putText(display_image, result_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
    cv2.imshow("Resultado do OCR", display_image)
    cv2.waitKey(1)

    return access_granted

def initialize_camera():
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration(main={"size": (config.IMG_WIDTH, config.IMG_HEIGHT)})
    picam2.configure(preview_config)
    picam2.start_preview(Preview.QTGL) 
    picam2.post_callback = draw_roi_overlay
    picam2.start()
    time.sleep(2)
    print("Câmera e preview inicializados.")
    return picam2

def main():
    global system_mode
    hardware_control.setup()
    picam2 = initialize_camera()
    mqtt = mqtt_client.get_client(on_mqtt_message)
    is_vehicle_present = False
    
    print(f"\n--- Sistema de Estacionamento ATIVADO | Modo Inicial: {system_mode} ---")
    
    try:
        while True:
            if system_mode == 'AUTOMATIC':
                distance = sensor_reader.get_distance_cm()
                mqtt_client.publish(mqtt, "sensor", {"distance_cm": round(distance, 2)})

                if distance <= 15 and not is_vehicle_present:
                    is_vehicle_present = True
                    access_was_granted = process_vehicle_event(picam2, mqtt)
                    
                    if access_was_granted:
                        hardware_control.set_gate_open()
                        print("Aguardando o veículo passar pela cancela...")
                        while sensor_reader.get_distance_cm() <= 15:
                            time.sleep(0.2)
                        print("Veículo passou! A passagem fechará...")
                        hardware_control.set_gate_closed()
                        mqtt_client.publish(mqtt, "gate", {"status": "CLOSED"})
                    
                    print("\nCiclo automático finalizado. Sistema pronto para nova detecção.")
                
                elif distance > 15 and is_vehicle_present:
                    is_vehicle_present = False

            time.sleep(0.1)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")
    finally:
        if mqtt:
            mqtt.loop_stop()
        hardware_control.cleanup()
        picam2.stop_preview()
        picam2.stop()
        cv2.destroyAllWindows()
        print("Recursos liberados.")

if __name__ == '__main__':
    main()
