import cv2
import pytesseract
import time
import re
from picamera2 import Picamera2, Preview, MappedArray
from libcamera import controls

# Importa nossos módulos customizados
from modules import ocr_reader, api_client, hardware_control
import config

def is_valid_plate_format(plate_text):
    """Valida o formato da placa (antigo ou Mercosul)."""
    pattern_old = re.compile(r"^[A-Z]{3}\d{4}$")
    pattern_mercosul = re.compile(r"^[A-Z]{3}\d[A-Z]\d{2}$")
    return bool(pattern_old.match(plate_text) or pattern_mercosul.match(plate_text))

def draw_roi_overlay(request):
    """Função de callback para desenhar o retângulo de ROI no preview da câmera."""
    with MappedArray(request, "main") as m:
        colour = (0, 255, 0)
        cv2.rectangle(m.array, (config.ROI_X, config.ROI_Y), (config.ROI_X + config.ROI_WIDTH, config.ROI_Y + config.ROI_HEIGHT), colour, 2)

def main():
    # --- INICIALIZAÇÃO DA CÂMERA E MÓDULOS ---
    hardware_control.setup()
    
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration(main={"size": (config.IMG_WIDTH, config.IMG_HEIGHT)})
    picam2.configure(preview_config)
    picam2.start_preview(Preview.QTGL)
    picam2.post_callback = draw_roi_overlay
    picam2.start()
    time.sleep(2)
    print("Câmera inicializada.")
    
    print("\n--- Sistema de Leitura e Integração de Estacionamento ---")
    print("Na janela de preview, posicione a placa do veículo dentro do retângulo.")
    
    try:
        while True:
            # --- LOOP PRINCIPAL AGUARDANDO COMANDO ---
            print("\nAguardando comando ('r' para ler, 'q' para sair):")
            user_input = input().lower()

            if user_input == 'q':
                break
            
            if user_input == 'r':
                print("Capturando foto e iniciando fluxo...")
                
                ocr_frame = picam2.capture_array()
                # ... (resto da lógica de captura e processamento da imagem) ...
                plate_text, processed_image = ocr_reader.perform_ocr(ocr_frame[config.ROI_Y:config.ROI_Y + config.ROI_HEIGHT, config.ROI_X:config.ROI_X + config.ROI_WIDTH])
                display_image = cv2.cvtColor(processed_image, cv2.COLOR_GRAY2BGR)
                result_message = ""
                text_color = (0, 0, 255)

                if is_valid_plate_format(plate_text):
                    print(f"Placa com formato válido lida: {plate_text}. Consultando API...")

                    if not api_client.check_customer_by_plate(plate_text):
                        result_message = f"NEGADO: Nao Cadastrado"
                        print(f"API -> {result_message}")
                        hardware_control.block_passage()
                    else:
                        print(f"API -> OK: Cliente cadastrado para a placa {plate_text}.")
                        active_service = api_client.get_active_service(plate_text)

                        if active_service is None:
                            # Lógica de ENTRADA (permanece a mesma)
                            print(f"API -> Ação: REGISTRAR ENTRADA para {plate_text}...")
                            if api_client.record_entry(plate_text):
                                result_message = f"ENTRADA OK: {plate_text}"
                                text_color = (0, 255, 0)
                                print("API -> SUCESSO: Entrada registrada.")
                                hardware_control.open_gate()
                            else:
                                result_message = "FALHA: Erro na API"
                                print("API -> ERRO: Falha ao registrar entrada.")
                                hardware_control.block_passage()
                        else:
                            # Lógica de SAÍDA (com a nova chamada)
                            print(f"API -> Ação: PROCESSAR SAÍDA para {plate_text}...")
                            is_paid_status = active_service.get('updated_record', {}).get('is_paid', False)
                            if is_paid_status:
                                result_message = f"SAIDA OK: {plate_text}"
                                text_color = (0, 255, 0)
                                print("API -> OK: Pagamento confirmado.")
                                hardware_control.open_gate()

                                # *** AQUI ESTÁ A NOVA CHAMADA ***
                                print("Finalizando serviço na API...")
                                if api_client.finalize_exit(plate_text):
                                    print("API -> SUCESSO: Serviço finalizado no banco de dados.")
                                else:
                                    # Alerta importante: a cancela abriu mas o registro não foi finalizado.
                                    # Isso pode exigir uma verificação manual ou um log de erros.
                                    print("API -> ALERTA: Cancela aberta, mas houve falha ao finalizar o serviço na API.")
                                # *** FIM DA NOVA CHAMADA ***

                            else:
                                fee = active_service.get('calculated_fee', 0)
                                result_message = f"FALHA: Pgmto Pendente"
                                print(f"API -> NEGADO: Pagamento pendente. Valor: R$ {fee:.2f}")
                                hardware_control.block_passage()
                else:
                    result_message = f"FALHA (Lido: '{plate_text}')"
                    print(f"Resultado do OCR inválido.")
                    hardware_control.block_passage()

                cv2.putText(display_image, result_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
                cv2.imshow("Resultado do OCR", display_image)
            
            else:
                print("Comando inválido.")

            cv2.waitKey(1)

    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")
    finally:
        print("Encerrando o programa e a câmera...")
        hardware_control.cleanup()
        picam2.stop_preview()
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    # É necessário adicionar as definições das funções que estão no main para que ele possa ser executado
    def is_valid_plate_format(plate_text):
        """Valida o formato da placa (antigo ou Mercosul)."""
        pattern_old = re.compile(r"^[A-Z]{3}\d{4}$")
        pattern_mercosul = re.compile(r"^[A-Z]{3}\d[A-Z]\d{2}$")
        return bool(pattern_old.match(plate_text) or pattern_mercosul.match(plate_text))

    def draw_roi_overlay(request):
        """Função de callback para desenhar o retângulo de ROI no preview da câmera."""
        with MappedArray(request, "main") as m:
            colour = (0, 255, 0)
            cv2.rectangle(m.array, (config.ROI_X, config.ROI_Y), (config.ROI_X + config.ROI_WIDTH, config.ROI_Y + config.ROI_HEIGHT), colour, 2)
    main()