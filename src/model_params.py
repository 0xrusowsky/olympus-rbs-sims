from dataclasses import dataclass
import pandas as pd

@dataclass
class ModelParams():
    # INITIAL PROTOCOL PARAMETERS - these get passed in the simulation.ipynb
    initial_supply:float = 25000000 # Starting supply of OHM
    initial_reserves_stables:float = 170000000 # rename to initial_reserves and drop initial_resrves_volatile. rename code.
    initial_reserves_volatile:float = 25000000
    initial_liq_stables:float = 21000000 # initial_liq_stables -> this will become OHM-ETH liquidity. However, need to consider OHM-stables liquidity as that can impact RBS.
    initial_price:float = 9.5  # used to determine amount of OHM in pool and therefore K. Change to OHM in ETH terms.
    initial_target:float = 9.5 # we can just it to liquid backing.
    target_price_function:str = 'price_moving_avg'

    # MARKET BEHAVIOR PARAMETERS
    netflow_type:str  # Determines the netflow types. Either 'historical', 'enforced', 'random', or 'cycles' (sin/cos waves)
    seed:int = 69 # Seed number to control simulation randomness
    horizon:int = 365  # Simulation timespan
    demand_factor:float = 0.007 # % of OHM supply expected to drive market demand
    supply_factor:float = -0.007  # % of OHM supply expected to drive market sell preasure# We want to influence the randomness toward a specific outcome (bullish = demand, bearish = supply) 
    
    # PROTOCOL-RELATED PARAMETERS
    max_liq_ratio:float  = 0.14375  # LiquidityUSD : reservesUSD ratio --> 1:1 = 0.5
    max_outflow_rate:float  = 0.05  # Max % of reservesUSD that can be released on a single day # Limits how much PCV can leave the treasury per some period of time
    with_reinstate_window:str = 'Yes'
    with_dynamic_reward_rate:str = 'No' # Implemented as NO. After OIP 119 regardless of the scenario, reward rate is fixed.

    # RBS PARAMETERS
    target_ma:float  = 30  # Length of the price target moving average (in days) # 30-day moving average
    lower_wall:float = 0.15  # Determines lower wall price target at x% below the target price
    upper_wall:float = 0.15  # Determines upper wall price target at x% above the target price
    lower_cushion:float = 0.075  # Determines lower cushion price target at x% below the target price
    upper_cushion:float = 0.075  # Determines upper cushion price target at x% above the target price
    bid_factor:float = 0.095  # % of the reserves that the treasury can deploy when price is trading below the lower target
    ask_factor:float = 0.095  # % of floating supply that the treasury can deploy when price is trading above the upper target
    cushion_factor:float = 0.3075  # The percentage of a bid or ask to offer as a cushion
    reinstate_window:int = 7  # The window of time (in days) to reinstate a bid or ask
    min_counter_reinstate:int = 6  # Number of days within the reinstate window that conditions are true to reinstate a bid or ask

    # DEPRECATED
    min_premium_target:int  = 0  # Minimum premium for mint&sync --> to keep adding liquidity as supply grows  # Deprecated
    release_capture:float  = 0  # % of reweight taken immediately by the market (Deprecated) # Deprecated.
    reserve_change_speed:float  = 1  # Directly related to the speed at which reserves are released/captured by the treasury. The higher the slower # Deprecated
    arb_factor:float  = 0  # Initial arb factor # Deprecated. No arbitrage assumptions since Montecarlos was used to model market behavior.
    cycle_reweights:float = 1  # DEPRECATED> Reweights per short market cycle (Deprecated) # Deprecated
    short_cycle:int       = 30  # Short market cycle duration (only relevant for netflow_type == cycles) # Only applicable for market behavior assumptions = sin/cos waves. Not used for sims since Montecarlo was used.
    long_cycle:int        = 730  # Long market cycle duration (only relevant for netflow_type == cycles)  # Only applicable for market behavior assumptions = sin/cos waves. Not used for sims since Montecarlo was used.
    long_sin_offset:float = 2  # Demand function offset (only relevant for netflow_type == cycles) # Only applicable for market behavior assumptions = sin/cos waves. Not used for sims since Montecarlo was used.
    long_cos_offset:float = 0  # Supply function offset (only relevant for netflow_type == cycles) # Only applicable for market behavior assumptions = sin/cos waves. Not used for sims since Montecarlo was used.
    supply_amplitude:int  = 0.8  # Supply function amplitude (only relevant for netflow_type == cycles) # Only applicable for market behavior assumptions = sin/cos waves. Not used for sims since Montecarlo was used.


    # Initialize any derived variables.
    def __post_init__(self):
        self.initial_liq_backing = self.initial_reserves_stables + self.initial_reserves_volatile + self.initial_liq_stables

    # Determines the netflow types. Either 'historical', 'enforced', 'random', or 'cycles' (sin/cos waves)
    # If the netflow_type is historical or enforced, then overwrite initial values.
    def update_with_historical_flows(self, initial_date = None):
        if self.netflow_type == 'historical' and initial_date is not None:
            historical_df = pd.read_csv('data/historical_ohm_data.csv', usecols= ['date','net_flows', 'price', 'supply','liquidity','reserves','reserves_volatile'])
            initial_index = historical_df[historical_df == initial_date]['date'].dropna().index[0]
            self.initial_price, self.initial_supply, self.initial_liq_stables, self.initial_reserves_stables, self.initial_reserves_volatile = historical_df.iloc[initial_index, [historical_df.columns.get_loc(c) for c in ['price', 'supply','liquidity','reserves','reserves_volatile']]]
            self.initial_target = self.initial_price