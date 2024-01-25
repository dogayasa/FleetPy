import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def demand_graphs():
    df0 = pd.read_csv("C:/Users/User/Desktop/FleetPy/data/demand/8_days_nyc_demand/matched/14_days_nyc_network/demand_nyc_2019_0.05.csv")
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

def shift_durations_graph(path):
    df = pd.read_csv(path + "4-0_work_summary.csv",  dtype={"taken_shift": int, "worked_today": float})
    fig, ax = plt.subplots()
    ax.boxplot(df.groupby('taken_shift')['worked_today'].apply(list))
    ax.set_yticks(range(0, int(df['worked_today'].max()) + 2000, 2000))
    ax.set_xticklabels(df['taken_shift'].unique()) 
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Number of the Taken Shift', fontsize=20)
    plt.ylabel('Shift Duration', fontsize=20)
    plt.show()
 
def shifts_on_days(path):
    df = pd.read_csv(path + "4-0_work_summary.csv",  dtype={"day": int, "worked_today": float})
    fig, ax = plt.subplots()
    ax.boxplot(df.groupby('day')['worked_today'].apply(list))
    ax.set_yticks(range(0, int(df['worked_today'].max()) + 2000, 2000))
    ax.set_xticklabels(df['day'].unique()) 
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Days', fontsize=20)
    plt.ylabel('Shift Duration', fontsize=20)
    plt.show()

def smallest_worked_today_on_day(path, target_day=4):
    # Read the CSV file
    df = pd.read_csv(path + "4-0_work_summary.csv", dtype={"day": int, "worked_today": float, "vehicle_id": str})

    # Filter data for the specified day
    df_target_day = df[df['day'] == target_day]

    # Find the row with the smallest 'worked_today' value on the target day
    min_row = df_target_day.loc[df_target_day['worked_today'].idxmin()]

    # Get the smallest 'worked_today' value and the associated vehicle ID
    smallest_worked_today = min_row['worked_today']
    smallest_vehicle_id = min_row['vehicle_id']

    # Visualize the data in a boxplot
    fig, ax = plt.subplots()
    ax.boxplot(df_target_day.groupby('day')['worked_today'].apply(list))
    ax.set_yticks(range(0, int(df['worked_today'].max()) + 2000, 2000))
    ax.set_xticklabels(df_target_day['day'].unique())
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel('Number of the Taken Shift', fontsize=20)
    plt.ylabel('Shift Duration', fontsize=20)
    plt.title(f'Smallest worked_today on Day {target_day}: {smallest_worked_today} (Vehicle ID: {smallest_vehicle_id})', fontsize=20)
    plt.show()

def bws_durations_graph(path):
    df = pd.read_csv(path + "5-0_break-stats.csv",  dtype={"taken_shift": float, "worked_today": float})
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

