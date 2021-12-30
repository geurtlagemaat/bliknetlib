# -*- coding: utf-8 -*-
import datetime
import traceback

import pytz
from astral import Astral, Location

def isDusk(oNodeControl):
    try:
        city = oNodeControl.nodeProps.get('location', 'city')
        country = oNodeControl.nodeProps.get('location', 'country')
        lat = oNodeControl.nodeProps.get('location', 'lat')
        long = oNodeControl.nodeProps.get('location', 'long')
        localtimezone = oNodeControl.nodeProps.get('location', 'localtimezone')
        elev = oNodeControl.nodeProps.get('location', 'elev')
        a = Astral()
        a.solar_depression = 'civil'
        l = Location()
        l.name = city
        l.region = country
        if "°" in lat:
            l.latitude = lat # example: 51°31'N parsed as string
        else:
            l.latitude = float(lat) #  make it a float

        if "°" in long:
            l.longitude = long
        else:
            l.longitude = float(long)

        l.timezone = localtimezone
        l.elevation = elev
        mySun = l.sun()
        oNodeControl.log.debug('Dawn: %s.' % str(mySun['dawn']))
        oNodeControl.log.debug('Sunrise: %s.' % str(mySun['sunrise']))
        oNodeControl.log.debug('Sunset: %s.' % str(mySun['sunset']))
        oNodeControl.log.debug('Dusk: %s.' % str(mySun['dusk']))
        oNodeControl.log.debug("Current time %s." % str(datetime.datetime.now(pytz.timezone(oNodeControl.nodeProps.get('location', 'localtimezone')))))
        """if datetime.datetime.now(pytz.timezone(oNodeControl.nodeProps.get('location', 'localtimezone'))) > mySun['sunrise'] and \
            datetime.datetime.now(pytz.timezone(oNodeControl.nodeProps.get('location', 'localtimezone'))) < mySun['dusk']:
            return False
        elif datetime.datetime.now(pytz.timezone(oNodeControl.nodeProps.get('location', 'localtimezone'))) > mySun['dusk']:
            return True """
        CurDateTime = datetime.datetime.now(pytz.timezone(oNodeControl.nodeProps.get('location', 'localtimezone')))
        if CurDateTime > mySun['sunset'] or CurDateTime < mySun['sunrise']: # avond en nacht
            return True
        else:
            return False

    except Exception as exp:
        oNodeControl.log.error("isDusk init error. Error %s." % (traceback.format_exc()))