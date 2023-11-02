import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def demand_graphs():
    df0 = pd.read_csv("C:/Users/User/Desktop/FleetPy/data/demand/8_days_nyc_demand/matched/8_days_nyc_network/demand_nyc_2019_0.05.csv")
    df0['rq_time'] = df0['rq_time'].div(3600)

    ranges = np.arange(0, 193, 1, dtype=int)
    df0['hour_intervals'] = pd.cut(df0['rq_time'], ranges, right=False)

    count_data = pd.DataFrame()
    count_data['counts'] = df0['hour_intervals'].value_counts().sort_index().values
    count_data['hours'] = ranges[:-1]

    ax = count_data.plot.bar(x="hours", y="counts", color='darkblue', edgecolor='black', width=1)
    xticks = np.arange(0, len(count_data), 6) 
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks, rotation = 0, fontsize=14)

    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Time in [h]', fontsize=20)
    plt.ylabel('Requests', fontsize=20)
    plt.show()

def shift_durations_graph():
    df = pd.read_csv("C:/Users/User/Desktop/FleetPy/studies/DriversOnly/results/base_8_days_driversonly/4-0_work_summary.csv",  dtype={"on_which_day": int, "worked_today": float})
    fig, ax = plt.subplots()
    ax.boxplot(df.groupby('on_which_day')['worked_today'].apply(list))
    ax.set_yticks(range(0, int(df['worked_today'].max()) + 2000, 2000))
    ax.set_xticklabels(df['on_which_day'].unique()) 
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Number of the Taken Shift', fontsize=20)
    plt.ylabel('Shift Duration', fontsize=20)
    plt.show()
 
def bws_durations_graph():
    df = pd.read_csv("C:/Users/User/Desktop/FleetPy/studies/DriversOnly/results/base_8_days_driversonly/5-0_break-stats.csv",  dtype={"on_which_day": float, "worked_today": float})
    filtered_df = df[df['status'] == 'on_shift_break']
    filtered_df['selected_bws_break_duration'] = filtered_df['selected_bws_break_duration'].div(3600)  # Convert seconds to hours
    bins = [5, 10, 15, 20, 25, np.inf]
    labels = ['[5-9]', '[10-14]', '[15-19]', '[20-24]', '[25<=]']
    grouped_df = filtered_df.groupby(pd.cut(filtered_df['selected_bws_break_duration'], bins=bins, labels=labels)).size().reset_index(name='count')
    plt.bar(grouped_df['selected_bws_break_duration'], grouped_df['count'])
    plt.xlabel('Between-Shift-Break Durations in Hours', fontsize=20)
    plt.ylabel('Number of Between-Shift-Breaks', fontsize=20)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.show()

