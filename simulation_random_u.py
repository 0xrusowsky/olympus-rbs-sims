import pandas as pd
import numpy as np
import random
import time
import os
from google.cloud import bigquery

from src.utils import ModelParams, Day, short_sin, short_cos, long_sin, long_cos
from src.init_functions import initial_params

print("Starting seeds 0-10k")

# Initialize BigQuery Client
client = bigquery.Client()

# Import Dataset and Table ID + Initial values for protocol variables
with open('src/price.txt') as f:
    initial_variables=[]
    lines = f.readlines()
    table_id = lines[0].split()[1]
    for line in lines[2:]:
        p = line.split()
        initial_variables.append(float(p[1]))

# Set table schema and to overwrite
job_config = bigquery.LoadJobConfig(
    autodetect=True,
    write_disposition="WRITE_APPEND",
)


# Simulate scenario with market operations
def model_inputs (initial_variables, max_liq_ratio, ask_factor, cushion_factor, lower_wall, lower_cushion, mint_sync_premium, with_reinstate_window, with_dynamic_reward_rate, seed):
    netflow_type, historical_net_flows, price, target, supply, reserves, liq_usd = initial_params(
        netflow_type = 'random' # determines the netflow types. Either 'historical', 'random', or 'cycles' (sin/cos waves)
        ,initial_date = '2021/12/18' # determines the initial date to account for 'historical' netflows and initial params. (example: '2021/12/18')
        ,initial_supply = initial_variables[0]
        ,initial_reserves = initial_variables[1]
        ,initial_liq_usd = initial_variables[2]
        ,initial_price = initial_variables[3]
        ,initial_target = initial_variables[4]
    )

    params = ModelParams(seed = seed  # seed number so all the simulations use the same randomness
        ,horizon = 365  # simulation timespan.
        ,short_cycle = 30  # short market cycle duration.
        ,cycle_reweights = 1  # reweights per short market cycle.
        ,long_cycle = 730  # long market cycle duration.
        ,long_sin_offset = 2  # demand function offset.
        ,long_cos_offset = 0  # supply function offset.
        ,supply_amplitude = 0.8  # supply function amplitude.

        # Initial Parameters
        ,initial_supply = supply, initial_reserves = reserves, initial_liq_usd = liq_usd, initial_price = price, initial_target = target, target_price_function = 'price_moving_avg', netflow_type = netflow_type

        ,demand_factor = 0.016  # % of OHM supply expected to drive market demand.
        ,supply_factor = -0.016  # % of OHM supply expected to drive market sell preasure.
        ,arb_factor = 0  # initial arb factor
        ,release_capture = 0  # % of reweight taken immediately by the market. --> I think it doesn't make sense anymore, that's why I set it to 0.

        ,max_liq_ratio = max_liq_ratio  # liquidityUSD : reservesUSD ratio --> 1:1 = 0.5
        ,min_premium_target = mint_sync_premium  # minimum premium to keep adding liquidity as supply grows (mint & sync).
        ,max_outflow_rate = 0.05 # max % of reservesUSD that can be released on a single day
        ,reserve_change_speed = 1  # directly related to the speed at which reserves are released/captured by the treasury. The higher the slower.
        ,with_reinstate_window = with_reinstate_window # determines if there is a minimum counter to reinstate the capacity to perform operations or not
        ,with_dynamic_reward_rate = with_dynamic_reward_rate # determines if there is less supply expansion when price < wall


        ,ask_factor = ask_factor  # % of floating supply that the treasury can deploy when price is trading above the upper target.
        ,bid_factor = ask_factor  # % of the reserves that the treasury can deploy when price is trading below the lower target.
        ,cushion_factor = cushion_factor  # the percentage of a bid or ask to offer as a cushion.
        ,target_ma = 30  # length of the price target moving average (in days).
        ,lower_wall = lower_wall  # determines lower wall price target at x% below the target price.
        ,upper_wall = lower_wall  # determines upper wall price target at x% above the target price.
        ,lower_cushion = lower_cushion  # determines lower cushion price target at x% below the target price.
        ,upper_cushion = lower_cushion  # determines upper cushion price target at x% above the target price.
        ,reinstate_window = 7 # the window of time (in days) to reinstate a bid or ask.
        ,min_counter_reinstate = 6 # number of days within the reinstate window that conditions are true to reinstate a bid or ask.
    )

    lags = {
        'price': (0, {1: params.initial_price}), 'target': (0, {1: params.initial_target}), 'avg': (0, {1: params.initial_target}), 'gohm price variation': (0, {1: params.initial_price})
    }

    arbs = {}

    random.seed(params.seed)

    if historical_net_flows is None:
        simulation = {'day1': Day(params=params, prev_arbs=arbs, prev_lags=lags)}
        for i in range (2, params.horizon):
            simulation[f'day{i}'] = Day(params=params, prev_arbs=arbs, prev_lags=lags, prev_day=simulation[f'day{i-1}'])
    else:
        simulation = {'day1': Day(params=params, prev_arbs=arbs, prev_lags=lags, historical_net_flows=historical_net_flows[0])}
        for i in range (2, min(params.horizon, len(historical_net_flows) - 1)):
            simulation[f'day{i}'] = Day(params=params, prev_arbs=arbs, prev_lags=lags, prev_day=simulation[f'day{i-1}'], historical_net_flows=historical_net_flows[i-2])

    return simulation

