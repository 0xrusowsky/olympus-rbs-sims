import random
import math
import numpy as np
from typing import Dict, List, Tuple


# Market behavior simulation functions
def short_sin(day:int, cycle:int):
    value = 1.5 + (0.5 * math.sin((day + 1.5 * cycle) / (cycle / (2*math.pi))))
    return value


def short_cos(day:int, cycle:int):
    value = 1.55 + (0.5 * math.cos((day + 0.5 * cycle) / (cycle / (2*math.pi))))
    return value


def long_sin(day:int, cycle:int, offset:float):
    value = 1 + (0.5 * math.sin(((day + cycle * offset) % cycle) / (cycle / (2*math.pi)))) * (10 - (day / cycle)) / 10
    #value = 1 + (0.5 * math.sin(((day + cycle * offset) % cycle) / (cycle / (2*math.pi))))
    return value


def long_cos(day:int, cycle:int, offset:float, amplitude:float):
    value = amplitude * (1 + (0.5 * math.cos(((day + 2 * cycle * offset) % (2 * cycle)) / (cycle / math.pi))) * (10 - (day / (2 * cycle))) / 10 )
    #value = 1 + (0.5 * math.cos(((day + cycle * offset) % cycle) / (cycle / (2*math.pi))))
    return value


# Reward rate framework
def rr_framework(supply:int, with_dynamic_reward_rate:str, rr_controller:int, version="v1"):
    if supply < 1_000_000:
        r = 0.3058 * 3 / 100
    elif supply < 10_000_000:
        r = 0.1587 * 3 / 100
    elif supply < 100_000_000:
        r = 0.1183 * 3 / 100
    elif supply < 1_000_000_000:
        r = 0.0458 * 3 / 100
    elif supply < 10_000_000_000:
        r = 0.0148 * 3 / 100
    elif supply < 100_000_000_000:
        r = 0.0039 * 3 / 100
    elif supply < 1_000_000_000_000:
        r = 0.0019 * 3 / 100
    else:
        r = 0.0009 * 3 / 100


    if with_dynamic_reward_rate == 'No':
        return r
    else:
        if version == "v0": # controller v0
            if rr_controller != 9:
                return r/2

        elif version == "v1": # controller v1
            if rr_controller == -3: #below backing
                return 0
            elif rr_controller == -2: #below wall
                return r * (0.5)
            elif rr_controller == -1: #below cushion
                return r * (0.75)
            elif rr_controller == 2: #above premium of 3
                return r * (1.25)
            elif rr_controller == 1: #above wall
                return r * (1.125)
            elif rr_controller == 0: #inside range, as usual
                return r



class ModelParams():
    def __init__(self, seed:int, netflow_type:str, horizon:int, ask_factor:float, bid_factor:float, cushion_factor:float, target_ma:float, lower_wall:float, upper_wall:float, lower_cushion:float, upper_cushion:float, reinstate_window:int, min_counter_reinstate:int, min_premium_target:int, max_outflow_rate:float, supply_amplitude:int, reserve_change_speed:float, max_liq_ratio:float, cycle_reweights:float, release_capture:float, demand_factor:float, supply_factor:float, initial_supply:float, initial_reserves:float, initial_liq_usd:float, arb_factor:float, initial_price:float, initial_target:float, target_price_function:str, short_cycle:int, long_cycle:int, long_sin_offset:float, long_cos_offset:float, with_reinstate_window:str, with_dynamic_reward_rate:str):
        self.seed = seed
        self.horizon = horizon
        self.cycle_reweights = cycle_reweights
        self.reserve_change_speed = reserve_change_speed
        self.short_cycle = short_cycle
        self.long_cycle = long_cycle
        self.long_sin_offset = long_sin_offset
        self.long_cos_offset = long_cos_offset
        self.supply_amplitude = supply_amplitude

        self.max_liq_ratio = max_liq_ratio
        self.min_premium_target = min_premium_target
        self.release_capture = release_capture
        self.max_outflow_rate = max_outflow_rate
        self.with_reinstate_window = with_reinstate_window
        self.with_dynamic_reward_rate = with_dynamic_reward_rate
        self.demand_factor = demand_factor
        self.supply_factor = supply_factor

        self.target_ma = target_ma
        self.lower_wall = lower_wall
        self.upper_wall = upper_wall
        self.lower_cushion = lower_cushion
        self.upper_cushion = upper_cushion
        self.bid_factor = bid_factor
        self.ask_factor = ask_factor
        self.cushion_factor = cushion_factor
        self.reinstate_window = reinstate_window
        self.min_counter_reinstate = min_counter_reinstate

        self.initial_supply = initial_supply
        self.initial_reserves = initial_reserves
        self.initial_liq_usd = initial_liq_usd
        self.initial_price = initial_price
        self.initial_target = initial_target
        self.target_price_function = target_price_function
        self.netflow_type = netflow_type
        self.arb_factor = arb_factor


