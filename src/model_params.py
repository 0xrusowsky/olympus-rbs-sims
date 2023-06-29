from dataclasses import dataclass

@dataclass
class ModelParams():
    # MARKET BEHAVIOR PARAMETERS
    seed:int
    netflow_type:str # random, historical, or sin/cos waves
    horizon:int
    demand_factor:float
    supply_factor:float # We want to influence the randomness toward a specific outcome (bullish = demand, bearish = supply) 
    arb_factor:float # Deprecated. No arbitrage assumptions since Montecarlos was used to model market behavior.
    cycle_reweights:float # Deprecated
    reserve_change_speed:float # Deprecated
    short_cycle:int # Only applicable for market behavior assumptions = sin/cos waves. Not used for sims since Montecarlo was used.
    long_cycle:int  # Only applicable for market behavior assumptions = sin/cos waves. Not used for sims since Montecarlo was used.
    long_sin_offset:float # Only applicable for market behavior assumptions = sin/cos waves. Not used for sims since Montecarlo was used.
    long_cos_offset:float # Only applicable for market behavior assumptions = sin/cos waves. Not used for sims since Montecarlo was used.
    supply_amplitude:int # Only applicable for market behavior assumptions = sin/cos waves. Not used for sims since Montecarlo was used.

    # PROTOCOL-RELATED PARAMETERS
    max_liq_ratio:float
    min_premium_target:int # Deprecated
    release_capture:float # Deprecated.
    max_outflow_rate:float # Limits how much PCV can leave the treasury per some period of time
    with_reinstate_window:str # Implemented as YES.
    with_dynamic_reward_rate:str # Implemented as NO. After OIP 119 regardless of the scenario, reward rate is fixed.

    # MARKET OPERATIONS-RELATED PARAMETERS
    target_ma:float # 30-day moving average
    lower_wall:float
    upper_wall:float
    lower_cushion:float
    upper_cushion:float
    bid_factor:float
    ask_factor:float
    cushion_factor:float
    reinstate_window:int
    min_counter_reinstate:int

    # INITIAL PROTOCOL PARAMETERS - these get passed in the simulation.ipynb
    initial_supply:float
    initial_reserves_stables:float
    initial_reserves_volatile:float
    initial_liq_stables:float
    initial_price:float
    initial_target:float
    target_price_function:str
    
    # Initialize any derived variables.
    def __post_init__(self):
        self.initial_liq_backing = self.initial_reserves_stables + self.initial_reserves_volatile + self.initial_liq_stables
