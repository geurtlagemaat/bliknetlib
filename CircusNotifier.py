__author__ = 'lagemaag'
import time, os
import traceback
from socket import *

from twisted.internet import task

class circusNotifier():
    def __init__(self, nodeControl):
        self.nodeControl = nodeControl
        self.circusNotifierEnabled = False

        if nodeControl.nodeProps.has_option('watchdog', 'circusWatchDog') and nodeControl.nodeProps.getboolean(
                'watchdog', 'circusWatchDog') == True:
            if nodeControl.nodeProps.has_option('watchdog', 'circusWatchDogInterval'):
                self.notifyInterval = nodeControl.nodeProps.get('watchdog', 'circusWatchDogInterval')
            else:
                self.notifyInterval = 10
            if nodeControl.nodeProps.has_option('watchdog', 'circusWatchDogPort'):
                self.notificationPort = nodeControl.nodeProps.get('watchdog', 'circusWatchDogPort')
            else:
                self.notificationPort = 1664
            if nodeControl.nodeProps.has_option('watchdog', 'circusWatchDogHost'):
                self.notificationHost = nodeControl.nodeProps.get('watchdog', 'circusWatchDogHost')
            else:
                self.notificationHost = '127.0.0.1'
            try:
                self.udpSocket = self.makeSocket()
                self.circusNotifierEnabled = True
            except:
                self.circusNotifierEnabled = False
                exception = str(traceback.format_exc())
                self.nodeControl.log.error('Error init circusNotifier: %s' % exception)

    def start(self):
        if self.circusNotifierEnabled == True:
            self.l = task.LoopingCall(self.sendNotification)
            self.l.start(int(self.notifyInterval))
            self.nodeControl.log.debug('circusNotifier started, interval: %s' % self.notifyInterval)
        else:
            self.nodeControl.log.error('Could not start circusNotifier')

    def sendNotification(self):
        if self.circusNotifierEnabled == True:
            try:
                if (self.nodeControl.nodeProps.has_option('watchdog', 'circusWatchDogPIDTYPE') and \
                            self.nodeControl.nodeProps.get('watchdog', 'circusWatchDogPIDTYPE') == "PPID"):
                    # stuur de pid van het parent proces
                    msgParent = '%d;%f' % (os.getppid(), time.time())
                    self.nodeControl.log.debug('Sending Circus Notification Parent pid message: %s' % msgParent)
                    self.udpSocket.sendto(msgParent,
                                          (self.notificationHost, int(self.notificationPort)))
                else:
                    # stuur de pid van het eigen proces (default)
                    msg = '%d;%f' % (os.getpid(), time.time())
                    self.nodeControl.log.debug('Sending Circus Notification message: %s' % msg)
                    self.udpSocket.sendto(msg, (self.notificationHost, int(self.notificationPort)))
            except:
                exception = str(traceback.format_exc())
                self.nodeControl.log.error('Failed to send watchdog message: %s' % exception)
                self.circusNotifierEnabled = False
                try:
                    self.udpSocket.close()
                    self.udpSocket = None
                except:
                    exception = str(traceback.format_exc())
                    self.nodeControl.log.error('Failed to close watchdog socket: %s' % exception)
            return True

    def makeSocket(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('', 0))
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        return s