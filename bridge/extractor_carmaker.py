import socket
import time
import sys

# ==============================================================================
# CONFIGURACIÓN CRÍTICA DEL LABORATORIO - MODIFICA ESTO AL SENTARTE AL SIMULADOR
# ==============================================================================
# 1. Dirección IP física de la máquina Linux con CARLA y puerto UDP receptor
LINUX_IP = "192.168.100.1"  # <-- SUSTITUIR POR LA IP REAL DE LA PC LINUX
UDP_PORT = 9000

# 2. Configuración del servidor de comandos de CarMaker (Loopback local)
CARMAKER_HOST = "127.0.0.1"
CARMAKER_PORT = 16660      # <-- El puerto definido en tu '-cmdport 16660'

# 3. VARIABLES UAQ (Mapeo Híbrido)
# NOTA: Si al mover el SensoWheel ves que cambia otra variable en el Data Dict,
# cambia "Senso.Ang" por el nombre exacto (ej. "Qu.Steer" o "Steer.WhlAng").
UAQ_STEER = "Senso.Ang"  # Control del usuario humano (Físico)
UAQ_GAS   = "DM.Gas"     # Control del piloto automático (Virtual)
UAQ_BRAKE = "DM.Brake"   # Control del piloto automático (Virtual)

# 4. Frecuencia de muestreo (Hz)
TICK_RATE = 100 
INTERVAL = 1.0 / TICK_RATE
# ==============================================================================

def connect_to_carmaker():
    """Establece la conexión TCP con el Command Port de la interfaz de CarMaker."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((CARMAKER_HOST, CARMAKER_PORT))
        sock.settimeout(1.0)
        # Limpiar el buffer del saludo inicial que envía el intérprete Tcl de CarMaker
        try:
            sock.recv(1024)
        except socket.timeout:
            pass
        return sock
    except Exception as e:
        print(f"[-] Error catastrófico conectando al backend de CarMaker ({CARMAKER_HOST}:{CARMAKER_PORT}): {e}")
        print("[!] Verifica que CarMaker esté abierto y que la configuración tenga la bandera '-cmdport 16660'.")
        sys.exit(1)

def get_uaq_value(cm_sock, uaq_name):
    """Consulta el valor en tiempo real de una UAQ usando el comando 'vget'."""
    try:
        # Enviamos el comando nativo de CarMaker para extraer el valor del diccionario
        cmd = f"vget {uaq_name}\n".encode('utf-8')
        cm_sock.sendall(cmd)
        
        response = cm_sock.recv(512).decode('utf-8').strip()
        
        # Filtro de contingencia por si la variable no existe aún en el ciclo actual
        if "no such variable" in response.lower() or not response:
            return 0.0
            
        return float(response)
    except ValueError:
        return 0.0
    except Exception as e:
        print(f"[-] Error de lectura en la UAQ [{uaq_name}]: {e}")
        return None

def main():
    print("[*] Inicializando Extractor SIL (CarMaker Windows -> CARLA Linux)...")
    
    # Inicializar socket UDP de transmisión hacia Linux
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Conexión al socket del backend
    print(f"[*] Intentando enganchar puerto APO TCP en {CARMAKER_HOST}:{CARMAKER_PORT}...")
    cm_sock = connect_to_carmaker()
    
    print("[+] Conexión con el backend de CarMaker establecida con éxito.")
    print(f"[+] Canal UDP abierto. Transmitiendo a {LINUX_IP}:{UDP_PORT} a {TICK_RATE}Hz.")
    print("[!] ADVERTENCIA: Ejecuta la simulación en CarMaker ANTES de lanzar este script para evitar lag.")
    print("Presiona Ctrl+C para detener de forma segura.\n")

    try:
        while True:
            start_time = time.time()
            
            # 1. Adquisición síncrona de datos desde el Data Dictionary
            steer = get_uaq_value(cm_sock, UAQ_STEER)
            gas = get_uaq_value(cm_sock, UAQ_GAS)
            brake = get_uaq_value(cm_sock, UAQ_BRAKE)
            
            # Gestión de desconexión abrupta del backend
            if steer is None or gas is None or brake is None:
                print("[-] Pérdida de comunicación con el puerto APO. Intentando reconexión...")
                cm_sock.close()
                time.sleep(1)
                cm_sock = connect_to_carmaker()
                continue

            # 2. Construcción del Payload (Formato plano de texto: "steer,gas,brake")
            # Nota: Asegúrate de comprobar en CARLA si necesitas normalizar el ángulo del SensoWheel
            payload = f"{steer},{gas},{brake}"
            
            # 3. Inyección UDP a la red física hacia la máquina Linux
            udp_sock.sendto(payload.encode('utf-8'), (LINUX_IP, UDP_PORT))
            
            # 4. Control de frecuencia estricto para mitigar el Real-time Overrun
            elapsed = time.time() - start_time
            sleep_time = INTERVAL - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # Alerta si el sistema se cuelga por encima de los 10ms asignados por ciclo
                print(f"[WARN] Ciclo de transmisión saturado. Retraso: {abs(sleep_time)*1000:.2f}ms.")

    except KeyboardInterrupt:
        print("\n[-] Extracción abortada por el usuario.")
    finally:
        cm_sock.close()
        udp_sock.close()
        print("[*] Sockets de Windows cerrados correctamente. Proceso finalizado.")

if __name__ == "__main__":
    main()