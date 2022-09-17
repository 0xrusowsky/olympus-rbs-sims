import pandas as pd
import numpy as np
import random
import os
from google.cloud import bigquery

from src.utils import ModelParams, Day, short_sin, short_cos, long_sin, long_cos
from src.init_functions import initial_params

study_seed = 0

# Initialize BigQuery Client
client = bigquery.Client()

# Import Dataset and Table ID + Initial values for protocol variables
with open('src/price.txt') as f:
    initial_variables=[]
    lines = f.readlines()
    read_table_id = lines[0].split()[1]
    table_id = lines[1].split()[1]
    for line in lines[2:]:
        p = line.split()
        initial_variables.append(float(p[1]))


# Set table schema and to overwrite
job_config_upload = bigquery.LoadJobConfig(
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

def get_trial_variables(from_df, initial_variables):
    
    result_df = pd.DataFrame(columns = ['key', 'day', 'netFlow', 'price', 'realTarget', 'lowerTargetCushion', 'upperTargetCushion', 'lowerTargetWall', 'upperTargetWall', 'liqUSD', 'liqOHM', 'poolK', 'reservesUSD', 'reserveChange', 'reservesIN', 'reservesOUT', 'tradedOHM', 'treasury', 'supply', 'marketcap', 'floatingSupply', 'floatingMarketcap', 'liqRatio_liqTreasury', 'liqRatio_liqReserves', 'reserveRatio', 'liqFloatingMCRatio', 'floatingMCTreasuryPremium', 'cumPurchasedOHM', 'cumBurntOHM', 'bidCapacity', 'askCapacity', 'bidCapacityCushion', 'askCapacityCushion', 'bidCapacityTargetCushion', 'askCapacityTargetCushion', 'bidCapacityTarget', 'askCapacityTarget', 'askCount', 'bidCount', 'marketDemand', 'marketSupply', 'netTotal', 'gohm7dVolatility']) 
        
    for key, value in from_df.iterrows():
        simulation = model_inputs(seed = value['seed']
                                  ,max_liq_ratio = value['maxLiqRatio']
                                  ,ask_factor = value['askFactor']
                                  ,cushion_factor = value['cushionFactor']
                                  ,lower_wall = value['wall']
                                  ,lower_cushion = value['cushion']
                                  ,mint_sync_premium = value['mintSyncPremium']
                                  ,with_reinstate_window = value['withReinstateWindow']
                                  ,with_dynamic_reward_rate = value['withDynamicRR']
                                  ,initial_variables = initial_variables
                                  )

        for day, data in simulation.items():
            result_df.loc[len(result_df)] = [str(f'{value["key"]}'), float(data.day), float(data.net_flow), float(data.price), float(data.ma_target), float(data.lower_target_cushion), float(data.upper_target_cushion), float(data.lower_target_wall), float(data.upper_target_wall), float(data.liq_usd), float(data.liq_ohm), float(data.k), float(data.reserves), float(100*data.reserves/data.prev_reserves), float(data.reserves_in), float(data.reserves_out), float(data.ohm_traded), float(data.treasury), float(data.supply), float(data.mcap), float(data.floating_supply), float(data.floating_mcap), float(data.liq_ratio), float(data.liq_usd/data.reserves), float(data.reserves_ratio), float(data.liq_fmcap_ratio), float(data.fmcap_treasury_ratio), float(data.cum_ohm_purchased), float(data.cum_ohm_burnt), float(data.bid_capacity), float(data.ask_capacity), float(data.bid_capacity_cushion), float(data.ask_capacity_cushion), float(data.bid_capacity_target_cushion), float(data.ask_capacity_target_cushion), float(data.bid_capacity_target), float(data.ask_capacity_target), float(data.control_ask), float(data.control_bid), float(data.market_demand), float(data.market_supply), float(data.total_net), float(data.gohm_volatility)]

    return result_df


# Load data from BigQuery
t = 43

#------------
#seeds 0-1000
query = f"""select * from `{read_table_id}` where 0 <= seed and seed < 1000 and cast(right(key,3) as int64) = @trial order by seed asc"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("trial", "INT64", t),
        ]
    )
parameters_df = (
    client.query(query, job_config).result().to_dataframe(create_bqstorage_client=True)
)

print(f"Current config: {t}")
print(f"config {t} status | START Printing data pulled from BigQuery")
print(parameters_df)
print(f"config {t} status | END Printing data pulled from BigQuery")

# Get all the historical data from the simulated scenario
print(f"config {t} status | START Re-simulating data for all trials")
historical_df = get_trial_variables(parameters_df, initial_variables)
print(f"config {t} status | END Re-simulating data for all trials")
print(historical_df)

# Load updated data
print(f"config {t} status | START uploading data into BigQuery")
job = client.load_table_from_dataframe(
    historical_df, table_id, job_config=job_config_upload, location="US"
)
job.result()
print(f"config {t} status | END uploading data into BigQuery")

# Print out confirmed job details
table = client.get_table(table_id)
print(
    "config status | Loaded {} rows and {} columns to {}".format(
        table.num_rows, len(table.schema), table_id
    )
)


#------------
#seeds 1000-2000
query = f"""select * from `{read_table_id}` where 1000 <= seed and seed < 2000 and cast(right(key,3) as int64) = @trial order by seed asc"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("trial", "INT64", t),
        ]
    )