class Day():
    def __init__(self, params:ModelParams, prev_arbs:Dict[int, Tuple[float, float]], prev_lags=Dict[int, Tuple[int, Dict[int, float]]], prev_day=None, historical_net_flows=None):

        if prev_day is None:
            self.day = 1
            self.supply = params.initial_supply
            self.reward_rate = rr_framework(self.supply, params.with_dynamic_reward_rate, 0)
            self.price = params.initial_price
            self.liq_usd = params.initial_liq_usd
            self.liq_ohm = self.liq_usd / self.price
            self.k = (self.liq_usd ** 2) / self.price

            self.reserves_in = 0
            self.reserves_out = 0
            self.release_capture = 0
            self.ohm_traded = 0
            self.cum_ohm_purchased = 0
            self.cum_ohm_burnt = 0
            self.cum_ohm_minted = 0
            self.reserves = params.initial_reserves
            self.prev_reserves = params.initial_reserves

            self.ma_target = params.initial_target
            self.lower_target_wall = self.ma_target * (1 - params.lower_wall)
            self.upper_target_wall = self.ma_target * (1 + params.upper_wall)
            self.lower_target_cushion = self.ma_target * (1 - params.lower_cushion)
            self.upper_target_cushion = self.ma_target * (1 + params.upper_cushion)

            self.bid_capacity_target = params.bid_factor * self.reserves
            self.ask_capacity_target = params.ask_factor * self.reserves / self.upper_target_wall * (1 + params.lower_wall + params.upper_wall)
            self.bid_capacity_target_cushion = self.bid_capacity_target * params.cushion_factor
            self.ask_capacity_target_cushion = self.ask_capacity_target * params.cushion_factor
            self.bid_capacity = self.bid_capacity_target
            self.ask_capacity = self.ask_capacity_target
            self.bid_capacity_cushion = self.bid_capacity_target_cushion
            self.ask_capacity_cushion = self.ask_capacity_target_cushion
            self.ask_change_ohm = 0
            self.bid_change_ohm = 0
            
            self.prev_price = self.price
            self.prev_lower_target_wall = self.lower_target_wall
            self.prev_upper_target_wall = self.upper_target_wall
            
            self.market_demand = params.demand_factor
            self.market_supply = params.supply_factor
            self.arb_factor = params.arb_factor
            self.arb_demand = 0
            self.arb_supply = 0
            self.unwind_demand = 0
            self.unwind_supply = 0

            if params.netflow_type == 'historical' and historical_net_flows is not None:
                self.net_flow = historical_net_flows
            else:
                self.net_flow = random.uniform(self.liq_usd * self.market_supply, self.liq_usd * self.market_demand)
            prev_arbs[self.day] = (self.arb_demand, self.arb_supply)
            
            self.bid_counter = [0] * (params.reinstate_window - params.min_counter_reinstate) + [1] * params.min_counter_reinstate
            self.ask_counter = [0] * (params.reinstate_window - params.min_counter_reinstate) + [1] * params.min_counter_reinstate
            
        else:
            self.day = prev_day.day + 1
        #decrease reward rate
            #below backing
            if prev_day.fmcap_treasury_ratio < 1:                
                self.reward_rate = rr_framework(prev_day.supply, params.with_dynamic_reward_rate, -3)
            #below wall
            elif prev_day.price < prev_day.lower_target_wall:
                self.reward_rate = rr_framework(prev_day.supply, params.with_dynamic_reward_rate, -2)
            #below cushion
            elif prev_day.price < prev_day.lower_target_cushion:
                self.reward_rate = rr_framework(prev_day.supply, params.with_dynamic_reward_rate, -1)

        #increase reward rate
            #above 3x premium
            elif prev_day.fmcap_treasury_ratio > 3:
                self.reward_rate = rr_framework(prev_day.supply, params.with_dynamic_reward_rate, 2)
            #above wall
            elif prev_day.price > prev_day.lower_target_wall:
                self.reward_rate = rr_framework(prev_day.supply, params.with_dynamic_reward_rate, 1)

        #framework reward rate
            else:
                self.reward_rate = rr_framework(prev_day.supply, params.with_dynamic_reward_rate, 0)


            self.floating_supply = max(prev_day.floating_supply * (1 + self.reward_rate) + prev_day.ask_change_ohm - prev_day.bid_change_ohm, 0)
            self.ma_target = calc_price_target(params=params, prev_day=prev_day, prev_lags=prev_lags)
            self.prev_price = prev_day.price

            # Walls
            self.lower_target_wall = self.ma_target * (1 - params.lower_wall)
            self.upper_target_wall = self.ma_target * (1 + params.upper_wall)

            # Cushions
            self.lower_target_cushion = self.ma_target * (1 - params.lower_cushion)
            self.upper_target_cushion = self.ma_target * (1 + params.upper_cushion)

            # Inside the range counters
            if prev_day.price > prev_day.lower_target_cushion:
                self.bid_counter = prev_day.bid_counter[1:] + [1]
            else:
                self.bid_counter = prev_day.bid_counter[1:] + [0]

            if prev_day.price < prev_day.upper_target_cushion:
                self.ask_counter = prev_day.ask_counter[1:] + [1]
            else:
                self.ask_counter = prev_day.ask_counter[1:] + [0]

            # Target capacities
            self.bid_capacity_target = params.bid_factor * prev_day.reserves
            self.ask_capacity_target = prev_day.upper_target_wall and params.ask_factor * prev_day.reserves * (1 + params.lower_wall + params.upper_wall) / prev_day.upper_target_wall or 0
            self.bid_capacity_target_cushion = self.bid_capacity_target * params.cushion_factor
            self.ask_capacity_target_cushion = self.ask_capacity_target * params.cushion_factor


            # Market dynamics
            if params.netflow_type == 'historical' and historical_net_flows is not None:
                self.net_flow = historical_net_flows
            else:
                #self.net_flow = random.uniform(prev_day.treasury * prev_day.total_supply, prev_day.treasury * prev_day.total_demand) + prev_day.release_capture
                self.net_flow = random.uniform(prev_day.treasury * prev_day.total_supply, prev_day.treasury * prev_day.total_demand) - (prev_day.supply * prev_day.reward_rate * prev_day.price / 10) + prev_day.release_capture

            if params.netflow_type == 'historical' and historical_net_flows is not None:
                self.market_demand = 0
                self.market_supply = 0
            elif params.netflow_type == 'random':
                self.market_demand = params.demand_factor * random.uniform(0.5, 3)
                self.market_supply = params.supply_factor * random.uniform(0.5, 3)
            else:
                self.market_demand = params.demand_factor * short_sin(self.day, params.short_cycle) * long_sin(self.day, params.long_cycle, params.long_sin_offset)
                self.market_supply = params.supply_factor * short_cos(self.day, params.short_cycle) * long_cos(self.day, params.long_cycle, params.long_cos_offset, params.supply_amplitude)


            # AMM k
            if prev_day.fmcap_treasury_ratio > params.min_premium_target:
                self.k = prev_day.k * (1 + self.reward_rate)**2
            else:
                self.k = prev_day.k
            
            
            # Reserve Intake
            if self.day % 7 == 0 and self.day != 0:  # Rebalance once a week
                if prev_day.reserves * (1 - params.max_liq_ratio) < prev_day.liq_usd * params.max_liq_ratio:
                    self.reserves_in = (prev_day.liq_usd * params.max_liq_ratio - prev_day.reserves * (1 - params.max_liq_ratio)) / (params.reserve_change_speed * params.short_cycle)
                else:
                    self.reserves_in = -2 * (prev_day.reserves * params.max_liq_ratio - prev_day.liq_usd * (1 - params.max_liq_ratio)) / (params.reserve_change_speed * params.short_cycle)
                
                if self.reserves_in < (-1) * prev_day.reserves:  # Ensure that the reserve release is limited by the total reserves left
                    self.reserves = (-1) * prev_day.reserves                
                if self.reserves_in < (-1) * prev_day.reserves * params.max_outflow_rate:  # Ensure that the reserve release is limited by the max_outflow_rate
                    self.reserves_in = (-1) * prev_day.reserves * params.max_outflow_rate
            else:
                self.reserves_in = 0

            natural_price = ((self.net_flow - self.reserves_in + prev_day.liq_usd) ** 2) / self.k

            # Real Bid Capacity - Cushion
            if (sum(self.bid_counter) >= params.min_counter_reinstate or params.with_reinstate_window == 'No') and natural_price > self.lower_target_cushion:
                self.bid_capacity_cushion = self.bid_capacity_target_cushion
            elif natural_price < self.lower_target_cushion and natural_price >= self.lower_target_wall:
                self.bid_capacity_cushion = prev_day.bid_capacity_cushion + self.net_flow - self.reserves_in + prev_day.liq_usd - (self.k * self.lower_target_cushion) ** (1/2)
            else:
                self.bid_capacity_cushion = prev_day.bid_capacity_cushion
            
            if self.bid_capacity_cushion < 0:
                self.bid_capacity_cushion = 0
            elif self.bid_capacity_cushion > self.bid_capacity_target_cushion:
                self.bid_capacity_cushion = self.bid_capacity_target_cushion

            # Effective Bid Capacity Changes - Cushion
            if natural_price <= self.lower_target_cushion and natural_price > self.lower_target_wall:
                self.bid_change_cushion_ohm = self.lower_target_cushion and (prev_day.bid_capacity_cushion - self.bid_capacity_cushion) / self.lower_target_cushion or 0
                self.bid_change_cushion_usd = prev_day.bid_capacity_cushion - self.bid_capacity_cushion
            else:
                self.bid_change_cushion_ohm = 0
                self.bid_change_cushion_usd = 0

            if self.bid_change_cushion_ohm > prev_day.bid_capacity_cushion:  # ensure that change is smaller than capacity left
                self.bid_change_cushion_ohm = self.lower_target_cushion and prev_day.bid_capacity_cushion / self.lower_target_cushion or 0
                self.bid_change_cushion_usd = prev_day.bid_capacity_cushion

            # Real Bid Capacity - Totals
            if (sum(self.bid_counter) >= params.min_counter_reinstate or params.with_reinstate_window == 'No') and natural_price > self.lower_target_cushion:
                self.bid_capacity = self.bid_capacity_target
            elif natural_price < self.lower_target_wall:
                self.bid_capacity = prev_day.bid_capacity + self.net_flow - self.reserves_in + prev_day.liq_usd - (self.k * self.lower_target_wall) ** (1/2)
            else:
                self.bid_capacity = prev_day.bid_capacity - self.bid_change_cushion_usd # update capacity total to account for the cushion

            if self.bid_capacity < 0:
                self.bid_capacity = 0
            elif self.bid_capacity > self.bid_capacity_target:
                self.bid_capacity = self.bid_capacity_target

            if self.bid_capacity_cushion > self.bid_capacity:
                self.bid_capacity_cushion = self.bid_capacity

            # Effective Bid Capacity Changes - Totals
            if natural_price >= self.lower_target_wall: #if wall wasn't used, update with cushion
                self.bid_change_ohm = self.bid_change_cushion_ohm
                self.bid_change_usd = self.bid_change_cushion_usd
            else:
                self.bid_change_ohm = self.lower_target_wall and self.bid_change_cushion_ohm + (prev_day.bid_capacity - self.bid_capacity - self.bid_change_cushion_usd) / self.lower_target_wall or 0
                self.bid_change_usd = prev_day.bid_capacity - self.bid_capacity

            if self.bid_change_usd > prev_day.bid_capacity:  # ensure that change is smaller than capacity left
                self.bid_change_ohm = self.lower_target_wall and prev_day.bid_capacity / self.lower_target_wall or 0
                self.bid_change_usd = prev_day.bid_capacity


            # Real Ask Capacity - Cushion
            if (sum(self.ask_counter) >= params.min_counter_reinstate or params.with_reinstate_window == 'No') and natural_price < self.upper_target_cushion:
                self.ask_capacity_cushion = self.ask_capacity_target_cushion
            elif natural_price > self.upper_target_cushion and natural_price <= self.upper_target_wall:
                self.ask_capacity_cushion = self.upper_target_cushion and prev_day.ask_capacity_cushion - (self.net_flow - self.reserves_in + prev_day.liq_usd) / self.upper_target_cushion + (self.k / self.upper_target_cushion) ** (1/2) or 0
            else:
                self.ask_capacity_cushion = prev_day.ask_capacity_cushion

            if self.ask_capacity_cushion < 0:
                self.ask_capacity_cushion = 0
            elif self.ask_capacity_cushion > self.ask_capacity_target_cushion:
                self.ask_capacity_cushion = self.ask_capacity_target_cushion

             # Effective Ask Capacity Changes - Cushion
            if natural_price > self.upper_target_cushion and natural_price <= self.upper_target_wall:
                self.ask_change_cushion_ohm = prev_day.ask_capacity_cushion - self.ask_capacity_cushion
                self.ask_change_cushion_usd = self.upper_target_cushion * (prev_day.ask_capacity_cushion - self.ask_capacity_cushion)
            else:
                self.ask_change_cushion_ohm = 0
                self.ask_change_cushion_usd = 0
            
            if self.ask_change_cushion_ohm > prev_day.ask_capacity_cushion:  # ensure that change is smaller than capacity left
                self.ask_change_cushion_ohm = prev_day.ask_capacity_cushion
                self.ask_change_cushion_usd = prev_day.ask_capacity_cushion * self.upper_target_cushion
                            
            # Real Ask Capacity - Totals
            if (sum(self.ask_counter) >= params.min_counter_reinstate or params.with_reinstate_window == 'No') and natural_price < self.upper_target_cushion:
                self.ask_capacity = self.ask_capacity_target
            elif natural_price > self.upper_target_wall:
                self.ask_capacity = self.upper_target_wall and prev_day.ask_capacity - (self.net_flow - self.reserves_in + prev_day.liq_usd) / self.upper_target_wall + (self.k / self.upper_target_wall) ** (1/2) or 0
            else:
                self.ask_capacity = prev_day.ask_capacity - self.ask_change_cushion_ohm # update capacity total to account for the cushion

            if self.ask_capacity < 0:
                self.ask_capacity = 0
            elif self.ask_capacity > self.ask_capacity_target:
                self.ask_capacity = self.ask_capacity_target

            if self.ask_capacity_cushion > self.ask_capacity:
                self.ask_capacity_cushion = self.ask_capacity

            # Effective Ask Capacity Changes - Totals
            if natural_price <= self.upper_target_wall: #if wall wasn't used, update with cushion
                self.ask_change_ohm = self.ask_change_cushion_ohm
                self.ask_change_usd = self.ask_change_cushion_usd
            else:
                self.ask_change_ohm = prev_day.ask_capacity - self.ask_capacity
                self.ask_change_usd = self.ask_change_cushion_usd + (prev_day.ask_capacity - self.ask_capacity - self.ask_change_cushion_ohm) * self.upper_target_wall
            
            if self.ask_change_ohm > prev_day.ask_capacity:  # ensure that change is smaller than capacity left
                self.ask_change_ohm = prev_day.ask_capacity
                self.ask_change_usd = prev_day.ask_capacity * self.upper_target_wall
        

            # Liquidity and Reserves
            self.liq_usd = max(prev_day.liq_usd + self.net_flow - self.reserves_in + self.bid_change_usd - self.ask_change_usd, 0)
            self.liq_ohm = self.liq_usd and self.k / self.liq_usd or 0  # ensure that if liq_usd is 0 then liq_ohm is 0 as well
            self.price = self.liq_ohm and self.liq_usd / self.liq_ohm or 0  # ensure that if liq_ohm is 0 then price is 0 as well

            self.reserves_out = self.liq_usd - prev_day.liq_usd - self.net_flow
            self.reserves = max(prev_day.reserves - self.reserves_out, 0)
            self.prev_reserves = prev_day.reserves

            self.ohm_traded = (self.price + prev_day.price) and (-2) * self.reserves_out / (self.price + prev_day.price) or 0
            self.cum_ohm_purchased = prev_day.cum_ohm_purchased - self.ohm_traded
            #self.cum_ohm_burnt = prev_day.cum_ohm_burnt - min(self.ohm_traded, 0)            
            #self.cum_ohm_minted = prev_day.cum_ohm_minted + max(self.ohm_traded, 0)
            self.cum_ohm_burnt = prev_day.cum_ohm_burnt + prev_day.bid_change_ohm
            self.cum_ohm_minted = prev_day.cum_ohm_minted + prev_day.ask_change_ohm


            #still necessary? set it to zero, but need to double check with Zeus (cause he maintained it on his model)
            # Release Capture
            if self.day % params.short_cycle == 0:
                self.release_capture = (-1) * self.reserves_out * params.release_capture
            else:
                self.release_capture = 0


        if self.day == 1:
            self.floating_supply = self.supply - self.liq_ohm
        else:
            self.supply = self.floating_supply + self.liq_ohm

        self.net_flow_and_bond = self.net_flow - self.reserves_in
        self.treasury = self.liq_usd + self.reserves
        self.mcap = self.supply * self.price
        self.floating_mcap = self.floating_supply * self.price

        self.liq_ratio = self.treasury and self.liq_usd / self.treasury or 0
        self.reserves_ratio = self.liq_usd and self.reserves / self.liq_usd or 0
        self.fmcap_treasury_ratio = self.treasury and self.floating_mcap / self.treasury or 0
        self.liq_fmcap_ratio = self.floating_mcap and self.liq_usd / self.floating_mcap or 0

        self.total_demand = self.market_demand
        self.total_supply = self.market_supply
        self.total_net = self.total_demand + self.total_supply

        self.control_ask = sum(self.ask_counter)
        self.control_bid = sum(self.bid_counter)

        # Only for reporting purposes (to check calculations)
        prev_lags['price'][1][self.day] = self.price
        prev_lags['target'][1][self.day] = self.ma_target
        prev_lags['gohm price variation'][1][self.day] = self.price * (1 + self.reward_rate)        
        self.gohm_volatility = calc_gohm_volatility(prev_lags=prev_lags)


