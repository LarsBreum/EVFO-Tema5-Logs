# The syslog-5424 format

# Structure: <$PRI>$VER $TIMESTAMP $HOSTNAME $APPNAME $PROCID $MSGID $STRUCTURED_DATA
# PRI: priority
# VER: version (currently 1)
# TIMESTAMP: timestamp in the format: YYYY  -MM-DD<T>HH:MM:SS.sssss+ZZ:ZZ
# HOSTNAME: Fully qualified domain name (FQND, IP, hostname or nil)
# APPNAME: Should identify the device or application
# PROCID: Process ID. is often nil. Not required but often used to identify discontinuities
# MSGGID: Type of message. Example: TCPIN
# STRUCTURED_DATA: If no data: nil. Otherwise a field used for metadata

'''
FORMATOS:

BASTION: timestamp host proceso[ID proceso]: mensaje
BLUECOAT: Timestamp (delay) proceso Structured data
hnet-hon: timestamp hostname aplicacion mensaje 
'''

path_entrada = "logs/input/log.txt"
path_salida = "logs/output/log.txt"

lista_logs_salida=[]
lista_logs_salida_ordenados=[]


def detectar_formato(linea):
    #procesa la linea para encontrar el formato
    if linea[:4].isdigit():
        print(f"{linea} es dragon")
        return "dragon"
    if linea[0] == "<":
        print(f"{linea} es rfc5424")
        return "rfc5424"
    else:
        print(f"{linea} ninguno de los anteriores")
        return False
    

def transformar_log(linea, formato):
    #transforma en formato syslog-RFC5424
    if formato == dragon:
        lista_logs_salida.add(linea)
    
def ordenar_logs():
    return True
    #ordena temporalmente
    
def escribir_salida():
    try:
        with open(path_salida, "w") as archivo:
            for linea in lista_logs_salida_ordenados:
                archivo.write(linea + "\n")  
        print(f"Se ha escrito correctamente el contenido en '{path_salida}'")
    except Exception as e:
        print(f"Ocurrió un error al escribir el archivo: {e}")
    

try:
    with open(path_entrada, "r") as archivo:
        for linea in archivo:
            # Process line
            if(linea != ""):
                detectar_formato(linea)
                #lista_logs_salida.add(transformar_log(linea, detectar_formato(linea)))
                print(lista_logs_salida) 
except FileNotFoundError:
    print(f"No se pudo encontrar el archivo '{path_entrada}'")
except Exception as e:
    print(f"Ocurrió un error: {e}")
    
#ordenar_logs()   
#escribir_salida()
    



