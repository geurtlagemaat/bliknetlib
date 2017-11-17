__author__ = 'geurt'


class serialMessageException(Exception):
    pass

class serialMessageType:
    ENQ, ACK, NAK = range(3)

class serialMessageSign:
    POSITIVE, NEGATIVE = range(2)

class serialMsg(object):
    def __init__(self, FromAdress=None, ToAdress=None, Function=None, MsgType=serialMessageType.ENQ):
        self._FromAdress = None                     # drie posities 001 - 999
        self._ToAdress = None                       # drie posities 001 - 999
        self._MsgType = MsgType  # ENQ, ACK, NAK
        self._Function = None                       # twee posities 01 - 99
        self._Sign = serialMessageSign.POSITIVE
        self._DecPos = 3                            # 0x30 (0 dus alles is 0.123), 0x31 (dus 1.23), 0x32 (dus 12.3), 0x33 (dus 123) 48 of 49 of 50
        self._MsgValue = None                       # drie posities 000 - 999
        self._IsValid = False
        if FromAdress is not None:
            self.FromAdress = FromAdress
        if ToAdress is not None:
            self.ToAdress = ToAdress
        if Function is not None:
            self.Function = Function
            # comm details
        self._SendTime = 0
        self._Trys = 0

    def serialMsgFromString(self, sString):
        if len(sString) >= 19:
            sReadChecksum = sString[16:19]
            iReadChecksum = int(sReadChecksum)
            # calculate iChecksum
            iCalculatedChecksum = 0
            iPos = 0
            for cChar in sString:
                iCalculatedChecksum += ord(cChar)
                iPos += 1
                if iPos == 16:
                    break
            if iCalculatedChecksum != iReadChecksum:
                raise serialMessageException("Invalid message: checksum mismatch")
            else:
                self._ToAdress = sString[1:4]
                self._FromAdress = sString[4:7]
                sMsgType = sString[7:8]
                #if sMsgType=='':
                if ord(sMsgType) == 5:
                    self._MsgType = serialMessageType.ENQ
                elif ord(sMsgType) == 6:
                    self._MsgType = serialMessageType.ACK
                elif ord(sMsgType) == 21:
                    self._MsgType = serialMessageType.NAK
                self._Function = sString[8:10]
                sSign = sString[10:11]
                if sSign == "-":
                    self._Sign = serialMessageSign.NEGATIVE
                else:
                    self._Sign = serialMessageSign.POSITIVE
                self._DecPos = sString[11:12]
                self._MsgValue = sString[12:15]
                self._IsValid = True

    def serialMsgToString(self):
        sTmp = chr(0x0)
        if self._ToAdress is not None:
            sTmp += str(self._ToAdress)
        else:
            sTmp += "000"
        if self._FromAdress is not None:
            sTmp += str(self._FromAdress)
        else:
            sTmp += "000"
        if self._MsgType == serialMessageType.ENQ:
            sTmp += chr(0x05)
        elif self._MsgType == serialMessageType.ACK:
            sTmp += chr(0x06)
        elif self._MsgType == serialMessageType.NAK:
            sTmp += chr(0x15)
        if self._Function is not None:
            sTmp += str(self._Function)
        else:
            sTmp += "00"
        if self._Sign == serialMessageSign.POSITIVE:
            sTmp += "+"
        else:
            sTmp += "-"
        if self._DecPos is not None:
            sTmp += str(self._DecPos)
        else:
            sTmp += "3"
        if self._MsgValue is not None:
            sTmp += str(self._MsgValue)
        else:
            sTmp += "000"
        sTmp += chr(0x04) # EOT

        iChecksum = 0
        for cChar in sTmp:
            iChecksum += ord(cChar)
        sTmp += str(iChecksum)
        sTmp += chr(0x04)  # EOT
        return sTmp #TODO, check geen laatste EOT?

    # FromAdress
    @property
    def FromAdress(self):
        return self._FromAdress

    @FromAdress.setter
    def FromAdress(self, value):
        self._FromAdress = "%03d" % (value,)

    # ToAdress
    @property
    def ToAdress(self):
        return self._ToAdress

    @ToAdress.setter
    def ToAdress(self, value):
        self._ToAdress = "%03d" % (value,)

    # MsgType
    @property
    def MsgType(self):
        return self._MsgType

    @MsgType.setter
    def MsgType(self, value):
        self._MsgType = value

    # Function
    @property
    def Function(self):
        return self._Function

    @Function.setter
    def Function(self, value):
        self._Function = "%02d" % (value,)

    # Sign
    @property
    def Sign(self):
        return self._Sign

    @Sign.setter
    def Sign(self, value):
        self._Sign = value

    # DecPos
    @property
    def DecPos(self):
        return self._DecPos

    @DecPos.setter
    def DecPos(self, value):
        self._DecPos = value

    # MsgValue
    @property
    def MsgValue(self):
        return self._MsgValue

    @MsgValue.setter
    def MsgValue(self, value):
        if isinstance( value, ( int, long ) ):
            self._MsgValue = "%03d" % (value,)
        else:
            self._MsgValue = value

    # IsValid
    @property
    def IsValid(self):
        return self._IsValid

    @IsValid.setter
    def IsValid(self, value):
        self._IsValid = value

    # SendTime
    @property
    def SendTime(self):
        return self._SendTime

    @SendTime.setter
    def SendTime(self, value):
        self._SendTime = value

    # _Retrys
    @property
    def Trys(self):
        return self._Trys

    @Trys.setter
    def Trys(self, value):
        self._Trys = value