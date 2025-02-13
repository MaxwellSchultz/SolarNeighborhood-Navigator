import constants as c
import math
import re
import sys

def calc_right_asc(ra_hr, ra_min, ra_sec):
    return (ra_hr + (ra_min*c.MIN2HR) + (ra_sec*c.SEC2HR))*c.RA2DEG

def calc_decl(decl_deg, decl_min, decl_sec):
    if decl_deg >= 0:
        return decl_deg + (decl_min*c.AMIN2DEG) + (decl_sec*c.ASEC2DEG)
    else:
        return decl_deg - (decl_min*c.AMIN2DEG) - (decl_sec*c.ASEC2DEG)

def match_pattern(pattern, coordinates, deg_val=True):
    match = re.match(pattern, coordinates)
    if match:
        if deg_val:
            deg = match.group('degrees')
            deg = deg.replace('−', '-').replace('–','-')
            deg = deg.replace('+','')
            deg = int(deg)
        else:
            deg = int(match.group('hours'))
        min = int(match.group('minutes'))
        sec = float(match.group('seconds'))
        
        return deg, min, sec
    else:
        print(f"Error: failed to match galactic coordinate {coordinates}")
        sys.exit(2)
        
def sph_cord2cart(r,theta,phi):
        x = r * math.sin(math.radians(theta)) * math.cos(math.radians(phi))
        y = r * math.sin(math.radians(theta)) * math.sin(math.radians(phi))
        z = r * math.cos(math.radians(theta))
        
        return x, y, z