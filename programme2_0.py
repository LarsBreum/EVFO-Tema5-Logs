import re 
from datetime import datetime

# The syslog-5424 format

# Structure: <$PRI>$VER $TIMESTAMP $HOSTNAME $APPNAME $PROCID $MSGID $STRUCTURED_DATA
# PRI: priority
# VER: version (currently 1)
# TIMESTAMP: timestamp in the format: YYYY-MM-DD<T>HH:MM:SS.sssss+ZZ:ZZ
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

#directorios
path_entrada = "logs/input/logs.txt"
path_salida = "logs/output/logs.txt"
path_salida_desconocida = "logs/output/logs_desconocidos.txt"

#listas
logs_desconocidos = []
logs_salida=[]
logs_salida_ordenados=[]

#patrones
patron_bastion = r'(\w{3}\s\d{1,2}\s\d{2}:\d{2}:\d{2}) (\w+) (\w+)(?:\[(\d+)\])?: (.*)'
#patron_mta = r'^(\w{3}\s+\d{1,2}\s\d{2}:\d{2}:\d{2})\s(\w+)\s(\w+)\[(\d+)\]:\s(\w+):.*to=<(.*?)>,\sctladdr=<(.*?)>\s\(\d+/\d+\),\sdelay=([\d:]+),\sxdelay=([\d:]+),\smailer=(\w+),\spri=(\d+),\sdsn=(\d\.\d\.\d),\sstat=(\w+)$'
patron_mailman = r'([A-Z][a-z]{2} \d{1,2}) (\d{2}:\d{2}:\d{2}) (\d{4}) ([a-zA-Z0-9]+\(\d+\)): (.+)'

# transform date_time for logs that does not include a year
def transformar_time(date_time):
    meses_abreviados = {'Ene': "01",'Feb': "02",'Mar': "03",'Abr': "04",'May': "05",'Jun': "06",'Jul': "07", 'Ago': "08",'Sep': "09",'Oct': "10",'Nov': "11",'Dic': "12"}
    mes, dia, hora = date_time.split()
    return f"*-{meses_abreviados.get(mes)}-{dia}T{hora}"

# transdorm date_time for logs that includes the yeay
def transformar_time_w_year(date_time):
    meses_abreviados = {'Ene': "01",'Feb': "02",'Mar': "03",'Abr': "04",'May': "05",'Jun': "06",'Jul': "07", 'Ago': "08",'Sep': "09",'Oct': "10",'Nov': "11",'Dic': "12"}
    mes, dia, hora = date_time.split()
    return f"{meses_abreviados.get(mes)}-{dia}T{hora}"


def transformar(linea):
    #procesa la linea para encontrar el formato
    matches = re.match(patron_bastion, linea)
    if matches:
        print(f"{linea} es bastion")
        date_time = matches.group(1)
        host = matches.group(2)
        program = matches.group(3)
        process_id = matches.group(4)
        if process_id== None: process_id='*'
        message = matches.group(5)
        log=f"<*>1 {transformar_time(date_time)} {host} {program} {process_id} * [] {message}"
        return True, log
    
    isDragon = linea[:4].isdigit()
    if isDragon:
        print(f"{linea} es dragon")
        matches = re.findall(r"([^|]+)", linea) # returns a list of groups seperated by the pipe charecter
        date_time = matches[0] + "T" + matches[1]
        host = f"{matches[3]}:{matches[5]}"
        program = matches[4]
        process_id = "*"
        message = matches[9]
        log=f"<*>1 {date_time} {host} {program} {process_id} * [] {message}"
        return True, log
    
    if "mailman" in linea:
        print(f"{linea} es mailman")
        mailman = re.match(patron_mailman, linea)
        year = mailman.group(3)
        date = transformar_time_w_year(mailman.group(1) + " " + mailman.group(2))
        date_time = f"{year}-{date}"
        program = mailman.group(4)
        host = mailman.group(4)
        process_id = "*"
        message = mailman.group(5)

        log=f"<*>1 {date_time} {host} {program} {process_id} * [] {message}"
        print(log)
        return True, log
        
    
    # match = re.match(patron_mta, linea)
    # if match:
    #     print("es MTA")
    
    if linea[0]=="<":
       return True, log
    else: #ningún patron conocidodate_time
        return False, linea   
    
def extraer_fecha_hora(log):
    # Extraer la fecha y hora de la cadena de registro
    time = log[log.find(" ")+1:log.find(" ", log.find(" ")+1)]
    partes = time.split('T')
    fecha = partes[0].split('-')
    tiempo = partes[1].split(':')
    
    # Convertir a números enteros
    try: año = int(fecha[0]) 
    except: año = 3000# Si no hay año, asigna 0
    mes = int(fecha[1])
    dia = int(fecha[2])
    hora = int(tiempo[0])
    minutos = int(tiempo[1])
    segundos = int(tiempo[2])
    
    return datetime(año, mes, dia, hora, minutos, segundos)
    
def ordenar_logs():
    # Ordenar los registros de log cronológicamente
    return sorted(logs_salida, key=extraer_fecha_hora)
    
def escribir_salida():
    try:
        with open(path_salida, "w") as archivo:
            for linea in logs_salida_ordenados:
                archivo.write(linea + "\n")  
        print(f"Se ha escrito correctamente el contenido en '{path_salida}'")
    except Exception as e:
        print(f"Ocurrió un error al escribir el archivo: {e}")
    try:
        with open(path_salida_desconocida, "w") as archivo:
            for linea in logs_desconocidos:
                archivo.write(linea + "\n")  
        print(f"Se ha escrito correctamente el contenido en '{path_salida_desconocida}'")
    except Exception as e:
        print(f"Ocurrió un error al escribir el archivo: {e}")
    

try:
    with open(path_entrada, "r") as archivo:
        for linea in archivo:
            # Process line
            if(linea != ""):
                conocido, log = transformar(linea)
                if conocido:
                    logs_salida.append(log)
                else:
                    logs_desconocidos.append(log)
except FileNotFoundError:
    print(f"No se pudo encontrar el archivo '{path_entrada}'")
except Exception as e:
    print(f"Ocurrió un error: {e}")
# print("LOGS SALIDA:")  
# print(logs_salida) 
# print("LOGS desconocdios:")  
# print(logs_desconocidos) 
logs_salida_ordenados = ordenar_logs() 
#print("LOGS ordenados:") 
#print(logs_salida_ordenados)  
escribir_salida()
    