parameters_df = (
    client.query(query, job_config).result().to_dataframe(create_bqstorage_client=True)
)

print(f"Current config: {t}")
print(f"config {t} status | START Printing data pulled from BigQuery")
print(parameters_df)
print(f"config {t} status | END Printing data pulled from BigQuery")

# Get all the historical data from the simulated scenario
print(f"config {t} status | START Re-simulating data for all trials")
historical_df = get_trial_variables(parameters_df, initial_variables)
print(f"config {t} status | END Re-simulating data for all trials")
print(historical_df)

# Load updated data
print(f"config {t} status | START uploading data into BigQuery")
job = client.load_table_from_dataframe(
    historical_df, table_id, job_config=job_config_upload, location="US"
)
job.result()
print(f"config {t} status | END uploading data into BigQuery")

# Print out confirmed job details
table = client.get_table(table_id)
print(
    "config status | Loaded {} rows and {} columns to {}".format(
        table.num_rows, len(table.schema), table_id
    )
)



#------------
#seeds 2000-3000
query = f"""select * from `{read_table_id}` where 2000 <= seed and seed < 3000 and cast(right(key,3) as int64) = @trial order by seed asc"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("trial", "INT64", t),
        ]
    )
parameters_df = (
    client.query(query, job_config).result().to_dataframe(create_bqstorage_client=True)
)

print(f"Current config: {t}")
print(f"config {t} status | START Printing data pulled from BigQuery")
print(parameters_df)
print(f"config {t} status | END Printing data pulled from BigQuery")

# Get all the historical data from the simulated scenario
print(f"config {t} status | START Re-simulating data for all trials")
historical_df = get_trial_variables(parameters_df, initial_variables)
print(f"config {t} status | END Re-simulating data for all trials")
print(historical_df)

# Load updated data
print(f"config {t} status | START uploading data into BigQuery")
job = client.load_table_from_dataframe(
    historical_df, table_id, job_config=job_config_upload, location="US"
)
job.result()
print(f"config {t} status | END uploading data into BigQuery")

# Print out confirmed job details
table = client.get_table(table_id)
print(
    "config status | Loaded {} rows and {} columns to {}".format(
        table.num_rows, len(table.schema), table_id
    )
)


#------------
#seeds 3000-4000
query = f"""select * from `{read_table_id}` where 3000 <= seed and seed < 4000 and cast(right(key,3) as int64) = @trial order by seed asc"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("trial", "INT64", t),
        ]
    )
parameters_df = (
    client.query(query, job_config).result().to_dataframe(create_bqstorage_client=True)
)

print(f"Current config: {t}")
print(f"config {t} status | START Printing data pulled from BigQuery")
print(parameters_df)
print(f"config {t} status | END Printing data pulled from BigQuery")

# Get all the historical data from the simulated scenario
print(f"config {t} status | START Re-simulating data for all trials")
historical_df = get_trial_variables(parameters_df, initial_variables)
print(f"config {t} status | END Re-simulating data for all trials")
print(historical_df)

# Load updated data
print(f"config {t} status | START uploading data into BigQuery")
job = client.load_table_from_dataframe(
    historical_df, table_id, job_config=job_config_upload, location="US"
)
job.result()
print(f"config {t} status | END uploading data into BigQuery")

# Print out confirmed job details
table = client.get_table(table_id)
print(
    "config status | Loaded {} rows and {} columns to {}".format(
        table.num_rows, len(table.schema), table_id
    )
)




#------------
#seeds 4000-5000
query = f"""select * from `{read_table_id}` where 4000 <= seed and seed < 5000 and cast(right(key,3) as int64) = @trial order by seed asc"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("trial", "INT64", t),
        ]
    )
parameters_df = (
    client.query(query, job_config).result().to_dataframe(create_bqstorage_client=True)
)

print(f"Current config: {t}")
print(f"config {t} status | START Printing data pulled from BigQuery")
print(parameters_df)
print(f"config {t} status | END Printing data pulled from BigQuery")

# Get all the historical data from the simulated scenario
print(f"config {t} status | START Re-simulating data for all trials")
historical_df = get_trial_variables(parameters_df, initial_variables)
print(f"config {t} status | END Re-simulating data for all trials")
print(historical_df)

# Load updated data
print(f"config {t} status | START uploading data into BigQuery")
job = client.load_table_from_dataframe(
    historical_df, table_id, job_config=job_config_upload, location="US"
)
job.result()
print(f"config {t} status | END uploading data into BigQuery")

# Print out confirmed job details
table = client.get_table(table_id)
print(
    "config status | Loaded {} rows and {} columns to {}".format(
        table.num_rows, len(table.schema), table_id
    )
)

