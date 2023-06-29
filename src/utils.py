import random
import math
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from src.model_params import ModelParams
from src.day import Day


# Get initial params based on historical data
# initial_date - Determines the initial date to account for 'historical' netflows and initial params. (example: '2021/12/18')
# NOTE: This function supercedes initial_functions.py.
def get_historical_net_flows(netflow_type:str, netflow_data:str=None, initial_date:str=None):
    if netflow_type == 'historical' and initial_date is not None:
        historical_df = pd.read_csv('data/historical_ohm_data.csv', usecols= ['date','net_flows', 'price', 'supply','liquidity','reserves','reserves_volatile'])
        initial_index = historical_df[historical_df == initial_date]['date'].dropna().index[0]
        return historical_df[historical_df.index >= initial_index]['net_flows'].tolist()
    elif netflow_type == 'enforced':
        f = open(f'./data/sim-vs-testnet/sim-results-{netflow_data}.json')
        data = json.load(f)
        df = pd.json_normalize(data)
        f.close()
        return df['netFlow'].apply(lambda x: round(float(x),2)).tolist()
    else:
        return None


# NOTE: Not that important since we were just ideating. After OIP 119 regardless of the scenario, reward rate is fixed.
# reserves_in is amount added to LP (as part of POL) so is tracked likewise. Assumption is xy=k so you get amount of OHM out.
def calculate_reward_rate(params:ModelParams, prev_day=None):
    if prev_day.fmcap_treasury_ratio < 1:  # below backing
        return rr_framework(prev_day.supply, params.with_dynamic_reward_rate, -3)
    elif prev_day.price < prev_day.lower_target_wall:  # below wall
        return rr_framework(prev_day.supply, params.with_dynamic_reward_rate, -2)
    elif prev_day.price < prev_day.lower_target_cushion:  # below cushion
        return rr_framework(prev_day.supply, params.with_dynamic_reward_rate, -1)
    elif prev_day.fmcap_treasury_ratio > 3:  # above 3x premium
        return rr_framework(prev_day.supply, params.with_dynamic_reward_rate, 2)
    elif prev_day.price > prev_day.lower_target_wall:  # above wall
        return rr_framework(prev_day.supply, params.with_dynamic_reward_rate, 1)
    else:  # inside the range
        return rr_framework(prev_day.supply, params.with_dynamic_reward_rate, 0)


# Reward rate framework
def rr_framework(supply:int, with_dynamic_reward_rate:str, rr_controller:int, version="flat"):
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

    if version == "flat":
        return 0.000198 # (1 + r) ^ 365 ~ 7.5%

    else:
        if with_dynamic_reward_rate == 'No':
            return r
        else:
            if version == "v0":  # controller v0
                if rr_controller != 9:
                    return r/2

            elif version == "v1":  # controller v1
                if rr_controller == -3:  # below backing
                    return 0
                elif rr_controller == -2:  # below wall
                    return r * (0.5)
                elif rr_controller == -1:  # below cushion
                    return r * (0.75)
                elif rr_controller == 2:  # above premium of 3
                    return r * (1.25)
                elif rr_controller == 1:  # above wall
                    return r * (1.125)
                elif rr_controller == 0:  # inside range, as usual
                    return r


# Target price controller
def calc_price_target(params:ModelParams, prev_day:Day, prev_lags:Dict[int, Tuple[int, Dict[int, float]]]):
    if params.target_price_function == 'price_moving_avg':
        s = 0
        days = len(prev_lags['price'][1]) - 1
        days_ma = int(params.target_ma)
        if days > params.target_ma:
            for i in range(days - days_ma, days):
                s += prev_lags['price'][1][i+1]
            return s / days_ma
        elif days == 0:
            return prev_day.ma_target
        else:
            for i in range (0, days):
                s += prev_lags['price'][1][i+1]
            s += prev_lags['price'][1][1] * (params.target_ma - days)
            return s / params.target_ma

    # Deprecated
    elif params.target_price_function == 'avg_lags':
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

    # Deprecated
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


# Market behavior simulation functions - Deprecated
def short_sin(day:int, cycle:int):
    value = 1.5 + (0.5 * math.sin((day + 1.5 * cycle) / (cycle / (2*math.pi))))
    return value


def short_cos(day:int, cycle:int):
    value = 1.55 + (0.5 * math.cos((day + 0.5 * cycle) / (cycle / (2*math.pi))))
    return value


def long_sin(day:int, cycle:int, offset:float):
    value = 1 + (0.5 * math.sin(((day + cycle * offset) % cycle) / (cycle / (2*math.pi)))) * (10 - (day / cycle)) / 10
    return value


def long_cos(day:int, cycle:int, offset:float, amplitude:float):
    value = amplitude * (1 + (0.5 * math.cos(((day + 2 * cycle * offset) % (2 * cycle)) / (cycle / math.pi))) * (10 - (day / (2 * cycle))) / 10 )
    return value