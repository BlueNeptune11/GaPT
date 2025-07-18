from datetime import datetime

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

def format_data(orbit_path, moon_name):    
    """
    Format .TAB data into a pandas dataframe, add distance column.
    """
    # Header units: absolute time, magnetic fields in nT, coordinates of Moon radii
    header = ['Time', 'B_x', 'B_y', 'B_z', 'B', 'X', 'Y', 'Z']

    # Create pandas dataframe
    orbit_data = pd.read_csv(orbit_path, sep='\s+', names=header)

    #Add column distance to Moon's Surface in Moon radii
    orbit_data["Distance"] = np.sqrt(orbit_data["X"]**2 + orbit_data["Y"]**2 + orbit_data["Z"]**2) - 1
    
    orbit_data["moon"] = moon_name
    orbit_data["start date"] = datetime.strptime(orbit_data['Time'][0], '%Y-%m-%dT%H:%M:%S.%f').strftime('%B %e, %Y')

    return orbit_data

def wake_dates(orbit_data):
    """
    Find times at which spacecraft enters and leaves the solar wind wake of the moon.
    """
    wake_cond = (orbit_data['X'] > 0) & (np.sqrt(orbit_data['Y']**2 + orbit_data['Z']**2) < 1)
    return orbit_data[wake_cond]["Time"].min(), orbit_data[wake_cond]["Time"].max()

def choose_rad_symbol(orbit_data):
    if orbit_data['moon'][0] == 'Ganymede':
        rad = 'GAN'

    if orbit_data['moon'][0] == 'Europa':
        rad = 'EUR'

    if orbit_data['moon'][0] == 'Callisto':
        rad = 'CAL'

    if orbit_data['moon'][0] == 'Io':
        rad = 'Io'

    return rad

def plot_mag(orbit_data, fig, gs, i, mag, color='blue'):
    """
    Plot Magnetic field signal on a 5-tile gridspec figure.
    """
    time = np.asarray(orbit_data['Time'], np.datetime64)

    ax = fig.add_subplot(gs[i])
    ax.plot(time, orbit_data[f'{mag}'], color)
    ax.vlines(orbit_data[orbit_data["Distance"] == orbit_data["Distance"].min()]["Time"], 0, 1, 'black', transform=ax.get_xaxis_transform(), lw=1, ls='--')

    ax.axvspan(*wake_dates(orbit_data), color='grey', alpha=0.5)

    ax.set_ylabel(f'${mag}$ [nT]')

    ax.xaxis.set_major_formatter(mdates.DateFormatter(''))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(0,60,3), interval=2))
    ax.tick_params(direction='in')

    ax.margins(x=0, y=0)
    ax.grid(color='grey', alpha=0.3, ls='--')

    return ax

def plot_distance(orbit_data, fig, gs, i):
    """
    Plot Distance on a 5-tile gridspec figure.
    """
    rad = choose_rad_symbol(orbit_data)

    time = np.asarray(orbit_data['Time'], np.datetime64)

    ax = fig.add_subplot(gs[i])
    ax.plot(time, orbit_data['Distance'])
    ax.vlines(orbit_data[orbit_data["Distance"] == orbit_data["Distance"].min()]["Time"], 0, 1, 'black', transform=ax.get_xaxis_transform(), lw=1, ls='--')

    ax.axvspan(*wake_dates(orbit_data), color='grey', alpha=0.5)

    ax.set_xlabel('UTC')
    ax.set_ylabel(f"Distance [$R_{{{rad}}}$]")

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(0,60,3), interval=2))
    ax.tick_params(direction='in')

    ax.margins(x=0, y=0)
    ax.grid(color='grey', alpha=0.3, ls='--')


    return ax

def time_labels(orbit_data, points_number):
    # Find evenly spaced indices
    step = int(len(orbit_data)/points_number)
    start = int(step/2)

    # Select values of x,y,z,time for time labelling
    x_time, y_time, z_time = orbit_data["X"][start::step].to_numpy(), orbit_data["Y"][start::step].to_numpy(), orbit_data["Z"][start::step].to_numpy()

    # Label every second time point
    x_label, y_label, z_label = x_time[1::2], y_time[1::2], z_time[1::2]

    time_sliced = orbit_data["Time"][start::step]
    time_labels = np.asarray(time_sliced[1::2], '<U42')
    time_strings = np.array([
        datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f').strftime('%H:%M') 
        for date in time_labels
    ])

    return (x_time, y_time, z_time), (x_label, y_label, z_label), time_strings

def plot_traj(orbit_data, fig, gs, i, coords, flowdir='right', lim=7, label_num=9, date_offsets=[0,0]):
    """
    Plot orbital trajectory in XY, YZ or XZ dimensions on one of the 3 tiles of a gridspec figure.
    """

    rad = choose_rad_symbol(orbit_data)

    # Retrieve coordinates from the coords string
    coord1, coord2 = coords[0], coords[-1]

    # Flow direction logic to show the correct symbol
    if flowdir == 'right':
        flow_label = '$\longrightarrow$'
    elif flowdir == 'out':
        flow_label = '$\odot$'
    else:
        print('Flow direction keyword invalid')

    # Define x and y limits
    lim1 = -lim
    lim2 = lim

    # Create axis and plot the trajectory data
    ax = fig.add_subplot(gs[i])
    ax.plot(orbit_data[f"{coord1}"], orbit_data[f"{coord2}"])

    # Set axis labels and xy limits
    ax.set_xlabel(f"{coord1} [$R_{{{rad}}}$]")
    ax.set_ylabel(f"{coord2} [$R_{{{rad}}}$]")
    ax.set_xlim(lim1, lim2)
    ax.set_ylim(lim1, lim2)

    # Add Io's trace and shadow on the plot
    if coords == 'XY' or coords == 'XZ':
        ax.add_patch(mpatches.Rectangle((0, -1), lim, 2, facecolor='grey', alpha=0.4, fill=True))
    
    ax.add_patch(mpatches.Circle((0, 0), 1, facecolor='white', edgecolor='black', fill=True))

    # Add centric lines
    ax.hlines(0, lim1, lim2, 'grey', lw=.6, alpha=.6)
    ax.vlines(0, lim1, lim2, 'grey', lw=.6, alpha=.6)

    # Flow legend and symbol
    ax.text((5/7)*lim, (6/7)*lim, 'Flow', fontweight='bold')
    ax.text((4.8/7)*lim, (5/7)*lim, flow_label, fontweight='bold', fontsize='xx-large')

    xyz_coords, xyz_labels, time_strings = time_labels(orbit_data, label_num)

    # Plot trajectory points at specific times
    if coords == 'XY':
        ax.plot(xyz_coords[0], xyz_coords[1], 'k.')
    if coords == 'YZ':
        ax.plot(xyz_coords[1], xyz_coords[2], 'k.')
    if coords == 'XZ':
        ax.plot(xyz_coords[0], xyz_coords[2], 'k.')

    dx, dy = date_offsets

    # Draw time labels
    for label, x_label, y_label, z_label in zip(time_strings, *xyz_labels):
        if coords == 'XY':
            ax.annotate(label, (x_label, y_label), xytext=(x_label + dx, y_label + dy), textcoords='data')
        if coords == 'YZ':
            ax.annotate(label, (y_label, z_label), xytext=(y_label + dx, z_label + dy), textcoords='data')
        if coords == 'XZ':
            ax.annotate(label, (x_label, z_label), xytext=(x_label + dx, z_label + dy), textcoords='data')

    return ax