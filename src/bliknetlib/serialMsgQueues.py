__author__ = 'geurt'
import time


class SerialMsgQueues(object):
    def __init__(self, oNodeControl, iTimeOut, iRetrys, bRetrysFirst):
        self._NodeControl = oNodeControl
        self._MsgToSend = {}  # dict msg's waiting to be send. key is id (_GetKeyStr), value is serialMsg object.
        self._SendEnq = {}  # dict send msg's. key is id (_GetKeyStr), value is serialMsg object.
        self._Retrys = {}
        self._Acks = {}
        self._iTimeOut = iTimeOut
        self._iRetrys = iRetrys
        self._bRetrysFirst = bRetrysFirst

    def AddMsgToSend(self, oSerialMsg):
        if self._GetKeyStr(oSerialMsg) not in self._MsgToSend:
            self._MsgToSend[self._GetKeyStr(oSerialMsg)] = oSerialMsg

    def MsgIsSend(self, oSerialMsg):
        if self._GetKeyStr(oSerialMsg) in self._MsgToSend:
            del self._MsgToSend[self._GetKeyStr(oSerialMsg)]

    def GetNextMsgToSend(self):
        if len(self._Acks) > 0:
            myID, mySerialMsg = self._Acks.popitem()
            return mySerialMsg
        elif self._bRetrysFirst:
            if len(self._Retrys) > 0:
                myID, mySerialMsg = self._Retrys.popitem()
                return mySerialMsg
            elif len(self._MsgToSend) > 0:
                myID, mySerialMsg = self._MsgToSend.popitem()
                return mySerialMsg
            else:
                return None
        else:
            if len(self._MsgToSend) > 0:
                myID, mySerialMsg = self._MsgToSend.popitem()
                return mySerialMsg
            elif len(self._Retrys) > 0:
                myID, mySerialMsg = self._Retrys.popitem()
                return mySerialMsg
            else:
                return None

    def AddEnqMsg(self, oSerialMsg):
        if self._GetKeyStr(oSerialMsg) not in self._SendEnq:
            oSerialMsg.SendTime = time.time()
            oSerialMsg.Trys += 1
            self._SendEnq[self._GetKeyStr(oSerialMsg)] = oSerialMsg

    def EnqMsgAnswered(self, oSerialMsg):
        if self._GetKeyStr(oSerialMsg) in self._SendEnq:
            del self._SendEnq[self._GetKeyStr(oSerialMsg)]
            # also in waiting for retry?
            if self._GetKeyStr(oSerialMsg) in self._Retrys:
                del self._Retrys[self._GetKeyStr(oSerialMsg)]
        else:
            self._NodeControl.log.debug("Got message with key which is not found in Enq. queue. Message: %s." % (
                oSerialMsg.serialMsgToString()))

    def AddAckMesg(self, oSerialMsg):
        if self._GetKeyStr(oSerialMsg) not in self._Acks:
            self._Acks[self._GetKeyStr(oSerialMsg)] = oSerialMsg

    def IsEmptyEnqQueue(self):
        if len(self._SendEnq) > 0:
            return False
        else:
            return True

    def CheckEnqTimeOuts(self):
        for MsgKey, oSerialMsg in self._SendEnq.items():
            if ((oSerialMsg.SendTime + self._iTimeOut) > time.time()):
                self._NodeControl.log.warning(
                    "Timeout of: %s, removed from Enq. queue. Current Message Trys is: %s." % (
                        MsgKey, str(oSerialMsg.Trys)))
                print "Timeout of key: %s, removed from Enq. queue. Current Message Trys is: %s." % (
                    MsgKey, str(oSerialMsg.Trys))
                del self._SendEnq[MsgKey]
                if oSerialMsg.Trys < self._iRetrys:
                    if self._GetKeyStr(oSerialMsg) not in self._Retrys:
                        self._NodeControl.log.debug("Msg not found on retry queue, added: %s." % (MsgKey))
                        oSerialMsg.SendTime = 0
                        self._Retrys[MsgKey] = oSerialMsg
                    else:
                        self._NodeControl.log.warning("Msg found on retry queue, not added: %s." % (MsgKey))
                else:
                    print "retries exhausted for: %s, retrys is set to: %s." % (MsgKey, str(self._iRetrys))
                    self._NodeControl.log.warning(
                        "retries exhausted for: %s, max retrys is set to: %s." % (MsgKey, str(self._iRetrys)))
                    if self._GetKeyStr(oSerialMsg) in self._Retrys:
                        del self._Retrys[self._GetKeyStr(oSerialMsg)]

    def ClearQueues(self):
        self._Retrys.clear()
        self._MsgToSend.clear()
        self._SendEnq.clear()
        self._Acks.clear()

    def _GetKeyStr(self, oSerialMsg):
        sFromAdress = str(oSerialMsg.FromAdress)
        sToAdress = str(oSerialMsg.ToAdress)
        if sFromAdress != self._NodeControl.nodeID:
            return "%s_%s" % (sFromAdress, str(oSerialMsg.Function))
        else:
            return "%s_%s" % (sToAdress, str(oSerialMsg.Function))
