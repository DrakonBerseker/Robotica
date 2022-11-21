import socket, time, sys, cv2, os, traceback
import mediapipe as mp
import numpy as np
import math as mt
mp_drawing_styles = mp.solutions.drawing_styles
mp_drawing = mp.solutions.drawing_utils #Esto es para sacar las herramientas de dibujo incluidas en mp
mp_pose = mp.solutions.pose #Este es el objeto de la clase pose de mp que detecta el cuerpo

class ControlCliente:
    def __init__(self, ip, port):
        #Atributos
        self.TCP_SERVER_IP = ip
        self.TCP_SERVER_PORT = port
        self.TotalConnectionTries=10
        self.connectCount = 0
        self.fixedmsglenght = 1024
        #Intento configuracion
        self.intentosConfiguracion=0
        self.maxIntentosConfiguracion=10
        #Intento de conexion
        self.connectServer()

    def connectServer(self):
        try:
            #Declaro el socket del server
            self.Sock = socket.socket()
            self.Sock.connect((self.TCP_SERVER_IP, self.TCP_SERVER_PORT))
            print(u'El cliente tiene la direccion IP: ' + self.TCP_SERVER_IP + ', Con puerto: ' + str(self.TCP_SERVER_PORT))
            print(self.receive_msg(17))
            self.connectCount = 0
            self.modeSelector()
        except Exception as e:
            print(e)
            self.connectCount += 1
            if self.connectCount >= self.TotalConnectionTries:
                print(u'No se pudo establecer conexion %d veces. Cerrando el cliente'%(self.connectCount))
                sys.exit()
            print(u'Intento de conexion numero {intentos} de {total}'.format(intentos=str(self.connectCount),total=str(self.TotalConnectionTries)))
            self.connectServer()

    def modeSelector(self):
        self.pausaFotograma=float(input("Introduzca la pausa en segundos entre cada fotograma "))
        self.Modo=input("\nSeleccione la forma en que desea manipular el robot:\n1.Modo de captura\n2.Modo continuo\n")
        if self.Modo == '1' or self.Modo == '2':
            self.send_msg("Valido")
            print(self.receive_msg(self.fixedmsglenght))
            self.TryConnectDobot()
        else:
            print("No ha seleccionado un modo valido")
            self.send_msg("Invalido")
            print(self.receive_msg(self.fixedmsglenght))
            sys.exit()

    def TryConnectDobot(self):
        print("Configurando Dobot")
        Estado="Reintentar"
        while(Estado == "Reintentar" and (self.intentosConfiguracion<=self.maxIntentosConfiguracion)):
            Connect_status=self.receive_msg(self.fixedmsglenght)
            if (Connect_status=="Dobot configurado..."):
                print(f"Conexion exitosa en el intento {self.intentosConfiguracion}")
                Estado=""
                self.send_msg("Recibir tripletas")
                break
            else:
                self.intentosConfiguracion += 1
                print(Connect_status)
                self.send_msg("Retry")
        if Estado=="":
            self.ImageProcessing()
        else:
            print(f"Despues de {self.maxIntentosConfiguracion} no fue posible configurar el dobot y por lo tanto se cerrara el cliente")
            self.send_msg("NoMoreTries")
            sys.exit()

    def receive_msg(self, lenght):
        return self.Sock.recv(lenght).decode('utf-8').rstrip()
    
    def send_msg(self, msg):
        self.Sock.sendall(msg.ljust(self.fixedmsglenght).encode('utf-8'))
 
    def ImageProcessing(self):
        print("Entre a procesar imagenes")
        cnt = 0
        video = cv2.VideoCapture(0)
        base=0
        smooth_minimun_size=10
        suavizado_angulo_brazo=[]
        suavizado_angulo_codo=[]
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as self.pose:
            while video.isOpened():
                start=time.time()

                #Captura, tratamiento de la imagen original y procesamiento mediapipe
                _, self.image = video.read()
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                self.image = cv2.flip(self.image,1)
                self.Procesamiento_Mediapipe()
                self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
                try:
                    #Resultado de angulos
                    BrazoIzquierdo, CodoIzquierdo, CodoDerecho,Pos_CodoDerecho,Pos_CodoIzquierdo,Pos_HombroIzquierdo=self.Resultados_Articulaciones()
                    angulo_suavizado_brazoIzquierdo, angulo_suavizado_codoizquierdo=self.Suavizado_Angulos(suavizado_angulo_brazo,suavizado_angulo_codo,BrazoIzquierdo,CodoIzquierdo,smooth_minimun_size)
                    #Angulo de la base
                    if(CodoDerecho<40):
                        base=-90.0 if (base-0.5)<-90 else base-0.5
                    elif(CodoDerecho>90):
                        base=90.0 if (base+0.5)>90 else base+0.5

                    #Modo Captura(Meter codigo)
                    if(self.Modo=="1"):
                        if cv2.waitKey(1) & 0xFF == ord ('p'):
                            self.sendTriplets(base, angulo_suavizado_brazoIzquierdo, angulo_suavizado_codoizquierdo)
                    #Modo Continuo
                    else:
                        self.sendTriplets(base, angulo_suavizado_brazoIzquierdo, angulo_suavizado_codoizquierdo)
                        
                    mp_drawing.draw_landmarks(self.image, self.resultados_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS, mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))
                    self.Informacion_Imagen(BrazoIzquierdo,CodoIzquierdo,base,Pos_CodoDerecho,Pos_CodoIzquierdo,Pos_HombroIzquierdo)
                except Exception:
                    traceback.print_exc()
                    self.send_msg("pasar")
                    pass
                end=time.time()
                fps=int(1/(end-start))
                cv2.putText(self.image,str(fps),(50,50),cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.imshow('Mediapipe Process', self.image)
                time.sleep(self.pausaFotograma)
                if cv2.waitKey(1) & 0xFF == ord ('q'):
                    if(self.Seleccion_Pausa()):
                        continue
                    else:
                        break
            video.release()
            cv2.destroyAllWindows()
    
    def Procesamiento_Mediapipe(self):
        self.image.flags.writeable = False
        self.resultados_pose = self.pose.process(self.image)
        self.image.flags.writeable = True

    def Calculo_Angulos(self,a,b,c,lim_inf,lim_sup):
        a=np.array(a)
        b=np.array(b)
        c=np.array(c)
        angulo=mt.degrees(np.arctan2(b[1]-a[1],b[0]-a[0])-np.arctan2(b[1]-c[1],b[0]-c[0]))
        if(lim_inf<=angulo<=lim_sup):
            return round(angulo,0)
        else:
            if(angulo>lim_sup):
                return round(lim_sup,0)
            else:
                return round(lim_inf,0)

    def Resultados_Articulaciones(self):
        articulaciones=self.resultados_pose.pose_landmarks.landmark
        Muneca_Derecha=[articulaciones[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,articulaciones[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        Codo_Derecho=[articulaciones[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,articulaciones[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        Hombro_Derecho=[articulaciones[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,articulaciones[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        Hombro_Izquierdo=[articulaciones[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,articulaciones[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        Codo_Izquierdo=[articulaciones[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,articulaciones[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        Muneca_Izquierda=[articulaciones[mp_pose.PoseLandmark.LEFT_WRIST.value].x,articulaciones[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        angulo_brazoIzquierdo_Torso = float(self.Calculo_Angulos(Hombro_Derecho,Hombro_Izquierdo,Codo_Izquierdo,105,134.14)-100)
        angulo_codoizquierdo = float(90+self.Calculo_Angulos(Hombro_Izquierdo,Codo_Izquierdo,Muneca_Izquierda,-90,-39.89))
        angulo_cododerecho = float(self.Calculo_Angulos(Hombro_Derecho,Codo_Derecho,Muneca_Derecha,0,180))
        return angulo_brazoIzquierdo_Torso, angulo_codoizquierdo, angulo_cododerecho, Codo_Derecho, Codo_Izquierdo, Hombro_Izquierdo

    def Suavizado_Angulos(self,suavizado_angulo_brazo,suavizado_angulo_codo,BrazoIzquierdo, CodoIzquierdo,buffer_suavizado):
        if(len(suavizado_angulo_brazo)==buffer_suavizado and len(suavizado_angulo_codo)==buffer_suavizado):
            suavizado_angulo_brazo.pop(0)
            suavizado_angulo_brazo.append(BrazoIzquierdo)
            suavizado_angulo_codo.pop(0)
            suavizado_angulo_codo.append(CodoIzquierdo)
            angulo_suavizado_brazoIzquierdo_Torso=float(sum(suavizado_angulo_brazo,10)/buffer_suavizado)
            angulo_suavizado_codoizquierdo=float(sum(suavizado_angulo_codo,10)/buffer_suavizado)
            #dType.SetPTPCmd(api, 4,base,angulo_suavizado_brazoIzquierdo_Torso,angulo_suavizado_codoizquierdo,0,isQueued=1)
            return angulo_suavizado_brazoIzquierdo_Torso, angulo_suavizado_codoizquierdo
        else:
            if(len(suavizado_angulo_brazo)<buffer_suavizado):
                suavizado_angulo_brazo.append(BrazoIzquierdo)
            if(len(suavizado_angulo_codo)<buffer_suavizado):
                suavizado_angulo_codo.append(CodoIzquierdo)
            return 0, 0

    def Informacion_Imagen(self, BrazoIzquierdo,CodoIzquierdo,base, Codo_Derecho,Codo_Izquierdo,Hombro_Izquierdo):
        cv2.putText(self.image,str(BrazoIzquierdo),tuple(np.multiply(Hombro_Izquierdo,[640,480]).astype(int)),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(self.image,str(CodoIzquierdo),tuple(np.multiply(Codo_Izquierdo,[640,480]).astype(int)),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(self.image,str(base),tuple(np.multiply(Codo_Derecho,[640,480]).astype(int)),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)

    def sendTriplets(self, base, brazo, codo): 
        msg='_'+str(base)+'_'+str(brazo)+'_'+str(codo)
        self.send_msg(msg)

    def Seleccion_Pausa(self):
        Decision=input("¿Desea reconfigurar, continuar o salir?\n 1:Reconfigurar\n 2:Continuar\n Cualquier otro tecla: Salir\n")
        if(Decision=='1'):
            self.send_msg("Reconfigurar")
            self.TryConnectDobot()
            msg=self.receive_msg(len("Se ha reconfigurado el Dobot".encode('utf-8')))
            print(msg)
            return True
        elif(Decision=='2'):
            print("Continuar")
            return True
        else:
            print("Desconexion")
            self.send_msg("Disconnect")
            return False

def main():
    #TCP_IP = socket.gethostbyname(socket.gethostname())
    TCP_IP='200.24.17.170'
    #TCP_IP='localhost'
    TCP_PORT = 8883
    client = ControlCliente(TCP_IP, TCP_PORT)

if __name__ == "__main__":
    main()