# Target price controller
def calc_price_target(params:ModelParams, prev_day:Day, prev_lags:Dict[int, Tuple[int, Dict[int, float]]]):
    if params.target_price_function == 'avg_lags':
        if prev_day.day % (params.short_cycle) == 0:
            s = 0
            lag_keys = set(prev_lags.keys()) - set(['price', 'target', 'natural', 'avg'])
            for key in lag_keys:
                days = prev_lags[key][1].keys()
                s += prev_lags[key][1][max(days)]
            avg_lag = s / len(lag_keys)
            return (prev_day.natural_target + avg_lag) / 2
        else:
            return prev_day.ma_target

    elif params.target_price_function == 'price_cycle_avg':
        if prev_day.day % (params.short_cycle) == 0:
            s = 0
            days = len(prev_lags['price'][1]) - 1
            days_reweight = int(params.short_cycle)
            if days > params.short_cycle:
                for i in range(days - days_reweight, days):
                    s += prev_lags['price'][1][i]
                return s / days_reweight
            else:
                 return prev_day.ma_target
        else:
            return prev_day.ma_target
            
    elif params.target_price_function == 'price_moving_avg':
        s = 0
        days = len(prev_lags['price'][1]) - 1
        days_ma = int(params.target_ma)
        if days > params.target_ma:
            for i in range(days - days_ma, days):
                s += prev_lags['price'][1][i]
            return s / days_ma
        #elif days > 5:
        #    for i in range (1, days):
        #        s += prev_lags['price'][1][i]
        #    return s / days
        #else:
        #    return prev_day.ma_target
        elif days == 0:
            return prev_day.ma_target
        else:
            for i in range (1, days):
                s += prev_lags['price'][1][i]
            s += prev_lags['price'][1][1] * (params.target_ma - days)
            return s / params.target_ma


