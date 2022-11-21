import numpy, socket, time, sys
from Comunicacion_Robot import *

class ControlRobot:

    def __init__(self, ip, port):
        #Atributos
        self.TCP_SERVER_IP = ip
        self.TCP_SERVER_PORT = port
        self.TotalConnectionTries=10
        self.connectCount = 0
        self.fixedmsglenght = 1024
        #Intento de conexion
        self.connectServer()

    #metodos

    def connectServer(self):
        try:
            #Declaro el socket del server
            self.Sock = socket.socket()
            self.Sock.connect((self.TCP_SERVER_IP, self.TCP_SERVER_PORT))
            print(u'El cliente tiene la direccion IP: ' + self.TCP_SERVER_IP + ', Con puerto: ' + str(self.TCP_SERVER_PORT))
            print(self.receive_msg(17))
            self.connectCount = 0
            self.Validity_Confirmation()
        except Exception as e:
            print(e)
            self.connectCount += 1
            if self.connectCount >= self.TotalConnectionTries:
                print(u'No se pudo establecer conexion %d veces. Cerrando el cliente'%(self.connectCount))
                sys.exit()
            print(u'Intento de conexion numero {intentos} de {total}'.format(intentos=str(self.connectCount),total=str(self.TotalConnectionTries)))
            self.connectServer()

    def Validity_Confirmation(self):
        try:
            validez=self.receive_msg(self.fixedmsglenght)
            if(validez=="Valido"):
                print("El control ha seleccionado un modo valido se procede a configurar el Dobot")
                self.send_msg("Respuesta Robot: Modo valido confirmado se procede a configurar el dobot")
                self.Connect_Dobot()
            elif(validez=="Invalido"):
                print("El cliente no selecciono un modo valido cerrando el robot")
                self.send_msg("Respuesta Robot: Como el modo es invalido se cerrara el contacto con el robot")
                sys.exit()
        except Exception as e:
            print(e)

    def Connect_Dobot(self):
        #self.api=dType.load()
        Estado="Retry"
        while(Estado=="Retry"):
            #Estado_Conexion=Connect_Magician(self.api)#Esto debe ir dentro del while
            Estado_Conexion=input("Ingresa la prueba") or "DobotConnect_NoError"#Borrar
            if(Estado_Conexion=="DobotConnect_NoError"):
                self.send_msg("Dobot configurado...")
                print("He configurado el Dobot")
                break
            else:
                self.send_msg(Estado_Conexion)
            Estado=self.receive_msg(self.fixedmsglenght)
        Estado=self.receive_msg(self.fixedmsglenght)
        if(Estado=="NoMoreTries"):
            print("No fue posible conectar el dobot en los intentos definidos por el cliente")
            self.socketClose()
            self.socketOpen()
        elif(Estado=="Recibir tripletas"):
            #sys.exit()
            self.receiveTripletas()
            
            

    def receiveTripletas(self):
        print("Entre a recibir tripletas")
        try:
            while True:
                Tripleta=self.receive_msg(self.fixedmsglenght)
                print(Tripleta)
                if(Tripleta=="Disconnect"):
                    #Disconect_Magician(api)
                    print("Magician desconectado")
                    sys.exit()
                elif(Tripleta=="Reconfigurar"):
                    #Disconect_Magician(api)
                    #self.Connect_Dobot()
                    print("Dobot reconfigurado")
                    #sys.exit()
                elif(Tripleta=="pasar"):
                    pass
                else:
                    separadores=[i for i,char in enumerate(Tripleta) if char=="_"]
                    Base=float(Tripleta[separadores[0]+1:separadores[1]])
                    Brazo=float(Tripleta[separadores[1]+1:separadores[2]])
                    Antebrazo=float(Tripleta[separadores[2]+1:])
                    print(list[Base,Brazo,Antebrazo])
                    #Movimiento_Magician(api,Base,Brazo,Antebrazo)
        except Exception as e:
            print(e)
            self.socketClose()
            self.socketOpen()
    
    def receive_msg(self, lenght):
        return self.Sock.recv(lenght).decode('utf-8').rstrip()
    
    def send_msg(self, msg):
        self.Sock.sendall(msg.ljust(self.fixedmsglenght).encode('utf-8'))

def main():
    #TCP_IP = socket.gethostbyname(socket.gethostname())
    #TCP_IP='200.24.17.170'
    TCP_IP='localhost'
    TCP_PORT = 8883
    client = ControlRobot(TCP_IP, TCP_PORT)

if __name__ == "__main__":
    main()