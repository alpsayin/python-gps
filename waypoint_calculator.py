#aaaa
import math
import time
import sys
from gps import Gps
  
def convert_image_location_to_waypoints( current_location, x_size, y_size, x_loc, y_loc): #altitude in meters
  '''
  creates triangular waypoints from a point in a rectangle and a current gps location

  current_location is gps object
  x_size, y_size, x_loc, y_loc are integers
  '''
  currentLat = current_location.get_lattitude()
  currentLon = current_location.get_longtitude()
  altitude = current_location.get_altitude()
  hor_size,ver_size = fov(2.8,5,4.28,5.7,altitude) #goPro hd hero specs
  speed = 1
  x_median = x_size/2
  y_median = y_size/2
  
  # print 'center: ', x_median,',', y_median
  x_diff = x_loc - x_median
  y_diff = y_loc - y_median
  
  hor_diff = realx(x_size,x_diff,hor_size)
  ver_diff = realy(y_size,y_diff,ver_size)
  # print 'horver diff', hor_diff, ver_diff
  
  horFollower1,verFollower1 = follower(hor_diff,ver_diff,altitude, 0)
  horFollower2,verFollower2 = follower(hor_diff,ver_diff,altitude,1)

  lat1,lon1 = offset(currentLat,currentLon,hor_diff,ver_diff)
  lat2,lon2 = offset(currentLat,currentLon,horFollower1,verFollower1)
  lat3,lon3 = offset(currentLat,currentLon,horFollower2,verFollower2)

  alpha = Gps( lat1, lon1)
  side1 = Gps( lat2, lon2)
  side2 = Gps( lat3, lon3)

  return (alpha, side1, side2)

def realx(x_size,x_diff,hor_size):
  return (x_diff*hor_size)/x_size
  
def realy(y_size,y_diff,ver_size):
  return (y_diff*ver_size)/y_size

def fov(N,f,h,v,alt): #N:focal number, f:focal dist, h-v: sensor size hor/ver, alt:altitude  
  D=f/N
  h_angle=2*math.atan2(h,2*f)
  v_angle=2*math.atan2(v,2*f)
  hor = math.tan(h_angle)*alt
  ver = math.tan(v_angle)*alt
  return (hor,ver)
  
def offset(lat,lon,hor_diff,ver_diff):
  R=6378137 #earth's radius
  newLat = lat + (hor_diff/R)*180/math.pi
  newLon = lon + (ver_diff/(R*math.cos(math.pi*lat/180))*(180/math.pi))
  return (newLat, newLon)
  
def follower(x,y,alt,fnum): #target coordinates, altitude, fnum: 0 if first follower, 1 if second
  if(alt<50):
    alt = 50
  r,deg = polar(x,y)
  opp = alt/4.0
  adj = r-alt*math.sqrt(3.0)/4.0
  theta = 180.0*math.atan2(adj,opp)
  r2d2 = math.sqrt(opp**2 + adj**2)
  if fnum:
    ang = deg + theta
  else:
    ang = deg - theta
    
  return rect(r2d2, ang)
  
def rect(r, w):
  w = math.pi * w / 180.0
  return r * math.cos(w), r * math.sin(w)        
    
def polar(x, y):
  return math.hypot(x, y), 180.0*math.atan2(y, x)/math.pi

if __name__ == "__main__":
   print convert_image_location_to_waypoints(640,480,323,244)

  