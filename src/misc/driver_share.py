fleet_size = 1000 # Total number of vehicles in the fleet
auto_share = 10 # Percentage of AVs in the fleet

# Shares of day and night drivers are obtained from a reference.
day_driver_share = 0.45
night_driver_share = 0.35
hybrid_driver_share = 0.2
types_of_car = 3

# Driver share is the remaining share after auto share
driver_share = 100 - auto_share

# Calculate total AVs and drivers
total_auto = fleet_size * auto_share / 100
total_driver = fleet_size * driver_share / 100

# Split AVs by vehicle type
auto_split = total_auto / types_of_car

# Obtain day and night drivers
day_driver = total_driver * day_driver_share
night_driver = total_driver * night_driver_share
hybrid_driver = total_driver * hybrid_driver_share

# Split day drivers by vehicle type
day_driver_split = day_driver / types_of_car

# Split night drivers by vehicle type
night_driver_split = night_driver / types_of_car

# Split hybrid drivers by vehicle type
hybrid_driver_split = hybrid_driver / types_of_car

print("Fleet Size of {} vehicles is divided as follows - ".format(fleet_size))
print("Autonomous Vehicles per vehicle type: ", auto_split)
print("Day Drivers per vehicle type: ", day_driver_split)
print("Night Drivers per vehicle type: ", night_driver_split)
print("Hybrid Drivers per vehicle type: ", hybrid_driver_split)