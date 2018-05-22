__author__ = 'geurt'

from twisted.protocols.basic import LineReceiver
from bliknetlib import serialMsg
import traceback

class SerialNodesProtocol(LineReceiver):

    def __init__(self, NodeControl, OnReceive):
        self._NodeControl = NodeControl
        self._OnReceive = OnReceive
        self.setRawMode()
        self._rawDataReceived = ""
        # self._readingMsg = False

    def rawDataReceived(self, sReceivedData):
        """  typical message:
             byte message[] = {0x00, 0x39, 0x39, 0x39, 0x30, 0x30, 0x32, 0x06, 0x30, 0x30, 0x2b, 0x33, 0x30, 0x30, 0x31, 0x04, 0x30, 0x30, 0x30, 0x04};
        """
        self._NodeControl.log.debug("rawDataReceived: %s." % (sReceivedData))
        if len(sReceivedData) > 0:
            """ if sReceivedData.find(chr(0x0)) >= 0:
    # self._readingMsg = True
    self._rawDataReceived = chr(0x0) + sReceivedData[sReceivedData.index(chr(0x0))+1:]
    elif sReceivedData.find(chr(0x04)) >= 0:
self._rawDataReceived = self._rawDataReceived + sReceivedData
if self._rawDataReceived.count(chr(0x04))==2:
myMsg = self._rawDataReceived[:self._rawDataReceived.rfind(chr(0x04))+1]
self._readingMsg = False
try:
myReceivedSerialMsg = serialMsg.serialMsg()
myReceivedSerialMsg.serialMsgFromString(myMsg)
if myReceivedSerialMsg.IsValid:
    self._NodeControl.log.info("Received valid message. Serial line: [%s]" % (myMsg))
    self._OnReceive(myReceivedSerialMsg)
except Exception, exp:
self._NodeControl.log.info(
    "Error reading serial line: [%s], error: %s." % (traceback.format_exc(), myMsg)) 
            # elif self._readingMsg:
            else: 
                self._rawDataReceived = self._rawDataReceived + sReceivedData """
            self._rawDataReceived = self._rawDataReceived + sReceivedData
            self._processRawData()

    def _processRawData(self):
        # TODO what if during processing rawDataReceived event happens?
        while ( (self._rawDataReceived.find(chr(0x0)) >= 0) and
                (self._rawDataReceived.count(chr(0x04)) >= 2) and
                ( (self._rawDataReceived.find(chr(0x0)) < (self._rawDataReceived.find(chr(0x4))) ) ) ):
            endPos = self._rawDataReceived.find(chr(0x04), self._rawDataReceived.find(chr(0x04))+1) # find second instance
            msgToken = self._rawDataReceived[self._rawDataReceived.find(chr(0x0)):endPos+1]
            self._rawDataReceived = self._rawDataReceived[endPos+1:] # update rawDate without parsed msgToken

            try:
                myReceivedSerialMsg = serialMsg.serialMsg()
                myReceivedSerialMsg.serialMsgFromString(msgToken)
                if myReceivedSerialMsg.IsValid:
                    self._NodeControl.log.info("Received valid message. Serial line: [%s]" % (msgToken))
                    self._OnReceive(myReceivedSerialMsg)
            except Exception:
                self._NodeControl.log.info(
                    "Error reading serial line: [%s], error: %s." % (traceback.format_exc(), msgToken))
        if ( (len(self._rawDataReceived) > 0) and
                (self._rawDataReceived.find(chr(0x0)) == -1) ):
            self._rawDataReceived=="" # cleanup when self._rawDataReceived is garbadge


