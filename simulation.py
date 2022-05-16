import pandas as pd
import numpy as np
import random
import optuna
import os
from google.cloud import bigquery
from google.oauth2 import service_account

from plotly.subplots import make_subplots
import plotly.express as px
pd.options.plotting.backend = "plotly"

from src.utils import ModelParams, Day, short_sin, short_cos, long_sin, long_cos
from src.init_functions import initial_params

study_seed = 0
private_key = os.environ["BIGQUERY_SECRET"]

client = bigquery.Client(credentials=service_account.Credentials.from_service_account_info(private_key))

# Simulate scenario with market operations
def simulate (max_liq_ratio, ask_factor, cushion_factor, lower_wall, lower_cushion, mint_sync_premium, with_reinstate_window, with_dynamic_reward_rate, seed):
    netflow_type, historical_net_flows, price, target, supply, reserves, liq_usd = initial_params(
        netflow_type = 'random' # determines the netflow types. Either 'historical', 'random', or 'cycles' (sin/cos waves)
        ,initial_date = '2021/12/18' # determines the initial date to account for 'historical' netflows and initial params. (example: '2021/12/18')
        ,initial_supply = 25000000
        ,initial_reserves = 340000000
        ,initial_liq_usd = 70000000
        ,initial_price = 30
        ,initial_target = 30
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

        ,demand_factor = 0.008  # % of OHM supply expected to drive market demand.
        ,supply_factor = -0.008  # % of OHM supply expected to drive market sell preasure.
        ,arb_factor = 0  # initial arb factor
        ,release_capture = 0  # % of reweight taken immediately by the market. --> I think it doesn't make sense anymore, that's why I set it to 0.

        ,max_liq_ratio = max_liq_ratio  # liquidityUSD : reservesUSD ratio --> 1:1 = 0.5
        ,min_premium_target = mint_sync_premium  # minimum premium to keep adding liquidity as supply grows (mint & sync).
        ,max_outflow_rate = 0.0033 # max % of reservesUSD that can be released on a single day
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



def objective(trial):
    global study_seed
    r = 0

    trial.set_user_attr("seed", study_seed)
    simulation = simulate(seed = study_seed
        ,max_liq_ratio = trial.suggest_float('maxLiqRatio', 0.1, 0.5, step=0.025)
        ,ask_factor = trial.suggest_float('askFactor', 0.01, 0.1,  step=0.005)
        ,cushion_factor = trial.suggest_float('cushionFactor', 0.1, 0.5, step=0.025)
        ,lower_wall = trial.suggest_float('wall', 0.2, 0.3, step=0.01)
        ,lower_cushion = trial.suggest_float('cushion', 0.1, 0.2, step=0.01)
				,mint_sync_premium = trial.suggest_int('mintSyncPremium', 0, 3, step=1)
				,with_reinstate_window = trial.suggest_categorical('withReinstateWindow', ['Yes','No'])
				,with_dynamic_reward_rate = trial.suggest_categorical('withDynamicRR', ['Yes','No'])
    )

    for day, data in simulation.items():
        r += data.treasury * data.mcap / (1 + data.gohm_volatility)
    return r


def get_trial_variables(from_df):
    
    result_df = pd.DataFrame(columns = ['key', 'day', 'netFlow', 'price', 'realTarget', 'lowerTargetCushion', 'upperTargetCushion', 'lowerTargetWall', 'upperTargetWall', 'liqUSD', 'liqOHM', 'poolK', 'reservesUSD', 'reserveChange', 'reservesIN', 'reservesOUT', 'tradedOHM', 'treasury', 'supply', 'marketcap', 'floatingSupply', 'floatingMarketcap', 'liqRatio_liqTreasury', 'liqRatio_liqReserves', 'reserveRatio', 'liqFloatingMCRatio', 'floatingMCTreasuryPremium', 'cumPurchasedOHM', 'cumBurntOHM', 'bidCapacity', 'askCapacity', 'bidCapacityCushion', 'askCapacityCushion', 'bidCapacityTargetCushion', 'askCapacityTargetCushion', 'bidCapacityTarget', 'askCapacityTarget', 'askCount', 'bidCount', 'marketDemand', 'marketSupply', 'netTotal', 'gohm7dVolatility']) 
        
    for key, value in from_df.iterrows():
        simulation = simulate(seed = value['seed']
            ,max_liq_ratio = value['maxLiqRatio']
            ,ask_factor = value['askFactor']
            ,cushion_factor = value['cushionFactor']
            ,lower_wall = value['wall']
            ,lower_cushion = value['cushion']
            ,mint_sync_premium = value['mintSyncPremium']
            ,with_reinstate_window = value['withReinstateWindow']
            ,with_dynamic_reward_rate = value['withDynamicRR']
        )

        for day, data in simulation.items():
            result_df.loc[data.day] = [f'{value["seed"]}_{key}', data.day, float(data.net_flow), float(data.price), float(data.ma_target), float(data.lower_target_cushion), float(data.upper_target_cushion), float(data.lower_target_wall), float(data.upper_target_wall), float(data.liq_usd), float(data.liq_ohm), float(data.k), float(data.reserves), float(100*data.reserves/data.prev_reserves), float(data.reserves_in), float(data.reserves_out), float(data.ohm_traded), float(data.treasury), float(data.supply), float(data.mcap), float(data.floating_supply), float(data.floating_mcap), float(data.liq_ratio), float(data.liq_usd/data.reserves), float(data.reserves_ratio), float(data.liq_fmcap_ratio), float(data.fmcap_treasury_ratio), float(data.cum_ohm_purchased), float(data.cum_ohm_burnt), data.bid_capacity, data.ask_capacity, data.bid_capacity_cushion, data.ask_capacity_cushion, data.bid_capacity_target_cushion, data.ask_capacity_target_cushion, data.bid_capacity_target, data.ask_capacity_target, data.control_ask, data.control_bid, data.market_demand, data.market_supply, data.total_net, data.gohm_volatility]

    return result_df



# Simulate different parameter configurations with different seeds
for i in range (0, 1000):
    global study_seed
    study_seed = i
    study_name=f"study{i}"
    study = optuna.create_study(study_name=study_name, storage=f"sqlite:///{study_name}.db", direction='maximize')
    study.optimize(objective, n_trials = 10000)
    study_df = study.trials_dataframe()
    study_df['key'] = study_df.user_attrs_seed.astype(str) + '_' + study_df.index.astype(str)
    parameters_df = pd.DataFrame.reindex(study_df, columns = ['key', 'user_attrs_seed', 'value', 'params_maxLiqRatio', 'params_askFactor', 'params_cushionFactor', 'params_wall', 'params_cushion', 'params_mintSyncPremium', 'params_withReinstateWindow', 'params_withDynamicRR'])

    # Clean df names
    for name in parameters_df.columns:
        if name[:7] == 'params_':
            parameters_df.rename(columns={name:name[7:]}, inplace=True)
        elif name[:11] == 'user_attrs_':
            parameters_df.rename(columns={name:name[11:]}, inplace=True)

    # Save data into BigQuery
    table_id = 'simulation.parameters'
    parameters_df.to_gbq(destination_table=table_id, project_id='range-stability-model', credentials=service_account.Credentials.from_service_account_info(private_key), if_exists = 'append')

    # Get all the historical data from the simulated scenario
    historical_df = get_trial_variables(parameters_df)

    # Save data into BigQuery
    table_id = 'simulation.historical'
    historical_df.to_gbq(destination_table=table_id, project_id='range-stability-model', credentials=service_account.Credentials.from_service_account_info(private_key), if_exists = 'append')