#price target functions
def calc_natural_target(params:ModelParams, prev_day:Day):
    if prev_day.day % (params.short_cycle) == 0:
      if prev_day.day % (params.short_cycle * 4) == 0:
        return ((prev_day.natural_target * prev_day.reserves / prev_day.prev_reserves) + prev_day.ma_target) / 2
      else:
        return prev_day.natural_target * prev_day.reserves / prev_day.prev_reserves
    else:
        return prev_day.natural_target


def calc_lag(day:int, params:ModelParams, prev_lags:Dict[int, Tuple[int, Dict[int, float]]], num_days:int=3):
    for key, values in prev_lags.items():
        if key not in ('price', 'target', 'natural', 'avg'):
          lag_days = values[0]
          if day > lag_days:
              if key == 'lag1':
                  if day > params.short_cycle:
                      s = prev_lags['price'][1][day-1]
                      for i in range(1, num_days):
                          s += prev_lags['price'][1][day - (i * lag_days)]
                      prev_lags[key][1][day] = s / num_days
                  else:
                    prev_lags[key][1][day] = values[1][day - 1]
              else:
                prev_lags[key][1][day] = prev_lags['lag1'][1][day - values[0]]
          else:
            prev_lags[key][1][day] = values[1][day - 1]


# gOHM volatility
def calc_gohm_volatility(prev_lags:Dict[int, Tuple[int, Dict[int, float]]]):
    days = len(prev_lags['gohm price variation'][1]) - 1
    data = list(prev_lags['gohm price variation'][1].values())
    if days > 6:
        if np.mean(data[-6:]) == 0:
           return 0
        else:
            return np.std(data[-6:])/np.mean(data[-6:])
    else:
        return 0
