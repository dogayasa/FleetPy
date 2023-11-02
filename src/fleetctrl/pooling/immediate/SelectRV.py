import numpy as np
from src.simulation.Vehicles import SimulationVehicle
from src.simulation.Driver import Driver
from src.fleetctrl.planning.VehiclePlan import VehiclePlan
from src.routing.NetworkBase import NetworkBase
from src.fleetctrl.planning.PlanRequest import PlanRequest

import logging
LOG = logging.getLogger(__name__)

def filter_directionality(prq, list_veh_obj, nr_best_veh, routing_engine, selected_veh):
    """This function filters the nr_best_veh from list_veh_obj according to the difference in directionality between
    request origin and destination and planned vehicle route. Vehicles with final position equal to current position
    are treated like driving perpendicular to the request direction.

    :param prq: plan request in question
    :param list_veh_obj: list of simulation vehicle objects in question
    :param nr_best_veh: number of vehicles that should be returned
    :param routing_engine: required to get coordinates from network positions
    :param selected_veh: set of vehicles that were already selected by another heuristic
    :return: list of simulation vehicle objects
    """
    if nr_best_veh >= len(list_veh_obj):
        return list_veh_obj
    prq_o_coord = np.array(routing_engine.return_position_coordinates(prq.o_pos))
    prq_d_coord = np.array(routing_engine.return_position_coordinates(prq.d_pos))
    tmp_diff = prq_d_coord - prq_o_coord
    prq_norm_vec = tmp_diff / np.sqrt(np.dot(tmp_diff, tmp_diff))
    tmp_list_veh_val = []
    for veh_obj in list_veh_obj:
        # vehicle already selected by other heuristic
        if veh_obj in selected_veh:
            continue
        if veh_obj.assigned_route:
            veh_coord = np.array(routing_engine.return_position_coordinates(veh_obj.pos))
            last_position = veh_obj.assigned_route[-1].destination_pos
            veh_final_coord = np.array(routing_engine.return_position_coordinates(last_position))
            if not np.array_equal(veh_coord, veh_final_coord):
                tmp_diff = veh_final_coord - veh_coord
                veh_norm_vec = tmp_diff / np.sqrt(np.dot(tmp_diff, tmp_diff))
            else:
                veh_norm_vec = np.array([0, 0])
        else:
            veh_norm_vec = np.array([0, 0])
        val = np.dot(prq_norm_vec, veh_norm_vec)
        tmp_list_veh_val.append((val, veh_obj.vid, veh_obj))
    # sort and return
    tmp_list_veh_val.sort(reverse=True)
    return_list = [x[2] for x in tmp_list_veh_val[:nr_best_veh]]
    return return_list


def filter_least_number_tasks(list_veh_obj, nr_best_veh, selected_veh):
    """This function filters the vehicles according to the number of assigned tasks.

    :param list_veh_obj: list of simulation vehicle objects in question (sorted by distance from destination)
    :param nr_best_veh: number of vehicles that should be returned
    :param selected_veh: set of vehicles that were already selected by another heuristic
    :return: list of simulation vehicle objects
    """
    if len(list_veh_obj) <= nr_best_veh:
        return list_veh_obj
    return_list = []
    remaining_dict = {}
    for veh_obj in list_veh_obj:
        if veh_obj in selected_veh:
            continue
        if not veh_obj.assigned_route:
            return_list.append(veh_obj)
        else:
            nr_vrl = len(veh_obj.assigned_route)
            try:
                remaining_dict[nr_vrl].append(veh_obj)
            except KeyError:
                remaining_dict[nr_vrl] = [veh_obj]
        if len(return_list) == nr_best_veh:
            break
    if len(return_list) < nr_best_veh:
        break_outer_loop = False
        for nr_vrl in sorted(remaining_dict.keys()):
            for veh_obj in remaining_dict[nr_vrl]:
                return_list.append(veh_obj)
                if len(return_list) == nr_best_veh:
                    break_outer_loop = True
                    break
            if break_outer_loop:
                break
    return return_list

def filter_enough_shift_time(veh_plan : VehiclePlan, veh_obj : SimulationVehicle, routing_engine : NetworkBase, prq : PlanRequest):
    
    shift_decrease = sum(veh_plan.shift_decreases)

    # calculate boarding times------------------------------------------------------------------------------
    number_stops = len(veh_obj.boarding_alighting_points)
    shift_decrease += veh_obj.const_bt * number_stops
    if prq.o_pos not in veh_obj.boarding_alighting_points:
        shift_decrease += veh_obj.const_bt
    if prq.d_pos not in veh_obj.boarding_alighting_points:
        shift_decrease += veh_obj.const_bt

    
    # check if feasible ------------------------------------------------------------------------------------
    feasible_overtime = None
    c_time = veh_obj.driver.selected_shift_time - veh_obj.driver.shift_time
    next_c_time = c_time + shift_decrease

    # for 4h without break 
    if veh_obj.driver.without_break + shift_decrease >= 13500 and veh_obj.driver.without_break + shift_decrease <= 15300:
        if (len(veh_obj.driver.break_time_points) == 0 and (veh_obj.driver.shift_time-shift_decrease) >= 900) or (len(veh_obj.driver.break_time_points) > 0 and next_c_time + 1 <= veh_obj.driver.break_time_points[0] - 900):
            veh_obj.driver.four_hour_zone = True
    elif  veh_obj.driver.without_break + shift_decrease > 15300:
        # not feasible 
        veh_plan = None 
        return (veh_plan, feasible_overtime)
                
    # for break 
    if len(veh_obj.driver.break_time_points) > 0 and veh_obj.driver.break_time_points[0] <= next_c_time:
        # not feasible 
        veh_plan = None 
        return (veh_plan, feasible_overtime)
    
    # for shift
    if shift_decrease > veh_obj.driver.shift_time:
        # check if driver can do this overtime
        overtime = veh_obj.driver.calculate_overtime(shift_decrease)
        if(veh_obj.driver.can_do_overtime(overtime)):
            feasible_overtime = overtime
        else:
            veh_plan = None 
        return (veh_plan, feasible_overtime)
    
    return (veh_plan, feasible_overtime)