def do_base_availability_graph(path, fleet):
    df = pd.read_csv(path + "6-availablity-stats.csv")
    df['on_shift'] = df['driving'] + df['idle'] + df['reposition']
    df['on_break'] = df['break']
    df['on_shift_break'] = df['on shift break']
    df['remaining'] = fleet - (df['on_shift'] + df['on_break']+ df['on_shift_break'])

    tuesday = df[(df['simulation_time'] >= 86400) & (df['simulation_time'] < 172800)]
    filtered_df = tuesday[tuesday['simulation_time'] % 3600 == 0]
    filtered_df['simulation_time'] = filtered_df['simulation_time'] // 3600 
    filtered_df['simulation_time'] = filtered_df['simulation_time'] - 24 
    filtered_df.set_index('simulation_time', inplace=True)

    total_vehicles = fleet 
    filtered_df['on_break_pct'] = (filtered_df['on_break'] / total_vehicles) * 100
    filtered_df['on_shift_break_pct'] = (filtered_df['on_shift_break'] / total_vehicles) * 100
    filtered_df['on_shift_pct'] = (filtered_df['on_shift'] / total_vehicles) * 100
    filtered_df['remaining_pct'] = (filtered_df['remaining'] / total_vehicles) * 100
    filtered_df[['on_break_pct', 'on_shift_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)
    
    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
    plt.legend()
    plt.show()

    sunday = df[(df['simulation_time'] >= 518400) & (df['simulation_time'] < 604800)]
    filtered_df2 = sunday[sunday['simulation_time'] % 3600 == 0]
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] // 3600 
    filtered_df2['simulation_time'] = filtered_df2['simulation_time'] - 72
    filtered_df2.set_index('simulation_time', inplace=True)

    total_vehicles = 200 
    filtered_df2['on_break_pct'] = (filtered_df2['on_break'] / total_vehicles) * 100
    filtered_df2['on_shift_break_pct'] = (filtered_df2['on_shift_break'] / total_vehicles) * 100
    filtered_df2['on_shift_pct'] = (filtered_df2['on_shift'] / total_vehicles) * 100
    filtered_df2['remaining_pct'] = (filtered_df2['remaining'] / total_vehicles) * 100
    filtered_df2[['on_break_pct', 'on_shift_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)

    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
    plt.legend()
    plt.show()

    second_tuesday = df[(df['simulation_time'] >= 691200) & (df['simulation_time'] < 777600)]
    filtered_df3 = second_tuesday[second_tuesday['simulation_time'] % 3600 == 0]
    filtered_df3['simulation_time'] = filtered_df3['simulation_time'] // 3600 
    filtered_df3['simulation_time'] = filtered_df3['simulation_time'] - 24 
    filtered_df3.set_index('simulation_time', inplace=True)

    total_vehicles = fleet 
    filtered_df3['on_break_pct'] = (filtered_df3['on_break'] / total_vehicles) * 100
    filtered_df3['on_shift_break_pct'] = (filtered_df3['on_shift_break'] / total_vehicles) * 100
    filtered_df3['on_shift_pct'] = (filtered_df3['on_shift'] / total_vehicles) * 100
    filtered_df3['remaining_pct'] = (filtered_df3['remaining'] / total_vehicles) * 100
    filtered_df3[['on_break_pct', 'on_shift_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)
    
    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
    plt.legend()
    plt.show()

    second_sunday = df[(df['simulation_time'] >= 1123200) & (df['simulation_time'] < 1209600)]
    filtered_df4 = second_sunday[second_sunday['simulation_time'] % 3600 == 0]
    filtered_df4['simulation_time'] = filtered_df4['simulation_time'] // 3600 
    filtered_df4['simulation_time'] = filtered_df4['simulation_time'] - 72
    filtered_df4.set_index('simulation_time', inplace=True)

    total_vehicles = 200 
    filtered_df4['on_break_pct'] = (filtered_df4['on_break'] / total_vehicles) * 100
    filtered_df4['on_shift_break_pct'] = (filtered_df4['on_shift_break'] / total_vehicles) * 100
    filtered_df4['on_shift_pct'] = (filtered_df4['on_shift'] / total_vehicles) * 100
    filtered_df4['remaining_pct'] = (filtered_df4['remaining'] / total_vehicles) * 100
    filtered_df2[['on_break_pct', 'on_shift_break_pct', 'on_shift_pct', 'remaining_pct']].plot(kind='bar', stacked=True)

    plt.xticks(fontsize=15, rotation=0)
    plt.yticks(fontsize=15)
    plt.xlabel('Simulation Time (hours)', fontsize=20)
    plt.ylabel('Percentage of Fleet Availability', fontsize=20)
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
    
def max_abs_overtime_difference(path):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(path + "4-0_work_summary.csv")

    # Calculate the absolute difference between overtime_today and expected_overtime
    df['abs_overtime_difference'] = abs(df['overtime_today'] - df['expected_overtime'])

    # Find the row with the maximum absolute difference
    max_row = df.loc[df['abs_overtime_difference'].idxmax()]

    # Print the result
    print(f"Maximum absolute difference between overtime_today and expected_overtime:")
    print(max_row[['operator_id', 'vehicle_id', 'abs_overtime_difference']])

def max_charging_duration(path):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(path + "4_charging_stats.csv")

    # Assuming charging_duration is the sum of connection_duration for each row
    df['charging_duration'] = df['connection_duration']

    # Find the row with the maximum charging_duration
    max_row = df.loc[df['charging_duration'].idxmax()]

    # Print the result
    print(f"Maximum charging duration:")
    print(max_row[['time', 'event', 'station_id', 'ch_op_id', 'vid', 'op_id', 'veh_type', 'charging_duration']])

def parse_fleet_composition(fleet_composition):
    matches = re.findall(r'(\w+:\d+)', fleet_composition)
    car_types = {}

    for match in matches:
        car_type, count = match.split(':')
        car_types[car_type] = int(count)

    return car_types


def main_graph():
    scenario_files_directory = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/HeterogeneousFleet/scenarios/"
    scenarios = []
    bar_width = 0.2  # Width of each bar

    # Initialize lists to store values for each scenario
    index = []
    autonomous = []
    classic_day = []
    classic_night = []

    # scenario 10 - 90 --------------------------------------------
    scenario_path = scenario_files_directory + "3_8_days_HT.csv"
    df_scenario = pd.read_csv(scenario_path)
    row = df_scenario.iloc[0]
    fleet = row["op_fleet_composition"]
    scenario_name = row["scenario_name"]
    scenarios.append(scenario_name)

    number_of_cars = parse_fleet_composition(fleet)
    index.append(len(scenarios) - 1)
    autonomous.append(number_of_cars["2019_fiat_500e"] + number_of_cars["2019_nissan_leaf"] + number_of_cars["2022_bmw_i4"])
    classic_day.append(number_of_cars["2019_fiat_500e_day_driver_vehtype"] + number_of_cars["2019_nissan_leaf_day_driver_vehtype"] + number_of_cars["2022_bmw_i4_day_driver_vehtype"])
    classic_night.append(number_of_cars["2019_fiat_500e_night_driver_vehtype"] + number_of_cars["2019_nissan_leaf_night_driver_vehtype"] + number_of_cars["2022_bmw_i4_night_driver_vehtype"])

    # scenario 20 - 80 --------------------------------------------
    scenario_path = scenario_files_directory + "4_8_days_HT.csv"
    df_scenario = pd.read_csv(scenario_path)
    row = df_scenario.iloc[0]
    fleet = row["op_fleet_composition"]
    scenario_name = row["scenario_name"]
    scenarios.append(scenario_name)

    number_of_cars = parse_fleet_composition(fleet)
    index.append(len(scenarios) - 1)
    autonomous.append(number_of_cars["2019_fiat_500e"] + number_of_cars["2019_nissan_leaf"] + number_of_cars["2022_bmw_i4"])
    classic_day.append(number_of_cars["2019_fiat_500e_day_driver_vehtype"] + number_of_cars["2019_nissan_leaf_day_driver_vehtype"] + number_of_cars["2022_bmw_i4_day_driver_vehtype"])
    classic_night.append(number_of_cars["2019_fiat_500e_night_driver_vehtype"] + number_of_cars["2019_nissan_leaf_night_driver_vehtype"] + number_of_cars["2022_bmw_i4_night_driver_vehtype"])

    # scenario 30 - 70 --------------------------------------------
    scenario_path = scenario_files_directory + "5_8_days_HT.csv"
    df_scenario = pd.read_csv(scenario_path)
    row = df_scenario.iloc[0]
    fleet = row["op_fleet_composition"]
    scenario_name = row["scenario_name"]
    scenarios.append(scenario_name)

    number_of_cars = parse_fleet_composition(fleet)
    index.append(len(scenarios) - 1)
    autonomous.append(number_of_cars["2019_fiat_500e"] + number_of_cars["2019_nissan_leaf"] + number_of_cars["2022_bmw_i4"])
    classic_day.append(number_of_cars["2019_fiat_500e_day_driver_vehtype"] + number_of_cars["2019_nissan_leaf_day_driver_vehtype"] + number_of_cars["2022_bmw_i4_day_driver_vehtype"])
    classic_night.append(number_of_cars["2019_fiat_500e_night_driver_vehtype"] + number_of_cars["2019_nissan_leaf_night_driver_vehtype"] + number_of_cars["2022_bmw_i4_night_driver_vehtype"])

    # scenario 40 - 60 --------------------------------------------
    scenario_path = scenario_files_directory + "6_8_days_HT.csv"
    df_scenario = pd.read_csv(scenario_path)
    row = df_scenario.iloc[0]
    fleet = row["op_fleet_composition"]
    scenario_name = row["scenario_name"]
    scenarios.append(scenario_name)

    number_of_cars = parse_fleet_composition(fleet)
    index.append(len(scenarios) - 1)
    autonomous.append(number_of_cars["2019_fiat_500e"] + number_of_cars["2019_nissan_leaf"] + number_of_cars["2022_bmw_i4"])
    classic_day.append(number_of_cars["2019_fiat_500e_day_driver_vehtype"] + number_of_cars["2019_nissan_leaf_day_driver_vehtype"] + number_of_cars["2022_bmw_i4_day_driver_vehtype"])
    classic_night.append(number_of_cars["2019_fiat_500e_night_driver_vehtype"] + number_of_cars["2019_nissan_leaf_night_driver_vehtype"] + number_of_cars["2022_bmw_i4_night_driver_vehtype"])

    # scenario 50 - 50 --------------------------------------------
    scenario_path = scenario_files_directory + "7_8_days_HT.csv"
    df_scenario = pd.read_csv(scenario_path)
    row = df_scenario.iloc[0]
    fleet = row["op_fleet_composition"]
    scenario_name = row["scenario_name"]
    scenarios.append(scenario_name)

    number_of_cars = parse_fleet_composition(fleet)
    index.append(len(scenarios) - 1)
    autonomous.append(number_of_cars["2019_fiat_500e"] + number_of_cars["2019_nissan_leaf"] + number_of_cars["2022_bmw_i4"])
    classic_day.append(number_of_cars["2019_fiat_500e_day_driver_vehtype"] + number_of_cars["2019_nissan_leaf_day_driver_vehtype"] + number_of_cars["2022_bmw_i4_day_driver_vehtype"])
    classic_night.append(number_of_cars["2019_fiat_500e_night_driver_vehtype"] + number_of_cars["2019_nissan_leaf_night_driver_vehtype"] + number_of_cars["2022_bmw_i4_night_driver_vehtype"])

    # scenario 60 - 40 --------------------------------------------
    scenario_path = scenario_files_directory + "8_8_days_HT.csv"
    df_scenario = pd.read_csv(scenario_path)
    row = df_scenario.iloc[0]
    fleet = row["op_fleet_composition"]
    scenario_name = row["scenario_name"]
    scenarios.append(scenario_name)

    number_of_cars = parse_fleet_composition(fleet)
    index.append(len(scenarios) - 1)
    autonomous.append(number_of_cars["2019_fiat_500e"] + number_of_cars["2019_nissan_leaf"] + number_of_cars["2022_bmw_i4"])
    classic_day.append(number_of_cars["2019_fiat_500e_day_driver_vehtype"] + number_of_cars["2019_nissan_leaf_day_driver_vehtype"] + number_of_cars["2022_bmw_i4_day_driver_vehtype"])
    classic_night.append(number_of_cars["2019_fiat_500e_night_driver_vehtype"] + number_of_cars["2019_nissan_leaf_night_driver_vehtype"] + number_of_cars["2022_bmw_i4_night_driver_vehtype"])

    # scenario 70 - 30 --------------------------------------------
    scenario_path = scenario_files_directory + "9_8_days_HT.csv"
    df_scenario = pd.read_csv(scenario_path)
    row = df_scenario.iloc[0]
    fleet = row["op_fleet_composition"]
    scenario_name = row["scenario_name"]
    scenarios.append(scenario_name)

    number_of_cars = parse_fleet_composition(fleet)
    index.append(len(scenarios) - 1)
    autonomous.append(number_of_cars["2019_fiat_500e"] + number_of_cars["2019_nissan_leaf"] + number_of_cars["2022_bmw_i4"])
    classic_day.append(number_of_cars["2019_fiat_500e_day_driver_vehtype"] + number_of_cars["2019_nissan_leaf_day_driver_vehtype"] + number_of_cars["2022_bmw_i4_day_driver_vehtype"])
    classic_night.append(number_of_cars["2019_fiat_500e_night_driver_vehtype"] + number_of_cars["2019_nissan_leaf_night_driver_vehtype"] + number_of_cars["2022_bmw_i4_night_driver_vehtype"])

    # scenario 80 - 20 --------------------------------------------
    scenario_path = scenario_files_directory + "10_8_days_HT.csv"
    df_scenario = pd.read_csv(scenario_path)
    row = df_scenario.iloc[0]
    fleet = row["op_fleet_composition"]
    scenario_name = row["scenario_name"]
    scenarios.append(scenario_name)

    number_of_cars = parse_fleet_composition(fleet)
    index.append(len(scenarios) - 1)
    autonomous.append(number_of_cars["2019_fiat_500e"] + number_of_cars["2019_nissan_leaf"] + number_of_cars["2022_bmw_i4"])
    classic_day.append(number_of_cars["2019_fiat_500e_day_driver_vehtype"] + number_of_cars["2019_nissan_leaf_day_driver_vehtype"] + number_of_cars["2022_bmw_i4_day_driver_vehtype"])
    classic_night.append(number_of_cars["2019_fiat_500e_night_driver_vehtype"] + number_of_cars["2019_nissan_leaf_night_driver_vehtype"] + number_of_cars["2022_bmw_i4_night_driver_vehtype"])

    # scenario 90 - 10 --------------------------------------------
    scenario_path = scenario_files_directory + "11_8_days_HT.csv"
    df_scenario = pd.read_csv(scenario_path)
    row = df_scenario.iloc[0]
    fleet = row["op_fleet_composition"]
    scenario_name = row["scenario_name"]
    scenarios.append(scenario_name)

    number_of_cars = parse_fleet_composition(fleet)
    index.append(len(scenarios) - 1)
    autonomous.append(number_of_cars["2019_fiat_500e"] + number_of_cars["2019_nissan_leaf"] + number_of_cars["2022_bmw_i4"])
    classic_day.append(number_of_cars["2019_fiat_500e_day_driver_vehtype"] + number_of_cars["2019_nissan_leaf_day_driver_vehtype"] + number_of_cars["2022_bmw_i4_day_driver_vehtype"])
    classic_night.append(number_of_cars["2019_fiat_500e_night_driver_vehtype"] + number_of_cars["2019_nissan_leaf_night_driver_vehtype"] + number_of_cars["2022_bmw_i4_night_driver_vehtype"])

    fig, ax = plt.subplots()

    # Adjust x-axis positions for each set of bars
    bar1 = ax.bar([i - bar_width for i in index], autonomous, bar_width, label='Autonomous Cars', color='blue')
    bar2 = ax.bar(index, classic_day, bar_width, label='Cars with Day Shift Drivers', color='orange')
    bar3 = ax.bar([i + bar_width for i in index], classic_night, bar_width, label='Cars with Night Shift Drivers', color='green')

    # Set labels and title
    ax.set_xlabel('Scenarios')
    ax.set_ylabel('Number of Vehicles')
    ax.set_title('Fleet Compositions for %95 Customer Satisfaction')
    ax.set_xticks(index)
    ax.set_xticklabels(scenarios, rotation=45, ha='right')

    # Add legend
    ax.legend()

    # Show the plot
    plt.show()



def plot_experiment(path, fleet):
    shifts_on_days(path)
    bws_durations_graph(path)
    do_base_availability_graph(path, fleet)
    max_abs_overtime_difference(path)
    max_charging_duration(path)

if __name__ == "__main__":
    base_eight = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/DriversOnly/results/base_8_days_driversonly/"
    base_five  ="C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/DriversOnly/results/base_5_days_driversonly/"
    large ="C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/DriversOnly/results/base_5_days_driversonly_larger_fleet/"
    diff_shift = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/DriversOnly/results/shift_start_5_days_driversonly/"
    diff_shift_large = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/DriversOnly/results/shift_start_5_days_driversonly_larger_fleet/"
    base_two_weeks ="C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/DriversOnly/results/base_14_days_driversonly/"
    hetero_10_90 = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/HeterogeneousFleet/results/10-90_8_days_hetero/"
    hetero_20_80 = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/HeterogeneousFleet/results/20-80_8_days_hetero/"
    hetero_30_70 = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/HeterogeneousFleet/results/30-70_8_days_hetero/"
    hetero_40_60 = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/HeterogeneousFleet/results/40-60_8_days_hetero/"
    hetero_50_50 = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/HeterogeneousFleet/results/50-50_8_days_hetero/"
    hetero_60_40 = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/HeterogeneousFleet/results/60-40_8_days_hetero/"
    hetero_70_30 = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/HeterogeneousFleet/results/70-30_8_days_hetero/"
    hetero_80_20 = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/HeterogeneousFleet/results/80-20_8_days_hetero/"
    hetero_90_10 = "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/HeterogeneousFleet/results/90-10_8_days_hetero/"


    plot_experiment( "C:/Users/User/Desktop/TUM/External Projects/FleetPy/studies/HeterogeneousFleet/results/balance_hetero_30-70/", 100)
    #main_graph()
