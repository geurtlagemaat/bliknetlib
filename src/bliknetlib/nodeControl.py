__author__ = 'geurt'
import configparser
import logging
import os
import time
import traceback

from CircusNotifier import circusNotifier

try:
    from cloghandler import ConcurrentRotatingFileHandler as RFHandler
    ConcurrentLogHandler = True
except ImportError:
    from warnings import warn
    warn("ConcurrentLogHandler package not installed. Using builtin log handler")
    from logging.handlers import RotatingFileHandler as RFHandler
    ConcurrentLogHandler = False

class nodeControl(object):
    def __init__(self, propertiesfile):
        self.propertyStore = {}
        self.propertiesFile = propertiesfile
        self.nodeProps = None
        self.nodeProps = configparser.ConfigParser()
        self.nodeProps.read(propertiesfile)

        self.nodeID = self.nodeProps.get('system', 'nodeId')

        if self.nodeProps.has_option('log', 'logLevel'):
            logMode = self.nodeProps.get('log', 'logLevel')
            if logMode.upper() == 'DEBUG':
                logLevel = logging.DEBUG
            elif logMode.upper() == 'INFO':
                logLevel = logging.INFO
            elif logMode.upper() == 'WARNING':
                logLevel = logging.WARNING
            elif logMode.upper() == 'ERROR':
                logLevel = logging.ERROR
            else:
                logLevel = logging.INFO
        else:
            logLevel = logging.INFO

        if self.nodeProps.has_option('log', 'logFile'):
            logFile = self.nodeProps.get('log', 'logFile')
        else:
            logFile = 'logs/bliknetNode.log'

        # CANDO set maxLogFiles and maxLogfileSize
        if self.nodeProps.has_option('log', 'logFiles'):
            maxLogFiles = self.nodeProps.getint('log', 'logFiles')
        else:
            maxLogFiles = 5
        if self.nodeProps.has_option('log', 'logSize'):
            maxLogfileSize = self.nodeProps.getint('log', 'logSize') * 1024
        else:
            maxLogfileSize = 512 * 1024

        self.log = logging.getLogger('')
        self.log.setLevel(logLevel)
        handler = RFHandler(logFile, maxBytes=maxLogfileSize, backupCount=maxLogFiles)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(process)-5d [%(module)s.%(funcName)s:%(lineno)d] %(message)s")
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.info("BliknetNode config, nodeID: %s" % (self.nodeID))

        # serial stuff
        """if self.nodeProps.has_option('serial', 'port'):
            self.serial = self.nodeProps.get('serial', 'port')
            self.log.info("Found serial port: %s" % self.serial)
        else:
            self.log.info("Did not found a serial port") """

        # data dir
        if self.nodeProps.has_option('paths', 'data'):
            self.datadir = self.nodeProps.get('paths', 'data')
            self.log.info("Found datadir location: %s" % self.datadir)
        else:
            self.log.info("Did not found a datadir location")

        # init DB
        self.DBConn = None
        self.DBCursor = None
        if self.nodeProps.has_option('database', 'dbtype') and \
                        self.nodeProps.get('database', 'dbtype') == "sqllite":
            if not self.nodeProps.has_option('database', 'datafile'):
                self.log.error("No SQLLite datafile location found in configfile")
            elif not os.path.isfile(self.nodeProps.get('database', 'datafile')):
                self.log.error("SQLLite datafile location does not exists")
            else:
                try:
                    import sqlite3
                    self.DBConn = sqlite3.connect(self.nodeProps.get('database', 'datafile'))
                    self.DBCursor = self.DBConn.cursor()
                except Exception as exp:
                    self.log.error(
                        "SQLLite init error. Location %s, error %s." % (self.nodeProps.get('database', 'datafile'), \
                                                                        traceback.format_exc()))
        elif self.nodeProps.has_option('database', 'dbtype') and \
                        self.nodeProps.get('database', 'dbtype') == "mysql":
            if not self.nodeProps.has_option('database', 'host') or \
                    not self.nodeProps.has_option('database', 'port') or \
                    not self.nodeProps.has_option('database', 'db') or \
                    not self.nodeProps.has_option('database', 'user') or \
                    not self.nodeProps.has_option('database', 'pw'):
                self.log.error("MySQL config options incomplete (host, port, db, user and pw.")
            else:
                try:
                    import mysql.connector
                    self.DBConn = mysql.connector.connect(host=self.nodeProps.get('database', 'host'),
                                                          port=self.nodeProps.getint('database', 'port'),
                                                          db=self.nodeProps.get('database', 'db'),
                                                          user=self.nodeProps.get('database', 'user'),
                                                          passwd=self.nodeProps.get('database', 'pw'))
                    self.DBCursor = self.DBConn.cursor()
                except Exception as exp:
                    self.log.error("mysql init error. Location %s, error %s." % (traceback.format_exc()))
        # init MQTT
        self.client = None
        self.mqttClient = None
        if self.nodeProps.has_option('MQTT', 'brokerActivate') and self.nodeProps.getboolean('MQTT', 'brokerActivate'):
            # init and activate MQTT broker
            self.mqttURL = self.nodeProps.get('MQTT', 'brokerURL')
            self.mqttPort = self.nodeProps.get('MQTT', 'brokerPORT')
            self.mqttClientID = self.nodeProps.get('MQTT', 'clientID')
            self.log.info("MQTT broker set to URL:%s, port: %s and ClientID: %s" % (
                self.mqttURL, self.mqttPort, self.mqttClientID))
            iTry = 1
            while not self.doMQTTConnect(iTry):
                if iTry == 5:
                    break
                time.sleep(20)
                iTry += 1
            if self.mqttClient is None:
                self.log.error("can not connect to MQTT Broker: %s. URL: %s, port: %s. Max trys reached, giving up." % (
                    traceback.format_exc(), self.mqttURL, self.mqttPort))
            """try:
                import paho.mqtt.client as paho
                self.mqttClient = paho.Client(client_id=self.mqttClientID)
                self.mqttClient.on_connect = self.on_MQTTConnect
                self.mqttClient.username_pw_set(self.nodeProps.get('MQTT', 'user'), self.nodeProps.get('MQTT', 'pw'))
                self.mqttClient.connect(self.mqttURL, self.mqttPort)
                # self.mqttClient.loop_start()
            except Exception, exp:
                self.log.error("can not connect to MQTT Broker: %s. URL: %s, port: %s." % (
                    traceback.format_exc(), self.mqttURL, self.mqttPort ))  """
        else:
            self.log.info("MQTT broker not activated")

        # Circus Watchdog
        self.circusNotifier = None
        self.log.info('circusWatchDog Notifier init')
        if self.nodeProps.has_option('watchdog', 'circusWatchDog'):
            if self.nodeProps.getboolean('watchdog', 'circusWatchDog') == True:
                self.circusNotifier = circusNotifier(self)
                self.log.info('circusWatchDog Notifier active')
            else:
                self.log.info('circusWatchDog Notifier NOT active')

    def __exit__(self, exception_type, exception_value, traceback):
        if self.mqttClient != None:
            self.mqttClient.disconnect()
        print("in __exit__, excpetion: %s." % exception_value)

    # MQTT Functions
    def doMQTTConnect(self, iTry=1):
        try:
            import paho.mqtt.client as paho
            self.mqttClient = paho.Client(client_id=self.mqttClientID)
            self.mqttClient.on_connect = self.on_MQTTConnect
            self.mqttClient.username_pw_set(self.nodeProps.get('MQTT', 'user'), self.nodeProps.get('MQTT', 'pw'))
            self.mqttClient.connect(self.mqttURL, self.mqttPort)
            return True
        except Exception as exp:
            self.log.error("can not connect to MQTT Broker: %s. URL: %s, port: %s. Try: %s." % (
                traceback.format_exc(), self.mqttURL, self.mqttPort, iTry))
            return False

    def on_MQTTConnect(self, client, userdata, flags, rc):
        self.log.info("MQTTConnected, client: %s, userdata: %s, flags:% s and rc: %s" % (client, userdata, flags, rc))
        pass

    def MQTTPublish(self, sTopic, sValue, iQOS=0, bRetain=True):
        self.log.debug("MQTTPublish of topic: %s, value: %s." % (sTopic, sValue))
        if self.mqttClient != None:
            try:
                self.mqttClient.publish(sTopic, sValue, qos=iQOS, retain=bRetain)
                self.log.debug("MQTTPublish of topic %s done" % sTopic)
            except Exception as exp:
                self.log.warning("can not publish to MQTT Broker: %s" % traceback.format_exc())

    # generic store
    def setProperty(self, propertyName, propertyValue):
        self.propertyStore[propertyName] = propertyValue

    def getProperty(self, propertyName):
        if propertyName in self.propertyStore:
            return self.propertyStore[propertyName]
        else:
            return None