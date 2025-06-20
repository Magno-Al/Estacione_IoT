# main.py
import time
import cv2
import re
from picamera2 import Picamera2, Preview, MappedArray
from libcamera import controls

from modules import ocr_reader, api_client, hardware_control, sensor_reader
import config

def is_valid_plate_format(plate_text):
    """Valida o formato da placa."""
    pattern_old = re.compile(r"^[A-Z]{3}\d{4}$")
    pattern_mercosul = re.compile(r"^[A-Z]{3}\d[A-Z]\d{2}$")
    return bool(pattern_old.match(plate_text) or pattern_mercosul.match(plate_text))

def draw_roi_overlay(request):
    """Desenha o retângulo de ROI no preview."""
    with MappedArray(request, "main") as m:
        colour = (0, 255, 0)
        cv2.rectangle(m.array, (config.ROI_X, config.ROI_Y), (config.ROI_X + config.ROI_WIDTH, config.ROI_Y + config.ROI_HEIGHT), colour, 2)

def process_vehicle_event(picam2):
    """
    Executa a leitura e a lógica da API.
    Retorna True se a passagem foi liberada, False caso contrário.
    """
    print("\n--- Veículo Detectado! Iniciando processamento ---")
    
    ocr_frame = picam2.capture_array()
    roi_image = ocr_frame[config.ROI_Y:config.ROI_Y + config.ROI_HEIGHT, config.ROI_X:config.ROI_X + config.ROI_WIDTH]
    plate_text, processed_image = ocr_reader.perform_ocr(roi_image)
    display_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
    
    result_message = ""
    text_color = (0, 0, 255) # Vermelho (Falha) por padrão
    access_granted = False # Começa como falso

    if is_valid_plate_format(plate_text):
        print(f"Placa válida lida: {plate_text}. Consultando API...")
        if not api_client.check_customer_by_plate(plate_text):
            result_message = f"NEGADO: Nao Cadastrado"
            hardware_control.set_gate_closed()
        else:
            print(f"API -> OK: Cliente cadastrado.")
            active_service = api_client.get_active_service(plate_text)
            if active_service is None: # Lógica de ENTRADA
                if api_client.record_entry(plate_text):
                    result_message = f"ENTRADA OK: {plate_text}"
                    text_color = (0, 255, 0)
                    hardware_control.set_gate_open()
                    access_granted = True
                else:
                    result_message = "FALHA: Erro na API"
                    hardware_control.set_gate_closed()
            else: # Lógica de SAÍDA
                is_paid = active_service.get('updated_record', {}).get('is_paid', False)
                if is_paid:
                    if api_client.finalize_exit(plate_text):
                        result_message = f"SAIDA OK: {plate_text}"
                        text_color = (0, 255, 0)
                        hardware_control.set_gate_open()
                        access_granted = True
                else:
                    fee = active_service.get('calculated_fee', 0)
                    result_message = f"FALHA: Pgmto Pendente"
                    print(f"API -> NEGADO: Pagamento pendente. Valor: R$ {fee:.2f}")
                    hardware_control.set_gate_closed()
    else:
        result_message = f"FALHA (Lido: '{plate_text}')"
        hardware_control.set_gate_closed()
    
    # --- AQUI ESTÁ A MUDANÇA ---
    # A janela de resultado agora é exibida IMEDIATAMENTE após a decisão.
    print(f"Resultado final do processamento: {result_message}")
    cv2.putText(display_image, result_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
    cv2.imshow("Resultado do OCR", display_image)
    cv2.waitKey(1) # Essencial para a janela ser desenhada na tela

    return access_granted

def initialize_camera():
    """Configura e inicia a câmera com o preview."""
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
    hardware_control.setup()
    picam2 = initialize_camera()
    is_vehicle_present = False
    
    print("\n--- Sistema de Estacionamento ATIVADO ---")
    print("Aguardando detecção de veículo pelo sensor...")
    
    try:
        while True:
            distance = sensor_reader.get_distance_cm()
            
            if distance <= 15 and not is_vehicle_present:
                is_vehicle_present = True
                
                # A função de processamento agora retorna se o acesso foi liberado
                access_was_granted = process_vehicle_event(picam2)
                
                # A lógica de espera agora fica no loop principal
                if access_was_granted:
                    print("Aguardando o veículo passar pela cancela...")
                    while sensor_reader.get_distance_cm() <= 15:
                        time.sleep(0.2)
                    
                    print("Veículo passou! A passagem fechará em 3 segundos...")
                    time.sleep(3)
                    hardware_control.set_gate_closed()
                
                print("\nCiclo finalizado. Sistema pronto para nova detecção.")

            # Reseta o status se o carro sair sem ter acionado o ciclo
            elif distance > 15 and is_vehicle_present:
                is_vehicle_present = False

            time.sleep(0.1)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")
    finally:
        hardware_control.cleanup()
        picam2.stop_preview()
        picam2.stop()
        cv2.destroyAllWindows()
        print("Recursos liberados.")

if __name__ == '__main__':
    main()