import argparse
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
import constants as c
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import utils as u
import warnings

def build_gal_ring(R):
    theta = np.linspace(0, 2 * np.pi, 100)  

    # Initial ring in xy-plane (equatorial)
    x = R * np.cos(theta)
    y = R * np.sin(theta)
    z = np.zeros_like(theta)

    ra_gal = u.calc_right_asc(c.GAL_RA_HR, c.GAL_RA_MIN, c.GAL_RA_SEC)
    ra_gal = np.radians(ra_gal) 
    decl_gal = np.radians(c.GAL_DECL)

    # Rotate around z by right ascension
    Rz = np.array([
        [np.cos(ra_gal), -np.sin(ra_gal), 0],
        [np.sin(ra_gal), np.cos(ra_gal), 0],
        [0, 0, 1]
    ])

    # Rotate around x by declination
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(decl_gal), -np.sin(decl_gal)],
        [0, np.sin(decl_gal), np.cos(decl_gal)]
    ])

    coords = np.vstack([x, y, z])
    coords_rotated = Rx @ Rz @ coords 

    x_rot, y_rot, z_rot = coords_rotated
    
    return x_rot, y_rot, z_rot

def add_ring(fig, R, name='Galactic Plane', color='blue'):
    Xs, Ys, Zs = build_gal_ring(R)
    
    fig.add_trace(go.Scatter3d(
            x=Xs, y=Ys, z=Zs,
            mode='lines',
            line=dict(color=color, width=2),
            name=name
        ))

def main():
    parser = argparse.ArgumentParser(description='A compact utility for observing the local solar neighborhood')
    parser.add_argument('-s','--silent',help='Silences console output of stellar data',action='store_true')
    parser.add_argument('-r','--rings',help='Specify between [0-3] (inclusive) how many galactic rings to display',type=int,default=1,choices=range(0,4))
    args = parser.parse_args()
    
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
    
    colorama_init()

    near_star = pd.read_csv("./data/nearest_stars.csv")
    near_star = near_star.iloc()[2:-2]

    ra_pattern = r'(?P<hours>\d+)h\s(?P<minutes>\d+)m\s(?P<seconds>\d+\.?\d*)s'
    decl_pattern = r'(?P<degrees>[+\u002D\u2212\u2013]?\d+)°\s(?P<minutes>\d+)′\s(?P<seconds>\d+)″'

    Xs = np.empty(0)
    Ys = np.empty(0)
    Zs = np.empty(0)
    masses = np.empty(0)
    
    silent = args.silent
    
    for _, row in near_star.iterrows():
        curr_dist = row[2]
        curr_dist = float(curr_dist.split("\n")[0])
        parsecs = curr_dist*c.LY2PARSEC
        
        curr_cord = row[4]
        right_asc, decl = curr_cord.split("\n")
        
        curr_mass = row[6]
        curr_mass = float(curr_mass)
        masses = np.append(masses, curr_mass)
        
        if not silent:
            print(f'{Fore.MAGENTA}[Distance]{Style.RESET_ALL} {Fore.CYAN}{curr_dist:.3f} ly{Style.RESET_ALL}, {Fore.CYAN}{parsecs:.3f} pc{Style.RESET_ALL}')
            print(f"{Fore.YELLOW}[Eqt Cord]{Style.RESET_ALL} right ascension: {Fore.GREEN}{right_asc}{Style.RESET_ALL}, declination: {Fore.GREEN}{decl}{Style.RESET_ALL}")

        ra_hr, ra_min, ra_sec = u.match_pattern(ra_pattern,right_asc,deg_val=False)
        decl_deg, decl_min, decl_sec = u.match_pattern(decl_pattern,decl)
            
        right_asc = u.calc_right_asc(ra_hr, ra_min, ra_sec)
        decl = u.calc_decl(decl_deg, decl_min, decl_sec)
        
        if not silent:
            print(f"{Fore.YELLOW}[Deg]{Style.RESET_ALL} right ascension: {Fore.GREEN}{right_asc:.3f}°{Style.RESET_ALL}, declination: {Fore.GREEN}{decl:.3f}°{Style.RESET_ALL}")
        
        x, y, z = u.sph_cord2cart(parsecs, right_asc, decl)
        Xs = np.append(Xs,x)
        Ys = np.append(Ys,y)
        Zs = np.append(Zs,-z) # Negate Z to flip axis
        
    if len(near_star) == len(Xs) == len(Ys) == len(Zs) == len(masses):
        near_star['x'] = Xs
        near_star['y'] = Ys
        near_star['z'] = Zs
        near_star['mass'] = masses
    else:
        print("Error: failed to process new columns of near_star DataFrame")
        sys.exit()
        
    near_star['stellar_class'] = near_star['Stellar\nclass'].str[0]
    
    label_dict = {'x': 'X (Parsecs)',
                    'y': 'Y (Parsecs)',
                    'z': 'Z (Parsecs)'}
    
    fig = px.scatter_3d(near_star, x='x', y='y', z='z', title='SolarNeighborhood Navigator', 
                        hover_name='Designation', size='mass', color='stellar_class', 
                        color_discrete_map=c.COLOR_MAP, labels=label_dict)
    fig.update_layout(template='plotly_dark')
    
    num_rings = args.rings
    if num_rings == 1:
        add_ring(fig,6)
    elif num_rings > 1:
        names = ['Galactic Plane (6pc)', 'Galactic Plane (4pc)', 'Galactic Plane (2pc)']
        radii = [6,4,2]
        colors = ['blue','cyan','lightgreen']
        for r in range(num_rings):
            add_ring(fig,radii[r],name=names[r],color=colors[r])
    
    fig.show()
        
if __name__ == "__main__":
    main()