# author: Alp Sayin
# mail: alpsayin[at]gmail
# sources:
# http://www.movable-type.co.uk/scripts/latlong.html
# http://gis.stackexchange.com/questions/29239/calculate-bearing-between-two-decimal-gps-coordinates
# 31.07.2013

import math
from math import sin, cos, acos, tan, atan2, sqrt, radians, degrees, asin, floor, log, pi

R = 6371 #km

def convertHMStoDecimal( hms):
    h = hms[0]
    m = hms[1]
    s = hms[2]
    if h < 0:
        sign = -1
    else:
        sign = 1
    dec = (h + (m/60.0) + (s/3600.0) ) * sign#/1000000.0;
    return round(dec, 6)

def convertDecimaltoHMS( dec):
    if dec < 0:
        sign = -1
    else:
        sign= 1

    h = floor(dec ) * sign
    m = floor(  ((dec) - floor(dec)) * 60) 
    s = round( floor(((((dec) - floor(dec)) * 60) - floor(((dec) - floor(dec)) * 60)) * 100000) * 60/100000, 2) 
    return (h, m, s)

class Gps(object):
    """a simple gps class for holding lat and long and calculating distances and locations"""
    def __init__(self, lat=0.0, lon=0.0, alt=0.0):
        super(Gps, self).__init__()
        self.lat = round(float(lat), 6)
        self.lon = round(float(lon), 6)
        self.alt = round(float(alt), 6)

    def get_lattitude(self):
        return self.lat

    def get_longtitude(self):
        return self.lon

    def get_altitude(self):
        return self.alt

    def distanceTo(self, otherGps):
        '''result in meters'''
        deltaLatRad = radians(self.lat-otherGps.lat)
        deltaLonRad = radians(self.lon-otherGps.lon)
        lat1Rad = radians(self.lat)
        lat2Rad = radians(otherGps.lat)
        lon1Rad = radians(self.lon)
        lon2Rad = radians(otherGps.lon)

        # Spherical law of cosines
        d = acos( (sin(lat1Rad)*sin(lat2Rad)) + (cos(lat1Rad)*cos(lat2Rad)*cos(lon2Rad-lon1Rad))) * R;

        # Haversine formula
        # a = (sin(deltaLatRad/2) * sin(deltaLatRad/2)) + (sin(deltaLonRad/2) * sin(deltaLonRad/2) * cos(lat1Rad) * cos(lat2Rad))
        # c = 2 * atan2(sqrt(a), sqrt(1-a))
        # d = R * c
        return d*1000

    def bearingTo(self, otherGps):
        deltaLon = radians(otherGps.lon) - radians(self.lon)
        deltaLat = radians(otherGps.lat) - radians(self.lat)
        lat1 = radians(self.lat)
        lat2 = radians(otherGps.lat)
        # http://gis.stackexchange.com/questions/29239/calculate-bearing-between-two-decimal-gps-coordinates
        dPhi = log(tan(lat2/2.0+pi/4.0)/tan(lat1/2.0+pi/4.0))
        if abs(deltaLon) > pi:
            if deltaLon > 0.0:
                deltaLon = -(2.0 * pi - deltaLon)
            else:
                deltaLon = (2.0 * pi + deltaLon)

        bearing = (degrees(atan2(deltaLon, dPhi)) + 360.0) % 360.0
        return round(bearing, 6)

    def locationOf(self, bearing, distance):
        '''bearing in degrees, distance in meters'''
        distance_km = distance/1000.0
        bearing_r = radians(bearing)
        lat1 = radians(self.lat)
        lon1 = radians(self.lon)
        lat2 = asin( (sin(lat1)*cos(distance_km/R)) + (cos(lat1)*sin(distance_km/R)*cos(bearing_r)) )
        lon2 = lon1 + atan2( sin(bearing_r) * sin(distance_km/R) * cos(lat1), cos(distance_km/R) - (sin(lat1)*sin(lat2)) );
        return Gps(lat=degrees(lat2), lon=degrees(lon2))

    def isInBoundingCircle(self, otherGps, radius):
        '''radius in meters'''
        return self.distanceTo(otherGps) <= radius

    def generateWaypointFile(self, altitude, commit=False, filename='wp.txt'):
        template = '''QGC WPL 110
0   0   3   16  0.000000    0.000000    0.000000    0.000000    lat lon 0.000000    1
1   0   3   16  0.000000    0.000000    0.000000    0.000000    lat lon alt 1
2   1   3   17  0.000000    0.000000    0.000000    0.000000    0.000000    0.000000    0.000000    1
3   0   3   20  0.000000    0.000000    0.000000    0.000000    0.000000    0.000000    0.000000    1'''
        template = template.replace('lat', str(self.get_lattitude()))
        template = template.replace('lon', str(self.get_longtitude()))
        template = template.replace('alt', str(float(altitude)))
        if commit:
            wpfile = open( filename, 'w')
            wpfile.write(template)
            wpfile.close()
        return filename

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        lathms = convertDecimaltoHMS(self.lat)
        lonhms = convertDecimaltoHMS(self.lon)
        return 'D('+str(self.lat)+', '+str(self.lon)+') : HMS'+str(lathms)+', '+ str(lonhms)

