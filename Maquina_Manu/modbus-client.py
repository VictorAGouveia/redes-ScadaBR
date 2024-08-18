# ██████╗  ██████╗ █████╗
# ██╔══██╗██╔════╝██╔══██╗
# ██║  ██║██║     ███████║
# ██║  ██║██║     ██╔══██║
# ██████╔╝╚██████╗██║  ██║
# ╚═════╝  ╚═════╝╚═╝  ╚═╝
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE, NATAL/RN
#
# (C) 2024 CARLOS M D VIEGAS
# https://github.com/cmdviegas

### Description:
# This script simulates the filling of a tank during which
# an LED lights up indicating the filling and turns off when
# emptying. It uses ModbusTCP as communcation protocol.
#### O codigo abaixo foi implementado a partir do programa base 
#### fornecido, cuja descricao original encontra-se acima.
# Aluno: Victor de Alcantara Gouveia
# Versao 0.2 - "Versao Manual"
from pyModbusTCP.client import ModbusClient
import time

# Create ModbusClient socket
client = ModbusClient(host="127.0.0.1", port=502, auto_open=True)

# Valores Iniciais
ligar_status = 0 # 0-1
ligar_datapoint = client.write_single_coil(1, ligar_status) # Indica se a maquina esta ligada

agua_status = 0 # 0-1
agua_datapoint = client.write_single_coil(2, agua_status) # Indica se ha agua suficiente

esquentar_status = 0 # 0-2
esquentar_datapoint = client.write_single_register(3, esquentar_status) # Mostra o modo do aquecedor

agua_level = 0 # 0-100
agualvl_datapoint = client.write_single_register(4, agua_level) # Mostra o nivel da agua no reservatorio

agua_temp = 20 # 20-90 --- 20 eh temperatura "ambiente", usada como valor minimo
temp_datapoint = client.write_single_register(5, agua_temp) # Mostra a temperatura da agua (em celcius)

cafe_status = 0 # 0-1
cafe_datapoint = client.write_single_coil(6, agua_status) # Indica se tem um pedido de cafe a ser feito

faz_status = 0 # 0-1
faz_datapoint = client.write_single_coil(7, faz_status) # Indica se esta fazendo um cafe - pode ser interpretado como "led do passador" ou algo assim

while True:
    # Connect modbus client to server
    client.open()
    # le se a maquina esta ligada e se tem um pedido na espera
    ligar_status = client.read_coils(1, 1)[0]
    cafe_status = client.read_coils(6, 1)[0]
    if (ligar_status and cafe_status):
        print ("Maquina Ligada! Comecando preparo do Cafe")

        time.sleep(2)
        
        if (agua_level < 50): # nem sempre vai faltar agua
            agua_status = 1 # 1 = pouca agua, 0 = agua suficiente

            print ("Tanque Insuficiente!")
            client.write_single_coil(2, agua_status)

            time.sleep(1)

            print ("Enchendo Tanque...")
            while agua_level < 100:
                print("Enchendo - Tanque = ", agua_level, " - LED Aviso = ", agua_status)

                agua_level = agua_level + 10
                client.write_single_register(4, agua_level) # Aumenta AGUA LEVEL em 5

                if (agua_level >= 50): # cada ciclo checa se ha agua suficiente, mas enche ateh completar o reservatorio
                    agua_status = 0

                client.write_single_coil(2, agua_status)

                time.sleep(1)

        if (agua_level == 100):
            print ("Tanque Cheio!")
            time.sleep(2)
        
        print ("Esquentando Agua...")
        while agua_temp < 90:
            esquentar_status = 2
            print("Esquentando - Temperatura = ", agua_temp)

            client.write_single_register(3, esquentar_status) # Esquentar = 2, "aumentar temp."

            agua_temp = agua_temp + 10

            client.write_single_register(5, agua_temp) # Aumenta AGUA TEMP em 10

            time.sleep(2)

        if (agua_temp >= 90):
            print ("Temperatura Ideal!")
            time.sleep(1)
        else:
            break
        
        print("Fazendo Cafe...")
        cafe = 0 # quantidade de cafe, apenas um valor interno pois a maquina nao detecta a quantidade de cafe na xicara, apenas sabe o quanto produziu
        while cafe < 50:
            esquentar_status = 1
            
            faz_status = 1
            client.write_single_coil(7, faz_status) # liga led de estar fazendo cafe
            print("Fazendo - Cafe = ", cafe)
            client.write_single_register(3, esquentar_status) # Esquentar = 1, "manter temp."

            agua_level = agua_level - 5
            client.write_single_register(4, agua_level) # Reduz AGUA LEVEL em 5

            cafe = cafe + 5

            time.sleep(1)
        
        print("Cafe Pronto!")

        esquentar_status = 0 # ao final nao esta esquentando nada, logo modo 0
        client.write_single_register(3, esquentar_status)

        cafe_status = 0 # pedido concluido, desliga led de pedido
        client.write_single_coil(6, cafe_status)

        faz_status = 0
        client.write_single_coil(7, faz_status) # nao esta mais fazendo cafe

        time.sleep(3)

        ## comentado pois agora fazer cafe depende de input, temperatura caira normalmente ##agua_temp = agua_temp -30 # baixa a temperatura apenas para quando retornar ao comeco
        client.write_single_register(5, agua_temp)
        ### parte abaixo comentada pois valores agora dependem de input externo
        #ligar_status = 0
        #client.write_single_coil(1, ligar_status)

    elif (ligar_status):
        print ("Maquina Ligada! Nenhum pedido")

        if (agua_level < 50): # checagem de agua apenas para avisar, nao vai encher tanque se nao houver pedido
            agua_status = 1 
            client.write_single_coil(2, agua_status)

            print ("Tanque Insuficiente!")
            
        time.sleep(2)

        if(agua_temp > 20):
            agua_temp = agua_temp -10 # baixa a temperatura da agua pois nao tem cafe sendo feito, mas apenas se acima da "ambiente"
            client.write_single_register(5, agua_temp)
    else:
        print ("Maquina Desligada!")
        agua_status = 0 # adicionado para versao manual, led desliga pois maquina esta desligada
        client.write_single_coil(2, agua_status)
        # como esse eh o unico sinal que pode chegar aqui ligado (devido montagem do codigo), apenas ele eh zerado
        time.sleep(2)

        if(agua_temp > 20):
            agua_temp = agua_temp -10 # baixa a temperatura da agua pois nao tem cafe sendo feito, mas apenas se acima da "ambiente"
            client.write_single_register(5, agua_temp)