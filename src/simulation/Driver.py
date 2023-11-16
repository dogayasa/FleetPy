import logging
import pandas as pd
import typing as tp
import random


from src.misc.globals import *
LOG = logging.getLogger(__name__)


class Driver: 
    def __init__(self, shift_data, veh_obj):     

        # output variables ----
        self.taken_shift = 0
        # weekly
        self.worked = 0
        self.rested = 0
        self.total_overtime = 0
        self.daily_overtime = 0
        self.expected_overtime = 0
        self.decreased_break = 0
        self.start_passengers = 0 
        # ---------------------

        # SelectRV -> take break after 4h of working
        self.four_hour_zone = False

        # standards (st) that won't be changed ------------------------
        self.min_shift_time = int(shift_data[G_STANDARD_MIN_SHIFT_TIME])
        self.max_shift_time = int(shift_data[G_STANDARD_MAX_SHIFT_TIME])
        self.min_break_time = int(shift_data[G_STANDARD_MIN_BREAK_TIME])
        self.max_break_time = int(shift_data[G_STANDARD_MAX_BREAK_TIME])
        self.min_week_time = int(shift_data[G_STANDARD_MIN_WEEK_TIME])
        self.max_week_time = int(shift_data[G_STANDARD_MAX_WEEK_TIME])
        self.st_bw_shifts = int(shift_data[G_STANDARD_BW_SHIFTS])
        self.min_num_breaks = int(shift_data[G_MIN_NUMBER_BREAKS])
        self.max_num_breaks = int(shift_data[G_MAX_NUMBER_BREAKS])

        self.planned_hour = 0 
        self.current_hour = 0
        self.planned_hour_start = 0

        self.check_input()
        
        # day or night ---------------------------------------------------------
        self.preferred_earliest = int(shift_data[G_EARLIEST_START]) 
        self.preferred_latest = int(shift_data[G_LATEST_START]) 
        # -> if based on name? 
        if "day" in veh_obj.veh_type:
            self.shift_type = DRIVER_SHIFTS.DAY_SHIFT
        elif "night" in veh_obj.veh_type: 
            self.shift_type = DRIVER_SHIFTS.NIGHT_SHIFT
        # if based on hour
        """
        check = self.order_chrono(self.preferred_earliest,3,18)
        if check == -1 or check == 0: 
            self.shift_type = DRIVER_SHIFTS.NIGHT_SHIFT
        else:
            self.shift_type = DRIVER_SHIFTS.DAY_SHIFT
        """
        # -----------------------------------------------------------------------

        # changed for every new shift -------------------------------------------
        # shift
        self.selected_shift_start_hour = 0 
        self.selected_shift_time = 0 # for night shifts its 0 
        # breaks
        self.selected_bws = 0
        self.selected_break_number = 0 
        # variables that will be updated throughout the scenario 
        # shift
        self.shift_time = None
        self.assumed_shift_time = None
        # breaks
        self.on_break = False
        self.on_shift_break = False
        self.planned_break = 0 # = 45 min
        self.break_time = None
        self.number_of_breaks = 0
        self.ready_for_break = True
        self.without_break = 0
        self.bw_shifts = 0
        self.break_time_points = [] # when sould a driver take a break 
        self.break_time_durations = [] 
        # -----------------------------------------------------------------------
        
        # changed for every new week --------------------------------------------
        self.weekly_shift_time = self.min_week_time 
        self.week = 604800
        # overtime 
        self.overtime = self.max_week_time - self.min_week_time        
    
    # initializers -----------------------------------------------------------------------
    def set_initial_state(self,state_dict):
        self.worked = state_dict[G_VD_WORKED_TOTAL]
        self.total_overtime = state_dict[G_VD_TOTAL_OVERTIME]
        self.taken_shift = state_dict[G_VD_SHIFT_COUNT]
        self.rested = state_dict[G_VD_RESTED_TOTAL]
        self.shift_type =  state_dict[G_V_INIT_SHIFT_TYPE]
        self.shift_time =  state_dict[G_V_INIT_SHIFT_TIME]
        self.break_time_durations = state_dict[G_V_INIT_BREAK_TIMES]
        self.break_time_points = state_dict[G_V_INIT_BREAK_POINTS]
        self.bw_shifts =  state_dict[G_V_INIT_BW_SHIFTS]  
    
    def init_break_type(self):
        """
        This function is called when initializing the driver's shift. 
        It determines first break_time and when should the break be taken. 
        """
        # Noon break for drivers with >= 8h shift is on 5th hour
        # Drivers with <= 4h dont take break 
        if self.selected_shift_time >= 28800: 
            self.number_of_breaks = random.randint(self.min_num_breaks,self.max_num_breaks)
            self.selected_break_number = self.number_of_breaks
            half_day = 18000
        elif self.selected_shift_time <= 14400: 
            self.number_of_breaks = 0
            self.ready_for_break = False
            self.selected_break_number = 0
            return
        else: 
            self.number_of_breaks = random.randint(self.min_num_breaks,self.max_num_breaks)
            self.selected_break_number = self.number_of_breaks
            half_day = self.selected_shift_time // 2 

        
        # there are 2 types of breaks ---------------------------------------------------------
        if self.number_of_breaks == 1:
            # long break of 45 minutes 
            self.break_time = 2700 
            self.break_time_points.append(half_day)
            self.break_time_durations.append(self.break_time)
            self.planned_break += self.break_time
        else: 
            # random number of breaks [2:5]
            after_noon = self.number_of_breaks // 2
            before_noon = self.number_of_breaks - after_noon
            avg_break = 2700 / self.number_of_breaks
            min_border = max(avg_break, self.min_break_time)

            # determining before noon break points ----------------------------------
            timestep = (half_day // before_noon)
            endborder = timestep - self.max_break_time
            startborder = 1 
            while(before_noon!=0):
                self.break_time_points.append(random.randint(startborder, endborder))
                self.break_time_durations.append(random.randint(min_border, self.max_break_time))
                self.planned_break += self.break_time_durations[len(self.break_time_durations)-1]
                startborder = endborder + self.max_break_time
                endborder += timestep
                before_noon -= 1
            # ------------------------------------------------------------------------

            # determining after noon break points ----------------------------------
            timestep = ((self.selected_shift_time-half_day) // after_noon)
            endborder = (timestep+half_day) - self.max_break_time
            startborder = half_day 
            while(after_noon!=0):
                self.break_time_points.append(random.randint(startborder, endborder))
                self.break_time_durations.append(random.randint(min_border, self.max_break_time))
                self.planned_break += self.break_time_durations[len(self.break_time_durations)-1]
                startborder = endborder + self.max_break_time
                endborder += timestep
                after_noon -= 1
            # ------------------------------------------------------------------------

            # for the first break 
            self.break_time = self.break_time_durations[0]
    
    def randomize_starting_point(self, veh_obj):
        """
        This function randomizes vehicle states in simulation start. 
        """
        # STARTING AT NIGHT - 23:00 - 03:00 ----------------------------------------------------------------------------------
        # NIGHT_SHIFT at night -------------------------------------------------------------------------------------------
        # at least 4 h between 00:00 and 07:00
        if self.shift_type == DRIVER_SHIFTS.NIGHT_SHIFT: 
            # when should the driver start his/her shifts on that week ----------------
            start_day = random.randint(1,4)

            # start hour may differ ---------------------------------------------------
            if self.preferred_latest >= self.preferred_earliest:
                self.selected_shift_start_hour = random.randint(self.preferred_earliest, self.preferred_latest)
            else:
                self.selected_shift_start_hour = self.hour_stabilizer(random.randint(self.preferred_earliest, self.preferred_latest+24))
            # -------------------------------------------------------------------------

            self.planned_hour = self.selected_shift_start_hour*3600
            self.planned_hour_start = self.planned_hour
            
            if start_day == 1: 
                chrono = self.order_chrono(self.selected_shift_start_hour, 0, self.preferred_earliest) 
            else: 
                chrono = 1 

            # if already started their night shift ------------------------------------
            if chrono == -1:
                self.current_hour = self.planned_hour
                worked_tdy = self.hour_difference(self.selected_shift_start_hour, 0)
                self.take_shift(veh_obj)
                self.current_hour = 0
                # update according to current time
                self.shift_time = self.shift_time - (worked_tdy*3600) 
                self.update_break_type(worked_tdy*3600)
                return
            # if there is time until their start time---------------------------------- 
            elif chrono == 1:
                self.on_shift_break = True
                self.shift_time = 0
                veh_obj.status = VRL_STATES.ON_SHIFT_BREAK

                # take bws break according to day ------
                self.bw_shifts = self.hour_difference(0, self.selected_shift_start_hour) * 3600
                if 1 < start_day: 
                    self.bw_shifts += ((start_day-1)*24*3600)
                # --------------------------------------

                # report break behavior ----------------
                if self.st_bw_shifts > self.bw_shifts:
                    self.planned_hour_start = self.planned_hour - self.st_bw_shifts
                    if self.planned_hour_start < 0: 
                        self.planned_hour_start += (24*3600)
                else:
                    self.planned_hour_start = 0
                self.selected_bws = max(self.bw_shifts,self.st_bw_shifts)
                veh_obj.cb_start_bws = self.selected_bws 
                # --------------------------------------
                return
            # shift starts now --------------------------------------------------------
            else:
                self.take_shift(veh_obj)
                return
    
        # DAY_SHIFT at night ---------------------------------------------------------------------------------------------
        else: 
            start_day = random.randint(1,4)

            # randomize start & stabilize time
            bws_start_hour = self.second_stabilizer(random.randint(self.preferred_earliest*3600+self.min_shift_time, self.preferred_latest*3600+self.max_shift_time))

            self.planned_hour = bws_start_hour
            self.planned_hour_start = self.planned_hour

            if start_day == 1: 
                earliest_day_end = ((self.preferred_earliest*3600)+self.min_shift_time)/3600
                chrono = self.order_chrono(bws_start_hour/3600, 0 ,earliest_day_end) 
            else:
                chrono = 0

            # if already started their bws --------------------------------------------------------------------------------
            if chrono == -1:
                self.current_hour = self.planned_hour
                done = self.hour_difference(bws_start_hour/3600, 0)
                self.take_bw_shifts(veh_obj)
                self.current_hour = 0
                self.bw_shifts -= (done*3600) 
                return 
            # if there is time until their bws -----------------------------------------------------------------------------
            elif chrono == 1: 
                # we assume current shift time was selected as minimum shift time
                self.planned_hour_start = bws_start_hour - self.min_shift_time
                if self.planned_hour_start < 0: 
                    self.planned_hour_start += (24*3600)
                    
                self.weekly_shift_time -= self.hour_difference(0, bws_start_hour/3600) # worked will updated in end_shift 
                self.taken_shift = 1 

                self.selected_shift_time = self.min_shift_time
                self.init_break_type()
                self.shift_time = (self.hour_difference(0, bws_start_hour/3600)) * 3600
                self.update_break_type(self.selected_shift_time-self.shift_time)
                self.continue_shift(veh_obj)
                return
            else:
                self.take_bw_shifts(veh_obj)
                if start_day > 1: 
                    self.bw_shifts += ((start_day-1)*24*3600)
                    self.selected_bws = self.bw_shifts
                    veh_obj.cb_start_bws = self.selected_bws
                return 
        # ----------------------------------------------------------------------------------------------------------------
                     
    # -------------------------------------------------------------------------------------
    
    # functions that start a shift behavior -----------------------------------------------
    def take_shift(self, veh_obj):
        """
        This function is called when it is time for a driver to start their shift.
        It also ends the between shift break before starting shift.
        """
        # update clock if necessary -------------------------------------------------------
        if self.current_hour != self.planned_hour:
            self.planned_hour = self.current_hour
        # ---------------------------------------------------------------------------------

        # didn't start shift again --------------------------------------------------------
        if self.weekly_shift_time <= 0:  
            # this vehicle can't take any more shift this week
            self.week_shift_is_over(veh_obj)
            return
        # ---------------------------------------------------------------------------------

        # if not simulation begin shift break has to be reported and shift vars resetted --
        if self.taken_shift != 0:
            self.rested += veh_obj.cb_start_bws - self.bw_shifts               
            veh_obj.end_bws_break()
            self.reset_shift_variables()
        # ---------------------------------------------------------------------------------
        
        self.on_shift_break = False

        if self.weekly_shift_time <= self.max_shift_time:
            # if a day is left, take the remaining -> it can also be less than minimum shift  
            self.shift_time = self.weekly_shift_time
        elif(self.weekly_shift_time > self.max_shift_time): 
            self.shift_time = random.randint(self.min_shift_time, self.max_shift_time)
        
        # changed for every new shift --------------------
        self.selected_shift_time = self.shift_time
        self.planned_hour_start = self.planned_hour
        self.planned_hour = self.second_stabilizer(self.planned_hour + self.selected_shift_time)
        self.assumed_shift_time = self.selected_shift_time
        self.init_break_type()
        # just selected shifts are decrease from weekly st, not overtimes
        self.planned_hour = self.second_stabilizer(self.planned_hour + self.planned_break)
        self.weekly_shift_time -= self.shift_time
        veh_obj.status = VRL_STATES.IDLE 
        self.taken_shift += 1
        # ------------------------------------------------

        LOG.info(f"Driver of vehicle {veh_obj.vid} has started its shift of {self.time_definer(self.shift_time)}.\n")

    def week_start(self):
        """
        This function is called at when simulation time is more than or equal to 168 h = 1 week. 
        """
        self.weekly_shift_time = self.min_week_time 
        self.week = 604800 # week in seconds to skip to next week 
        # overtime 
        self.overtime = self.max_week_time - self.min_week_time
        self.total_overtime = 0
        self.daily_overtime = 0
        self.worked = 0
        self.rested = 0

    def continue_shift(self, veh_obj):
        """
        This function is called after a normal break. 
        """
        if self.shift_time <= 0: 
            self.take_bw_shifts(veh_obj)
            return
        veh_obj.status = VRL_STATES.IDLE

    def take_break(self, veh_obj):
        """
        This function starts a normal break. 
        """
        self.on_break = True 

        # report break behavior ----------------
        veh_obj.cb_start_break = self.break_time
        # --------------------------------------
        
        veh_obj.status = VRL_STATES.ON_BREAK

    def take_bw_shifts(self, veh_obj):
        """
        This function starts a shift break and decides on the next shift's start time.
        """
        # didn't start normal bws again ---------------------------------------------------
        if self.weekly_shift_time <= 0:  
            # this vehicle can't take any more shift this week
            self.week_shift_is_over(veh_obj)
            return
        # ---------------------------------------------------------------------------------

        self.on_shift_break = True

        # decide on the next shift start time & updated planned_hour ------------------------------------------
        if self.preferred_latest >= self.preferred_earliest:
            self.selected_shift_start_hour = self.hour_stabilizer(random.randint(self.preferred_earliest, self.preferred_latest))        
        else:
            self.selected_shift_start_hour = self.hour_stabilizer(random.randint(self.preferred_earliest, self.preferred_latest+24))

        # update clock if necessary -------------------------------------------------------
        if self.current_hour != self.planned_hour:
            self.planned_hour = self.current_hour
        # ---------------------------------------------------------------------------------
        
        self.selected_bws = self.hour_difference(self.planned_hour/3600, self.selected_shift_start_hour) * 3600
        # if for example bws for night shift finished at 02 and next shift time is next day 04 than bws = 1 day + 2h
        
        if 5*3600 > self.selected_bws:
            self.selected_bws += (24*3600) 

        self.planned_hour_start = self.planned_hour
        self.planned_hour = self.selected_shift_start_hour*3600
        # -----------------------------------------------------------------------------------------------------

        # start the bws time count and assign status ----------------------------------------------------------
        self.shift_time = 0
        self.bw_shifts = self.selected_bws
        veh_obj.status = VRL_STATES.ON_SHIFT_BREAK
        # -----------------------------------------------------------------------------------------------------

        # report break behavior ----------------
        veh_obj.cb_start_bws = self.selected_bws
        # --------------------------------------
        LOG.info(f"\nTime for a between shifts break of {self.time_definer(self.bw_shifts)} for vehicle {veh_obj.vid}\n")
    
    def rest_while_charging(self, veh_obj, duration):
        """
        This function is called when the vehicle is charging. 
        """
        veh_obj.ch_duration += duration
        self.rested += duration
        self.without_break = 0

        # was on break and had to charge -------------------
        if self.on_break and duration != 0 and self.break_time > 0:
            if duration >= self.break_time:
                duration -= self.break_time 
                self.break_time = 0
                if duration != 0:
                    self.break_time -= duration
                    self.planned_hour = self.second_stabilizer(self.planned_hour+duration)
                    duration = 0
            else:
                self.break_time -= duration
                duration = 0
        # was on shift break -------------------------------
        elif self.on_shift_break and duration != 0 and self.bw_shifts > 0: 
            if duration >= self.bw_shifts:
                duration -= self.bw_shifts 
                self.bw_shifts = 0
                if duration != 0:
                    self.bw_shifts -= duration
                    self.planned_hour = self.second_stabilizer(self.planned_hour+duration)
                    duration = 0
            else:
                self.bw_shifts -= duration
                duration = 0
            
        # was idle but has breaks to take ------------------
        else:              
            while duration != 0 and len(self.break_time_durations) > 0: 
                self.break_time = self.break_time_durations[0]
                if duration >= self.break_time:
                    duration -= self.break_time 
                    self.decreased_break += self.break_time
                    del self.break_time_durations[0]
                    del self.break_time_points[0]
                    self.number_of_breaks -= 1
                else:
                    self.break_time -= duration
                    self.decreased_break += duration
                    duration = 0
                    self.break_time_durations[0] = self.break_time
            if duration != 0:
                self.planned_hour = self.second_stabilizer(self.planned_hour+duration)
                duration = 0   
            if len(self.break_time_durations) == 0: 
                self.ready_for_break = False   
    # -------------------------------------------------------------------------------------

    # functions that end a shift behavior -------------------------------------------------
    def week_shift_is_over(self, veh_obj):
        """
        This function is called when drivers minimum allowed shift is over.
        And it randomizes the week start. 
        """
        self.on_shift_break = True 

        # calculate selected bws ------------------------------------------------------------
        self.selected_bws = self.week
        # decide on the next shift start time&day and update planned_hour 
        start_day = random.randint(1,4)
        if self.preferred_latest >= self.preferred_earliest:
            self.selected_shift_start_hour = random.randint(self.preferred_earliest, self.preferred_latest)
        else:
            self.selected_shift_start_hour = self.hour_stabilizer(random.randint(self.preferred_earliest, self.preferred_latest+24))
        # -----------------------------------------------------------------------------------

        # calculate bws duration ------------------------------------------------------------
        if self.week <= 24*3600 and start_day == 1:
            difference = self.hour_difference(self.planned_hour/3600, self.selected_shift_start_hour) 
            # if for example week ended at 23:00 sunday and selected start is 01:00 than driver should start
            # on tuesday 
            if 24 > difference:
                self.selected_bws += (24*3600) 
        self.selected_bws += (self.selected_shift_start_hour*3600)
        self.selected_bws += ((start_day-1)*24*3600)
        # -----------------------------------------------------------------------------------
        
        self.planned_hour_start = self.planned_hour
        self.planned_hour = self.selected_shift_start_hour*3600

        # start the bws time count and assign status ----------------------------------------
        self.shift_time = 0
        self.bw_shifts = self.selected_bws
        veh_obj.status = VRL_STATES.ON_SHIFT_BREAK
        # -----------------------------------------------------------------------------------

        # report break behavior ----------------
        veh_obj.cb_start_bws = self.selected_bws
        # --------------------------------------

    def end_break(self, veh_obj): 
            """
            This function is called when the requested break time is taken. 
            It determines next break_time and continues shift 

            :param veh_obj: the vehicle of this driver
            """
            self.rested += (veh_obj.cb_start_break - self.break_time)
            veh_obj.end_break()
            self.number_of_breaks -= 1
            del self.break_time_durations[0]
            del self.break_time_points[0]
            self.without_break = 0
            self.on_break = False

            if self.number_of_breaks == 0:
                self.ready_for_break = False
            else:
                self.break_time = self.break_time_durations[0]

            self.continue_shift(veh_obj)
    
    def end_shift(self, veh_obj):
        """
        This function is called when the taken shift duration is over.
        """
        # update clock if necessary -------------------------------------------------------
        if self.current_hour != self.planned_hour:
            self.planned_hour = self.current_hour
        # ---------------------------------------------------------------------------------
            
        exceed = -1 * veh_obj.driver.shift_time
        self.total_overtime += exceed
        if self.daily_overtime != exceed:
            self.expected_overtime = self.daily_overtime
            self.daily_overtime = exceed
        
        # daily summary -----------------------------------------------------------------------------------------------------------------------
        veh_obj.end_shift()
        self.worked += self.selected_shift_time + exceed
        # --------------------------------------------------------------------------------------------------------------------------------------    
    
    def reset_shift_variables(self):
        """
        This function resets shift control variables when ending a between shift break in take_shift
        """
        self.selected_shift_time = 0 # for night shifts its 0 
        self.selected_break_number = 0 
        self.shift_time = None
        self.assumed_shift_time = None
        self.planned_break = 0 
        self.break_time = None
        self.number_of_breaks = 0
        self.ready_for_break = True
        self.without_break = 0
        self.break_time_points = [] # when sould a driver take a break 
        self.break_time_durations = [] 
        self.on_break = False
        self.on_shift_break = False
        self.daily_overtime = 0
        self.expected_overtime = 0
    # -------------------------------------------------------------------------------------

    # control and helper functions --------------------------------------------------------
    def calculate_overtime(self, shift_decrease): 
        """
        This function calculates overtime according to assumed shift decrease and current 
        remaining shift time. 
        """
        if self.daily_overtime > 0:
            return shift_decrease - self.shift_time - self.daily_overtime
        return shift_decrease - self.shift_time 
    
    def can_do_overtime(self, exceed):
        """
        This function checks if the drivers exceeds max shift time or max weekly shift time with over time
        """
        if self.daily_overtime > 0:
            # already did overtime 
            future_worked_today = self.selected_shift_time + self.daily_overtime + exceed
        else:
            future_worked_today = self.selected_shift_time + exceed
        if self.overtime > 0 and exceed <= self.overtime and (future_worked_today) <= self.max_shift_time and (self.worked + future_worked_today) <= self.max_week_time:
            return True
        return False 

    def update_shift(self, shift_decrease):
        """
        This function decreases shift time everytime driver is working.
        """
        self.shift_time -= shift_decrease
        self.without_break += shift_decrease 
    
    def check_shift(self, veh_obj):
        """
        This function is called when alighting or IDLE and doesn't have an assigned route. 
        It checks if it is time to take any type of break. 
        If driver works more than 4h, it will take a break of 10 mins. 
        """
        # check if shift is over ------------------------------------------------------
        if self.shift_time <= 0:
            self.end_shift(veh_obj)
            self.take_bw_shifts(veh_obj)
            return
        # -----------------------------------------------------------------------------
        c_time = self.selected_shift_time - self.shift_time

        # worked for 4h and now idle 
        if veh_obj.status == VRL_STATES.IDLE and self.without_break >= 14400:
            if (len(self.break_time_points) == 0 and self.shift_time >= 900) or (len(self.break_time_points) > 0 and c_time + 1 <= self.break_time_points[0] - 900):
                self.break_time_points.insert(0,c_time)
                self.break_time_durations.insert(0,600)
                self.number_of_breaks += 1 
                self.ready_for_break = True


        # check if it is time for a normal break --------------------------------------
        if self.ready_for_break: 
            # check if it is time to take a break
            if c_time >= self.break_time_points[0]: 
                self.take_break(veh_obj)  
        # -----------------------------------------------------------------------------

    def time_definer(self, time):
            """
            This function returns string for the given second in hours or minutes.
            """
            if time == 3600: 
                return "1 hour"
            elif time > 3600:
                return f"{time/3600} hours"
            elif time > 60 and time < 3600:
                return f"{time/60} minutes"
            else: 
                return f"{time} seconds"
                
    def check_input(self):
        """
        This function checks if the given inputs are logical.
        """
        if self.min_shift_time > self.max_shift_time or self.max_break_time > self.min_shift_time or self.min_break_time > self.max_break_time or self.max_shift_time > self.st_bw_shifts or self.min_week_time > self.max_week_time or self.max_shift_time > self.min_week_time or self.min_num_breaks > self.max_num_breaks:
            print("ERROR! Input variables for driver is wrong.")
            print("Hint: Look out for min and max in input names.")
            exit()
    
    def update_break_type(self, c_time):
        """
        This function is a helper for randomizing simulation start time. 
        It updates the break points & duration if driver already started shift before simulation, according
        to the remaining shift time. 
        """
        self.break_time_points = list(filter(lambda point: point >= c_time, self.break_time_points))
        self.break_time_durations = self.break_time_durations[self.number_of_breaks-len(self.break_time_points):]
        if len(self.break_time_points) > 0 : 
            self.break_time = self.break_time_durations[0] 
            self.ready_for_break = True 
        else:
            self.ready_for_break = False
        self.number_of_breaks = len(self.break_time_points)

    def update_until_today(self,bws_count):
        """
        This function is a helper for randomizing simulation start time. 
        """
        max_possible_worked = min(self.weekly_shift_time, self.max_shift_time*self.taken_shift)
        self.worked += random.randint((self.min_shift_time*self.taken_shift),max_possible_worked)
        self.rested += (self.st_bw_shifts*bws_count) # assumed 11h bws before
        self.weekly_shift_time -= self.worked

    def update_week(self, time_passed, veh_obj):
        """
        This function is a helper for randomizing simulation start time. 
        """
        self.week -= time_passed 
        self.current_hour += time_passed
        if self.current_hour >= 24*3600:
            self.current_hour -= (24*3600)

        if self.week <= 0: 
            if veh_obj.status != VRL_STATES.ON_SHIFT_BREAK and not self.on_shift_break: 
                self.weekly_shift_time += self.shift_time
                if veh_obj.status == VRL_STATES.ON_BREAK or self.on_break: 
                    self.rested -= self.break_time
                self.week_start()
                if veh_obj.status == VRL_STATES.ON_BREAK or self.on_break: 
                    veh_obj.cb_start_break = self.break_time
                self.weekly_shift_time -= self.shift_time
            else:
                self.rested -= self.bw_shifts
                self.week_start()
                veh_obj.cb_start_bws = self.bw_shifts

    def hour_difference(self, x, point):
        """
        This function calculates the hour difference between points.
        """
        count = 0
        if point - x < 0:
            count = 24
        count += (point-x)
        return count 
    
    def order_chrono(self, x, point, start):
        """
        This function determines if x or point comes first after start.
        """
        hour_x = self.hour_difference(start, x)
        hour_point = self.hour_difference(start, point)
        if hour_point > hour_x:
            return -1 # point is after x 
        elif hour_x > hour_point:
            return 1 
        else:
            return 0 
        
    def hour_stabilizer(self, hour):
        if hour >= 24:
            return hour - 24
        else: 
            return hour 
        
    def second_stabilizer(self, second):
        if second >= 24*3600:
            return second - 24*3600
        else: 
            return second 
    # ------------------------------------------------------------------------------------

    