def do_base_availability_graph():
    df = pd.read_csv("C:/Users/User/Desktop/FleetPy/studies/DriversOnly/results/base_5_days_driversonly/6-availablity-stats.csv")
    df['on_shift'] = df['driving'] + df['idle'] + df['reposition']
    df['on_break'] = df['break'] + df['on shift break']
    df['remaining'] = 200 - (df['on_shift'] + df['on_break'])

    second_day = df[(df['simulation_time'] >= 86400) & (df['simulation_time'] < 172800)]
    filtered_df = second_day[second_day['simulation_time'] % 3600 == 0]
    filtered_df['simulation_time'] = filtered_df['simulation_time'] // 3600 
    filtered_df['simulation_time'] = filtered_df['simulation_time'] - 24 
    filtered_df.set_index('simulation_time', inplace=True)

    total_vehicles = 200 
    filtered_df['on_break_pct'] = (filtered_df['on_break'] / total_vehicles) * 100
    filtered_df['on_shift_pct'] = (filtered_df['on_shift'] / total_vehicles) * 100
    filtered_df['remaining_pct'] = (filtered_df['remaining'] / total_vehicles) * 100
    filtered_df[['on_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)
    
    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
    plt.legend()
    plt.show()

    fourth_day = df[(df['simulation_time'] >= 259200) & (df['simulation_time'] < 345600)]
    filtered_df2 = fourth_day[fourth_day['simulation_time'] % 3600 == 0]
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] // 3600 
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] - 72
    filtered_df2.set_index('simulation_time', inplace=True)

    total_vehicles = 200 
    filtered_df2['on_break_pct'] = (filtered_df2['on_break'] / total_vehicles) * 100
    filtered_df2['on_shift_pct'] = (filtered_df2['on_shift'] / total_vehicles) * 100
    filtered_df2['remaining_pct'] = (filtered_df2['remaining'] / total_vehicles) * 100
    filtered_df2[['on_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)

    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
    plt.legend()
    plt.show()

def do_base_lf_availability_graph():
    df = pd.read_csv("C:/Users/User/Desktop/FleetPy/studies/DriversOnly/results/base_5_days_driversonly_larger_fleet/6-availablity-stats.csv")
    df['on_shift'] = df['driving'] + df['idle'] + df['reposition']
    df['on_break'] = df['break'] + df['on shift break']
    df['remaining'] = 525 - (df['on_shift'] + df['on_break'])

    second_day = df[(df['simulation_time'] >= 86400) & (df['simulation_time'] < 172800)]
    filtered_df = second_day[second_day['simulation_time'] % 3600 == 0]
    filtered_df['simulation_time'] = filtered_df['simulation_time'] // 3600 
    filtered_df['simulation_time'] = filtered_df['simulation_time'] - 24 
    filtered_df.set_index('simulation_time', inplace=True)

    total_vehicles = 525 
    filtered_df['on_break_pct'] = (filtered_df['on_break'] / total_vehicles) * 100
    filtered_df['on_shift_pct'] = (filtered_df['on_shift'] / total_vehicles) * 100
    filtered_df['remaining_pct'] = (filtered_df['remaining'] / total_vehicles) * 100
    filtered_df[['on_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)
    
    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
    plt.legend()
    plt.show()

    fourth_day = df[(df['simulation_time'] >= 259200) & (df['simulation_time'] < 345600)]
    filtered_df2 = fourth_day[fourth_day['simulation_time'] % 3600 == 0]
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] // 3600 
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] - 72
    filtered_df2.set_index('simulation_time', inplace=True)

    total_vehicles = 525 
    filtered_df2['on_break_pct'] = (filtered_df2['on_break'] / total_vehicles) * 100
    filtered_df2['on_shift_pct'] = (filtered_df2['on_shift'] / total_vehicles) * 100
    filtered_df2['remaining_pct'] = (filtered_df2['remaining'] / total_vehicles) * 100
    filtered_df2[['on_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)

    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
    plt.legend()
    plt.show()

def do_sh_availability_graph():
    df = pd.read_csv("C:/Users/User/Desktop/FleetPy/studies/DriversOnly/results/shift_start_5_days_driversonly/6-availablity-stats.csv")
    df['on_shift'] = df['driving'] + df['idle'] + df['reposition']
    df['on_break'] = df['break'] + df['on shift break']
    df['remaining'] = 200 - (df['on_shift'] + df['on_break'])

    second_day = df[(df['simulation_time'] >= 86400) & (df['simulation_time'] < 172800)]
    filtered_df = second_day[second_day['simulation_time'] % 3600 == 0]
    filtered_df['simulation_time'] = filtered_df['simulation_time'] // 3600 
    filtered_df['simulation_time'] = filtered_df['simulation_time'] - 24 
    filtered_df.set_index('simulation_time', inplace=True)

    total_vehicles = 200 
    filtered_df['on_break_pct'] = (filtered_df['on_break'] / total_vehicles) * 100
    filtered_df['on_shift_pct'] = (filtered_df['on_shift'] / total_vehicles) * 100
    filtered_df['remaining_pct'] = (filtered_df['remaining'] / total_vehicles) * 100
    filtered_df[['on_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)
    
    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
    plt.legend()
    plt.show()

    fourth_day = df[(df['simulation_time'] >= 259200) & (df['simulation_time'] < 345600)]
    filtered_df2 = fourth_day[fourth_day['simulation_time'] % 3600 == 0]
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] // 3600 
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] - 72
    filtered_df2.set_index('simulation_time', inplace=True)

    total_vehicles = 200 
    filtered_df2['on_break_pct'] = (filtered_df2['on_break'] / total_vehicles) * 100
    filtered_df2['on_shift_pct'] = (filtered_df2['on_shift'] / total_vehicles) * 100
    filtered_df2['remaining_pct'] = (filtered_df2['remaining'] / total_vehicles) * 100
    filtered_df2[['on_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)

    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
    plt.legend()
    plt.show()

def do_sh_lf_availability_graph():
    df = pd.read_csv("C:/Users/User/Desktop/FleetPy/studies/DriversOnly/results/shift_start_5_days_driversonly_larger_fleet/6-availablity-stats.csv")
    df['on_shift'] = df['driving'] + df['idle'] + df['reposition']
    df['on_break'] = df['break'] + df['on shift break']
    df['remaining'] = 425 - (df['on_shift'] + df['on_break'])

    second_day = df[(df['simulation_time'] >= 86400) & (df['simulation_time'] < 172800)]
    filtered_df = second_day[second_day['simulation_time'] % 3600 == 0]
    filtered_df['simulation_time'] = filtered_df['simulation_time'] // 3600 
    filtered_df['simulation_time'] = filtered_df['simulation_time'] - 24 
    filtered_df.set_index('simulation_time', inplace=True)

    total_vehicles = 425 
    filtered_df['on_break_pct'] = (filtered_df['on_break'] / total_vehicles) * 100
    filtered_df['on_shift_pct'] = (filtered_df['on_shift'] / total_vehicles) * 100
    filtered_df['remaining_pct'] = (filtered_df['remaining'] / total_vehicles) * 100
    filtered_df[['on_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)
    
    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
    plt.legend()
    plt.show()

    fourth_day = df[(df['simulation_time'] >= 259200) & (df['simulation_time'] < 345600)]
    filtered_df2 = fourth_day[fourth_day['simulation_time'] % 3600 == 0]
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] // 3600 
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] - 72
    filtered_df2.set_index('simulation_time', inplace=True)

    total_vehicles = 425 
    filtered_df2['on_break_pct'] = (filtered_df2['on_break'] / total_vehicles) * 100
    filtered_df2['on_shift_pct'] = (filtered_df2['on_shift'] / total_vehicles) * 100
    filtered_df2['remaining_pct'] = (filtered_df2['remaining'] / total_vehicles) * 100
    filtered_df2[['on_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)

    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
    plt.legend()
    plt.show()

def ht_availability_graph():
    df = pd.read_csv("C:/Users/User/Desktop/FleetPy/studies/HeterogeneousFleet/results/base_5_days_hetero/6-availablity-stats.csv")
    df['on_shift'] = df['driving'] + df['idle'] + df['reposition']
    df['on_break'] = df['break'] + df['on shift break']
    df['remaining'] = 200 - (df['on_shift'] + df['on_break'])

    second_day = df[(df['simulation_time'] >= 86400) & (df['simulation_time'] < 172800)]
    filtered_df = second_day[second_day['simulation_time'] % 3600 == 0]
    filtered_df['simulation_time'] = filtered_df['simulation_time'] // 3600 
    filtered_df['simulation_time'] = filtered_df['simulation_time'] - 24 
    filtered_df.set_index('simulation_time', inplace=True)
    ax = filtered_df[['on_break', 'on_shift', 'remaining']].plot(kind='bar', stacked=True)
    plt.xlabel('Simulation Time (hours)')
    plt.ylabel('Number of Vehicles')
    plt.title('Fleet Availability in Base Scenario with Heterogeneous Fleet on Thursday')
    plt.legend()
    plt.show()

    fourth_day = df[(df['simulation_time'] >= 259200) & (df['simulation_time'] < 345600)]
    filtered_df2 = fourth_day[fourth_day['simulation_time'] % 3600 == 0]
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] // 3600 
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] - 72
    filtered_df2.set_index('simulation_time', inplace=True)
    ax2 = filtered_df2[['on_break', 'on_shift', 'remaining']].plot(kind='bar', stacked=True)
    plt.xlabel('Simulation Time (hours)')
    plt.ylabel('Number of Vehicles')
    plt.title('Fleet Availability in Base Scenario with Heterogeneous Fleet on Saturday')
    plt.legend()
    plt.show()

def ht_sf_availability_graph():
    df = pd.read_csv("C:/Users/User/Desktop/FleetPy/studies/HeterogeneousFleet/results/smaller_fleet_5_days_hetero/6-availablity-stats.csv")
    # Create the 'on_shift' column
    df['on_shift'] = df['driving'] + df['idle'] + df['reposition']
    # Create the 'on_break' column
    df['on_break'] = df['break'] + df['on shift break']
    # Create the 'remaining' column
    df['remaining'] = 75 - (df['on_shift'] + df['on_break'])

    # Filter rows based on simulation time
    second_day = df[(df['simulation_time'] >= 86400) & (df['simulation_time'] < 172800)]
    filtered_df = second_day[second_day['simulation_time'] % 3600 == 0]
    # Divide simulation time by 3600 and round to the nearest whole number
    filtered_df['simulation_time'] = filtered_df['simulation_time'] // 3600 
    filtered_df['simulation_time'] = filtered_df['simulation_time'] - 24 
    filtered_df.set_index('simulation_time', inplace=True)
    ax = filtered_df[['on_break', 'on_shift', 'remaining']].plot(kind='bar', stacked=True)
    plt.xlabel('Simulation Time (hours)')
    plt.ylabel('Number of Vehicles')
    plt.title('Fleet Availability in Base Scenario with Heterogeneous Fleet on Thursday')
    plt.legend()
    plt.show()

    # Filter rows based on simulation time
    fourth_day = df[(df['simulation_time'] >= 259200) & (df['simulation_time'] < 345600)]
    filtered_df2 = fourth_day[fourth_day['simulation_time'] % 3600 == 0]
    # Divide simulation time by 3600 and round to the nearest whole number
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] // 3600 
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] - 72
    filtered_df2.set_index('simulation_time', inplace=True)
    ax2 = filtered_df2[['on_break', 'on_shift', 'remaining']].plot(kind='bar', stacked=True)
    plt.xlabel('Simulation Time (hours)')
    plt.ylabel('Number of Vehicles')
    plt.title('Fleet Availability in Base Scenario with Heterogeneous Fleet on Saturday')
    plt.legend()
    plt.show()

def passenger_satisfaction():
    data = {'y': [0.933592, 0.953284], 'x': ['Default Shift', 'Optimized Shift']}
    df = pd.DataFrame(data)
    plt.bar(df['x'], df['y'], width=0.4)  # Adjust the width as desired
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Shift Start Type', fontsize=20)
    plt.ylabel('Served Online Users [%]', fontsize=20)
    plt.ylim(0.9, 0.96) 
    plt.show()

    data2 = {'y':[93.3592, 100, 95.3284, 100, 100, 100], 'x': ['Default [200]', 'Default [525]', 'Optimized [200]', 'Optimized [425]', 'Autonomous [50]', "Hetero [75]"]}
    df = pd.DataFrame(data2)
    plt.bar(df['x'], df['y'], width=0.4) 
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Shift Start Type', fontsize=20)
    plt.ylabel('Served Online Users [%]', fontsize=20)
    plt.ylim(90, 100)  
    plt.show()
    

if __name__ == "__main__":

    demand_graphs()
    shift_durations_graph()
    bws_durations_graph()
    do_base_availability_graph()
    do_base_lf_availability_graph()
    do_sh_availability_graph()
    do_sh_lf_availability_graph()
    ht_availability_graph()
    ht_sf_availability_graph()
    passenger_satisfaction()