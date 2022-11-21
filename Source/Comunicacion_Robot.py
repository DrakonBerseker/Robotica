import serial
import struct
import time
from dobotDLLs import DobotDllType as dType

#Funciones Magician
def Connect_Magician(api):
    CON_STR = {dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
                dType.DobotConnect.DobotConnect_NotFound: "Dobot no encontrado.",
                dType.DobotConnect.DobotConnect_Occupied: "Dobot esta ocupado.."}
    state = dType.ConnectDobot(api, "COM7", 115200)[0]
    if (state == dType.DobotConnect.DobotConnect_NoError):
        dType.SetQueuedCmdClear(api)
        dType.SetHOMEParams(api, 196, 0, -6, 200, isQueued = 1)
        dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued = 1)
        dType.SetPTPCommonParams(api, 100, 100, isQueued = 1)
        dType.SetHOMECmd(api, temp = 0, isQueued = 1)
        dType.SetQueuedCmdStartExec(api)
        time.sleep(20)
        return CON_STR[state]
    else:
        return CON_STR[state]

def Movimiento_Magician(api,j1,j2,j3):
    print("Entre a movimiento magician")
    dType.SetPTPCmd(api, 4,j1,j2,j3,0,isQueued=1)
    time.sleep(0.1)

def Disconect_Magician(api):
    dType.SetQueuedCmdStopExec(api)
    dType.DisconnectDobot(api)