def model_distributions(seed, trial, initial_variables):
    r = 0
    random.seed(seed*trial + trial)

    trial_params = (0.225 #random.choice([i/1000 for i in range(100, 501, 25)])
                   ,0.075 #random.choice([i/1000 for i in range(10, 101, 5)])
                   ,0.3 #random.choice([i/1000 for i in range(100, 501, 25)])
                   ,0.03 #random.choice([i/100 for i in range(20, 31, 1)])
                   ,0.15 #random.choice([i/100 for i in range(10, 21, 1)])
                   ,0 #random.choice([i for i in range(0, 4, 1)])
                   ,'Yes' #random.choice(['Yes','No'])
                   ,'No' #random.choice(['Yes','No'])
                   )

    simulation = model_inputs(seed = seed
                              ,max_liq_ratio = trial_params[0]
                              ,ask_factor = trial_params[1]
                              ,cushion_factor = trial_params[2]
                              ,lower_wall = trial_params[3]
                              ,lower_cushion = trial_params[4]
                              ,mint_sync_premium = trial_params[5]
                              ,with_reinstate_window = trial_params[6]
                              ,with_dynamic_reward_rate = trial_params[7]
                              ,initial_variables = initial_variables)

    for day, data in simulation.items():
        r += data.treasury * data.mcap / (1 + data.gohm_volatility)

    return (seed, trial_params, r)


# Simulate different parameter configurations with different seeds
parameters_df = pd.DataFrame(columns = ['key', 'seed', 'value', 'maxLiqRatio', 'askFactor', 'cushionFactor', 'wall', 'cushion', 'mintSyncPremium', 'withReinstateWindow', 'withDynamicRR'])
for i in range (0, 5000):
    seed = i
    for j in [21]:
        seed, trial_params, r = model_distributions(i, j, initial_variables)
        parameters_df.loc[i] = [str(f'{seed}_{str(j).zfill(3)}'), seed, r, trial_params[0], trial_params[1], trial_params[2], trial_params[3], trial_params[4], trial_params[5], trial_params[6], trial_params[7]]

# Load updated data
print(f"seed {seed} status | START uploading data into BigQuery")
job = client.load_table_from_dataframe(
    parameters_df, table_id, job_config=job_config, location="US"
)
job.result()
print(f"seed {seed} status | END uploading data into BigQuery")

# Print out confirmed job details
table = client.get_table(table_id)
print(
    "seed status | Loaded {} rows and {} columns to {}".format(
        table.num_rows, len(table.schema), table_id
    )
)