import pandas as pd
import math
from typing import Dict, List, Tuple

# Get initial params based on historical data
def initial_params(netflow_type:str, initial_date:str=None, initial_supply:float=None, initial_reserves:float=None, initial_liq_usd:float=None, initial_price:float=None, initial_target:float=None):
    if netflow_type == 'historical' and initial_date is not None:
        historical_df = pd.read_csv('/content/liquidity-olympus/data/historical_ohm_data.csv', usecols= ['date','net_flows', 'price', 'supply'])
        initial_index = historical_df[historical_df == initial_date]['date'].dropna().index[0]
        historical_net_flows = historical_df[historical_df.index >= initial_index]['net_flows'].tolist()
        price, supply = historical_df.iloc[initial_index, [historical_df.columns.get_loc(c) for c in ['price', 'supply']]]
    else:
        historical_net_flows = None
        price = initial_price
        supply = initial_supply

    target = price
    reserves = initial_reserves
    liq_usd = initial_liq_usd
    
    return netflow_type, historical_net_flows, price, target, supply, reserves, liq_usd