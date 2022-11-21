import numpy, socket, time, threading,sys,traceback

class Server:

    def __init__(self, ip, port):
        #Atributos de la clase
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.fixedmsglenght = 1024
        self.Connections=[]#Siempre debe conectarse primero el control
        self.socketOpen()

    #metodos

    #Cerrar el socket
    def socketClose(self):
        self.sock.close()
        print(u'Se cerro el server con parametros [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ]')

    #Abrir el socket
    def socketOpen(self):
        #creamos el socket y lo asociamos a un dispositivo fisico
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.TCP_IP, self.TCP_PORT))
        #Esperamos a un cliente
        self.sock.listen()
        print(u'Se ha abierto el socket con parametros [ TCP_IP: ' + self.TCP_IP + ', TCP_PORT: ' + str(self.TCP_PORT) + ' ]')
        self.receiveConnections()

    def receiveConnections(self):
        try:
            for i in range(2):
                Cliente, Direccion = self.sock.accept()
                self.Connections.append(Cliente)
                Cliente.sendall("Conexion aceptada".encode('utf-8'))
                print(f'El server esta conectado con el cliente de ip {Direccion[0]} y puerto {Direccion[1]}')
                Thread=threading.Thread(target=self.handlemsg, args=(Cliente,))
                Thread.start()
        except Exception as e:
            print(e)
            self.socketClose()
            self.socketOpen()

    def handlemsg(self,Cliente):
        while True:
            try:
                msg=Cliente.recv(self.fixedmsglenght)
                msg_Disconnect=msg.decode('utf-8').rstrip()
                for connection in self.Connections:
                    if connection != Cliente:
                        connection.sendall(msg)
                if(msg_Disconnect=="Disconnect"):
                    self.socketClose()
                    self.socketOpen()
            except Exception as e:
                print(e)
                self.socketClose()
                self.socketOpen()
            except KeyboardInterrupt:
                self.socketClose()
                sys.exit()

def main():
    #ip = get('https://api.ipify.org').text
    #print(f'My public IP address is: {ip}')
    #SERVERIP=socket.gethostbyname(socket.gethostname())
    #SERVERIP='200.24.17.170'
    SERVERIP='localhost'
    server = Server(SERVERIP, 8883)

if __name__ == "__main__":
    main()