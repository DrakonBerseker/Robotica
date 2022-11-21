import  socket, threading, sys,cv2, traceback

class Server:

    def __init__(self, ip, port):
        #Atributos de la clase
        self.TCP_IP = ip
        self.TCP_PORT = port
        self.Connections=[]
        self.counter=0
        self.socketOpen()#Funcion
        self.receiveThread = threading.Thread(target=self.sendImageInfo)
        self.receiveThread.start()

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
                print(f'El server esta conectado con el cliente de ip {Direccion[0]} y puerto {Direccion[1]}')
                Cliente.sendall("Conexion Aceptada".encode('utf-8'))
            for Client in self.Connections:
                Client.sendall("Todas las conexiones fueron establecidas".encode('utf-8'))   
            self.sendImageInfo()
                #Thread=threading.Thread(target=self.sendImageInfo, args=(Cliente,))
                #Thread.start()
        except Exception as e:
            print(e)
            traceback.print_exc()
            #cv2.waitKey()
            self.socketClose()
            self.socketOpen()

    def sendImageInfo(self):
        while True:
            try:
                self.counter += 1
                print(self.counter)
                imglenght=self.Connections[0].recv(64)
                #imgdata=self.Connections[0].recv(int(imglenght.decode('utf-8')))
                self.Connections[1].sendall(imglenght)
                buf=self.sendall(int(imglenght.decode('utf-8')))

            except Exception as e:
                print(e)
                traceback.print_exc()
                self.socketClose()
                self.socketOpen()
            except KeyboardInterrupt:
                self.socketClose()
                sys.exit()

    def sendall(self, count):
        try:
            buf=b''
            while count:
                newbuf = self.Connections[0].recv(count)
                self.Connections[1].sendall(newbuf)
                if not newbuf: return None
                buf += newbuf
                count -= len(newbuf)
            return buf
        except KeyboardInterrupt:
            self.socketClose()
            sys.exit()

def main():
    #ip = get('https://api.ipify.org').text
    #print(f'My public IP address is: {ip}')
    #SERVERIP=socket.gethostbyname(socket.gethostname())
    SERVERIP='localhost'
    #SERVERIP='200.24.17.170'
    TCPPORT=8883
    server = Server(SERVERIP, TCPPORT)

if __name__ == "__main__":
    main()