import numpy, socket, cv2, threading, base64,sys
class Receive:

    def __init__(self, ip, port):
        #Atributos de la clase
        self.TCP_SERVER_IP = ip
        self.TCP_SERVER_PORT = port
        self.connectCount = 0
        self.ConnectServer()#Funcion
        self.receiveThread = threading.Thread(target=self.receiveImages)
        self.receiveThread.start()

    #metodos

    #Cerrar el socket
    def socketClose(self):
        self.sock.close()
        print(u'Server socket [ TCP_IP: ' + self.TCP_SERVER_IP + ', TCP_PORT: ' + str(self.TCP_SERVER_PORT) + ' ] is close')

    #Abrir el socket
    def ConnectServer(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.TCP_SERVER_IP, self.TCP_SERVER_PORT))
            print(u'Client socket is connected with Server socket [ TCP_SERVER_IP: ' + self.TCP_SERVER_IP + ', TCP_SERVER_PORT: ' + str(self.TCP_SERVER_PORT) + ' ]')
            self.connectCount = 0
            print(self.sock.recv(17).decode('utf-8'))
            print(self.sock.recv(42).decode('utf-8'))
            self.receiveImages()
        except Exception as e:
            print(e)
            self.connectCount += 1
            if self.connectCount == 10:
                print(u'Connect fail %d times. exit program'%(self.connectCount))
                sys.exit()
            print(u'%d times try to connect with server'%(self.connectCount))
            self.ConnectServer()

    def receiveImages(self):
        try:
            while True:
                #Necesitamos el tamaño de la imagen y decodificarlo esto servira como cabezera del mensaje, ademas, tiene un tamaño fijo de 64bits
                length = self.recvall(self.sock, 64)
                length1 = length.decode('utf-8')
                #Recibir la data de la imagen en forma de string, recibiendo toda la imagen a traves de la funcion creada recvall
                stringData = self.recvall(self.sock, int(length1))
                #Recibimos el tiempo que se demoro la data en llegar del cliente al server
                data = numpy.frombuffer(base64.b64decode(stringData), numpy.uint8)#Decodifica toda esta damier a uint8 para que almenos tenga el rango de pixeles
                decimg = cv2.imdecode(data, 1)#Convierte la damier anterior en un formato valido de imagen *ejem* BGR *ejem*
                cv2.imshow("image", decimg)
                cv2.waitKey(1)
        except Exception as e:
            print(e)
            self.socketClose()
            cv2.destroyAllWindows()
            self.ConnectServer()
            self.receiveThread = threading.Thread(target=self.receiveImages)
            self.receiveThread.start()

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

def main():
    #ip = get('https://api.ipify.org').text
    #print(f'My public IP address is: {ip}')
    #SERVERIP=socket.gethostbyname(socket.gethostname())
    SERVERIP='localhost'
    #SERVERIP='200.24.17.170'
    TCPPORT=8883
    server = Receive(SERVERIP, TCPPORT)

if __name__ == "__main__":
    main()