if __name__ == '__main__':
    coordHms1 = ( (39,52,4.35), (32,45,5.27))
    coordHms2 = ( (39,52,7.79), (32,45,11.68))
    print('HMS 1 -> ' + str(coordHms1))
    print('HMS 2 -> ' + str(coordHms2))
    coordDec1 = ( convertHMStoDecimal(coordHms1[0]), convertHMStoDecimal(coordHms1[1]))
    coordDec2 = ( convertHMStoDecimal(coordHms2[0]), convertHMStoDecimal(coordHms2[1]))
    print('Dec 1 ->' + str(coordDec1))
    print('Dec 2 ->' + str(coordDec2))
    backHms1 = ( convertDecimaltoHMS(coordDec1[0]), convertDecimaltoHMS(coordDec1[1]))
    backHms2 = ( convertDecimaltoHMS(coordDec2[0]), convertDecimaltoHMS(coordDec2[1]))
    print('HMS 1 -> ' + str(backHms1))
    print('HMS 2 -> ' + str(backHms2))
    loc1 = Gps( coordDec1[0], coordDec1[1] )
    loc2 = Gps( coordDec2[0], coordDec2[1] )
    distance = loc1.distanceTo(loc2)
    bearing1 = loc1.bearingTo(loc2)
    bearing2 = loc2.bearingTo(loc1)
    print('distance: ' + str(distance))
    print('bearing12: ' + str(bearing1))
    print('bearing12: ' + str(convertDecimaltoHMS(bearing1)))
    print('bearing21: ' + str(bearing2))
    print('bearing21: ' + str(convertDecimaltoHMS(bearing2)))
    loc2fromDistance = loc1.locationOf(bearing1, distance)
    loc1fromDistance = loc2.locationOf(bearing2, distance)
    print(loc1)
    print(loc1fromDistance)
    print(loc2 )
    print(loc2fromDistance)
    
    balciLatHms = (39, 53, 23.23)
    balciLonHms = (32, 46, 30.70)
    balciLatDec = convertHMStoDecimal(balciLatHms)
    balciLonDec = convertHMStoDecimal(balciLonHms)
    balci = Gps(balciLatDec, balciLonDec)
    bodrumLatHms = (37, 1, 49.38)
    bodrumLonHms = (27, 25, 1.41)
    bodrumLatDec = convertHMStoDecimal(bodrumLatHms)
    bodrumLonDec = convertHMStoDecimal(bodrumLonHms)
    bodrum = Gps(bodrumLatDec, bodrumLonDec)
    bodrum = Gps(bodrumLatDec, bodrumLonDec)
    print('balci : '+str(balci))
    print('bodrum : '+str(bodrum))
    distance = balci.distanceTo(bodrum)/1000
    bearing = balci.bearingTo(bodrum)
    print('distance: '+str(distance))
    print('bearing: '+str(bearing))
    balci.generateWaypointFile(100, True)
    
