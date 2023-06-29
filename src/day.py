import random
from typing import Dict, List, Tuple
from src.model_params import ModelParams
from src.utils import rr_framework, calc_gohm_volatility, calculate_reward_rate, calc_price_target

class Day():
    # Requires model parameters, 
    # prev_arbs = not really used anymore, 
    # prev_lags = stores historical price (to calculate moving average)
    # prev_day = stores previous day's data so we can update the system during state transition

    def __init__(self, params:ModelParams, prev_arbs:Dict[int, Tuple[float, float]], prev_lags=Dict[int, Tuple[int, Dict[int, float]]], prev_day=None, historical_net_flows=None):
        # Initialize variables for the first day
        if prev_day is None:
            self.initialize_first_day(params, prev_arbs)
        else:
            self.initialize_from_previous_day(params, prev_arbs, prev_lags, prev_day, historical_net_flows)

        # PROTOCOL VARIABLES (FOR REPORTING) 
        self.update_protocol_metrics(params, prev_lags)


    def initialize_first_day(self, params:ModelParams, prev_arbs:Dict[int, Tuple[float, float]]):
        self.day = 1
        self.supply = params.initial_supply
        self.reward_rate = rr_framework(self.supply, params.with_dynamic_reward_rate, 0)
        self.price = params.initial_price
        self.liq_stables = params.initial_liq_stables # This is initial liquidity stables, replace with ETH in liquidity pool
        self.liq_ohm = self.liq_stables / self.price # Calculate liquidity in OHM assuming xy=k invariant
        self.k = (self.liq_stables ** 2) / self.price # Calculate k invariant

        self.reserves_in = 0
        self.reserves_out = 0
        self.release_capture = 0  # Deprecated
        self.ohm_traded = 0
        self.cum_ohm_purchased = 0
        self.cum_ohm_burnt = 0
        self.cum_ohm_minted = 0
        self.reserves_stables = params.initial_reserves_stables
        self.prev_reserves = params.initial_reserves_stables

        self.ma_target = params.initial_target
        self.lb_target = params.initial_liq_backing / params.initial_supply
        self.target    = max(self.ma_target, self.lb_target)

        self.lower_target_wall = self.ma_target * (1 - params.lower_wall)
        self.upper_target_wall = self.ma_target * (1 + params.upper_wall)
        self.lower_target_cushion = self.ma_target * (1 - params.lower_cushion)
        self.upper_target_cushion = self.ma_target * (1 + params.upper_cushion)

        self.bid_capacity_target = params.bid_factor * self.reserves_stables
        self.ask_capacity_target = params.ask_factor * self.reserves_stables / self.upper_target_wall * (1 + params.lower_wall + params.upper_wall)
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

        self.net_flow = 0
        prev_arbs[self.day] = (self.arb_demand, self.arb_supply)
        
        self.bid_counter = [0] * params.reinstate_window
        self.ask_counter = [0] * params.reinstate_window
        self.target_liq_ratio_reached = False

    def initialize_from_previous_day(self, params:ModelParams, prev_arbs:Dict[int, Tuple[float, float]], prev_lags=Dict[int, Tuple[int, Dict[int, float]]], prev_day=None, historical_net_flows=None):
        self.day = prev_day.day + 1

        # -- PRE-MARKET OPERATIONS ---------------------------------------------------------------------------------------        
        # Update supply
        self.reward_rate = calculate_reward_rate(params, prev_day)
        self.supply = prev_day.price and max((prev_day.supply - prev_day.reserves_in / prev_day.prev_price + prev_day.ask_change_ohm - prev_day.bid_change_ohm) * (1 + self.reward_rate), 0) or 0

        # Rebalance treasury and update RBS parameters
        self.rebalance_treasury(params=params, prev_day=prev_day)
        self.k = prev_day.price and ((prev_day.liq_stables - self.reserves_in)**2 / prev_day.price) or 0  # Mint & sync has been deprecated
        self.update_rbs_parameters(params=params, prev_day=prev_day, prev_lags=prev_lags)

        # -- MARKET BEHAVIOR  ---------------------------------------------------------------------------------------
        # Simulate market behavior
        self.simulate_market_behavior(params=params, prev_day=prev_day, historical_net_flows=historical_net_flows)

        # Run RBS in response
        self.perform_rbs_operations(params=params, prev_day=prev_day)

        # -- MARKET CLOSE  ---------------------------------------------------------------------------------------
        # Update treasury mgetrics
        self.update_treasury_metrics(params=params, prev_day=prev_day)

    def update_protocol_metrics(self, params:ModelParams, prev_lags=Dict[int, Tuple[int, Dict[int, float]]]):
        self.floating_supply = max(self.supply - self.liq_ohm, 0)
        self.treasury_stables = self.liq_stables + self.reserves_stables
        self.liq_backing = self.treasury_stables + params.initial_reserves_volatile
        self.mcap = self.supply * self.price
        self.floating_mcap = self.floating_supply * self.price

        self.liq_ratio = self.treasury_stables and self.liq_stables / self.treasury_stables or 0
        self.target_liq_ratio_reached = True if self.liq_ratio >= params.max_liq_ratio else False
        self.reserves_ratio = self.liq_stables and self.reserves_stables / self.liq_stables or 0
        self.fmcap_treasury_ratio = self.treasury_stables and self.floating_mcap / self.treasury_stables or 0
        self.liq_fmcap_ratio = self.floating_mcap and self.liq_stables / self.floating_mcap or 0

        self.total_demand = self.market_demand  # + self.arb_demand
        self.total_supply = self.market_supply  # + self.arb_supply
        self.total_net = self.total_demand + self.total_supply

        self.control_ask = sum(self.ask_counter)
        self.control_bid = sum(self.bid_counter)

        prev_lags['price'][1][self.day] = self.price
        prev_lags['target'][1][self.day] = self.ma_target
        prev_lags['gohm price variation'][1][self.day] = self.price * (1 + self.reward_rate)        
        self.gohm_volatility = calc_gohm_volatility(prev_lags=prev_lags)

    def rebalance_treasury(self, params:ModelParams, prev_day=None):
        # Treasury Rebalance - Reserve Intake
        if self.day % 7 == 0:  # Rebalance once a week
            self.reserves_in = prev_day.liq_stables - prev_day.treasury_stables * params.max_liq_ratio
            if prev_day.target_liq_ratio_reached is False:
                max_outflow = (-1) * prev_day.reserves_stables * params.max_outflow_rate * 2 / 3  # Smaller max_outflow_rate until target is first reached
            else:
                max_outflow = (-1) * prev_day.reserves_stables * params.max_outflow_rate  # Ensure that the reserve release is limited by max_outflow_rate
            
            # max_outflow is really target. reserves_stables is updated in L320
            if self.reserves_in < max_outflow:
                self.reserves_in = max_outflow
            if self.reserves_in < (-1) * prev_day.reserves_stables:  # Ensure that the reserve release is limited by the total reserves left
                self.reserves_in = (-1) * prev_day.reserves_stables
        else:
            self.reserves_in = 0

    def update_rbs_parameters(self, params:ModelParams, prev_day=None, prev_lags=Dict[int, Tuple[int, Dict[int, float]]]):
        # Price Target
        self.ma_target = calc_price_target(params=params, prev_day=prev_day, prev_lags=prev_lags)
        self.lb_target = prev_day.floating_supply and prev_day.liq_backing / prev_day.floating_supply or 0
        self.target = max(self.ma_target, self.lb_target)
        self.prev_price = prev_day.price

        # Walls
        self.lower_target_wall = self.target * (1 - params.lower_wall)
        self.upper_target_wall = self.target * (1 + params.upper_wall)

        # Cushions
        self.lower_target_cushion = self.target * (1 - params.lower_cushion)
        self.upper_target_cushion = self.target * (1 + params.upper_cushion)

        # Reinstate Window --> Inside the range counters
        if prev_day.price > prev_day.target:
            self.bid_counter = prev_day.bid_counter[1:] + [1]
        else:
            self.bid_counter = prev_day.bid_counter[1:] + [0]

        if prev_day.price < prev_day.ma_target:
            self.ask_counter = prev_day.ask_counter[1:] + [1]
        else:
            self.ask_counter = prev_day.ask_counter[1:] + [0]

    def simulate_market_behavior(self, params:ModelParams, prev_day=None, historical_net_flows=None):
        if params.netflow_type == 'historical' or params.netflow_type == 'enforced' and historical_net_flows is not None:  # Arbitrary market behavior
            self.net_flow = historical_net_flows
            self.market_demand = 0
            self.market_supply = 0

        else:  # Random market behavior
            # Assumption: trading volume is proportional to treasury value - bigger treasury = bigger volume
            self.net_flow = random.uniform(prev_day.treasury_stables * prev_day.total_supply, prev_day.treasury_stables * prev_day.total_demand)

            if params.netflow_type == 'waves':
                self.market_demand = params.demand_factor * short_sin(self.day, params.short_cycle) * long_sin(self.day, params.long_cycle, params.long_sin_offset)
                self.market_supply = params.supply_factor * short_cos(self.day, params.short_cycle) * long_cos(self.day, params.long_cycle, params.long_cos_offset, params.supply_amplitude)
            else:
                # Assumption is that we make assumptions about levels of volatility using random.uniform
                self.market_demand = params.demand_factor * random.uniform(0.5, 3)
                self.market_supply = params.supply_factor * random.uniform(0.5, 3)

    # How it works: calculate natural_price w/o RBS interventions (following xy=k), then compare to cushions and do market operations if necessary
    def perform_rbs_operations(self, params:ModelParams, prev_day=None):
        # Target capacities
        self.bid_capacity_target = params.bid_factor * prev_day.reserves_stables
        self.ask_capacity_target = prev_day.upper_target_wall and params.ask_factor * prev_day.reserves_stables * (1 + 2 * params.upper_wall) / prev_day.upper_target_wall or 0
        self.bid_capacity_target_cushion = self.bid_capacity_target * params.cushion_factor
        self.ask_capacity_target_cushion = self.ask_capacity_target * params.cushion_factor

        
        natural_price = self.k and ((self.net_flow - self.reserves_in + prev_day.liq_stables) ** 2) / self.k or 0 # Price without any treasury market operations

        # BID: Real Bid Capacity - Cushion
        # Change this to be within a target. This follows assumption that there is no bond discount & cushions are efficient.
        if (sum(self.bid_counter) >= params.min_counter_reinstate or params.with_reinstate_window == 'No') and natural_price > self.lower_target_cushion:  # Refill capacity
            self.bid_capacity_cushion = self.bid_capacity_target_cushion
        elif natural_price < self.lower_target_cushion and natural_price >= self.lower_target_wall:  # Deploy cushion capcity
            self.bid_capacity_cushion = prev_day.bid_capacity_cushion + self.net_flow - self.reserves_in + prev_day.liq_stables - (self.k * self.lower_target_cushion) ** (1/2)
        else:
            self.bid_capacity_cushion = prev_day.bid_capacity_cushion
        
        if self.bid_capacity_cushion < 0:
            self.bid_capacity_cushion = 0
        elif self.bid_capacity_cushion > self.bid_capacity_target_cushion:
            self.bid_capacity_cushion = self.bid_capacity_target_cushion

        # BID: Effective Bid Capacity Changes - Cushion
        if natural_price <= self.lower_target_cushion and natural_price > self.lower_target_wall:
            self.bid_change_cushion_usd = prev_day.bid_capacity_cushion - self.bid_capacity_cushion
            self.bid_change_cushion_ohm = self.lower_target_cushion and (prev_day.bid_capacity_cushion - self.bid_capacity_cushion) / self.lower_target_cushion or 0
        else:
            self.bid_change_cushion_usd = 0
            self.bid_change_cushion_ohm = 0

        if self.bid_change_cushion_ohm > prev_day.bid_capacity_cushion:  # Ensure that change is smaller than capacity left
            self.bid_change_cushion_usd = prev_day.bid_capacity_cushion
            self.bid_change_cushion_ohm = self.lower_target_cushion and prev_day.bid_capacity_cushion / self.lower_target_cushion or 0

        # BID: Real Bid Capacity - Totals
        if self.target == self.lb_target and natural_price <= self.lb_target * (1 - params.lower_wall): # Below liquid backing, the wall has infinite capacity (unlimited treasury redemptions at those levels)
            self.bid_capacity = self.bid_capacity_target
        elif (sum(self.bid_counter) >= params.min_counter_reinstate or params.with_reinstate_window == 'No') and natural_price > self.lower_target_cushion:  # Refill capacity
            self.bid_capacity = self.bid_capacity_target
        elif natural_price < self.lower_target_wall:  # Deploy cushion capcity
            self.bid_capacity = prev_day.bid_capacity + self.net_flow - self.reserves_in + prev_day.liq_stables - (self.k * self.lower_target_wall) ** (1/2)
        else:
            self.bid_capacity = prev_day.bid_capacity - self.bid_change_cushion_usd
        
        
        if self.bid_capacity < 0:
            self.bid_capacity = 0
        elif self.bid_capacity > self.bid_capacity_target:
            self.bid_capacity = self.bid_capacity_target

        if self.bid_capacity_cushion > self.bid_capacity:
            self.bid_capacity_cushion = self.bid_capacity

        # BID: Effective Bid Capacity Changes - Totals
        if self.target == self.lb_target and natural_price <= self.lb_target * (1 - params.lower_wall): # Below liquid backing, the wall has infinite capacity (unlimited treasury redemptions at those levels)
            self.bid_change_usd = self.reserves_in - self.net_flow - prev_day.liq_stables + (self.k * self.lower_target_wall) ** (1/2)
            self.bid_change_ohm = self.lower_target_wall and self.bid_change_usd / self.lower_target_wall or 0
        elif natural_price >= self.lower_target_wall:  # If wall wasn't used, update with cushion
            self.bid_change_usd = self.bid_change_cushion_usd
            self.bid_change_ohm = self.bid_change_cushion_ohm
        else:
            self.bid_change_usd = prev_day.bid_capacity - self.bid_capacity
            self.bid_change_ohm = self.lower_target_wall and self.bid_change_cushion_ohm + (prev_day.bid_capacity - self.bid_capacity - self.bid_change_cushion_usd) / self.lower_target_wall or 0

        if self.bid_change_usd > prev_day.bid_capacity:  # Ensure that change is smaller than capacity left
            self.bid_change_usd = prev_day.bid_capacity
            self.bid_change_ohm = self.lower_target_wall and prev_day.bid_capacity / self.lower_target_wall or 0


        # ASK: Real Ask Capacity - Cushion
        if (sum(self.ask_counter) >= params.min_counter_reinstate or params.with_reinstate_window == 'No') and natural_price < self.upper_target_cushion:
            self.ask_capacity_cushion = self.ask_capacity_target_cushion
        elif natural_price > self.upper_target_cushion and natural_price <= self.upper_target_wall:
            self.ask_capacity_cushion = self.upper_target_cushion and prev_day.ask_capacity_cushion - (self.net_flow - self.reserves_in + prev_day.liq_stables) / self.upper_target_cushion + (self.k / self.upper_target_cushion) ** (1/2) or 0
        else:
            self.ask_capacity_cushion = prev_day.ask_capacity_cushion

        if self.ask_capacity_cushion < 0:
            self.ask_capacity_cushion = 0
        elif self.ask_capacity_cushion > self.ask_capacity_target_cushion:
            self.ask_capacity_cushion = self.ask_capacity_target_cushion

        # ASK: Effective Ask Capacity Changes - Cushion
        if natural_price > self.upper_target_cushion and natural_price <= self.upper_target_wall:
            self.ask_change_cushion_ohm = prev_day.ask_capacity_cushion - self.ask_capacity_cushion
            self.ask_change_cushion_usd = self.upper_target_cushion * (prev_day.ask_capacity_cushion - self.ask_capacity_cushion)
        else:
            self.ask_change_cushion_ohm = 0
            self.ask_change_cushion_usd = 0
        
        if self.ask_change_cushion_ohm > prev_day.ask_capacity_cushion:  # ensure that change is smaller than capacity left
            self.ask_change_cushion_ohm = prev_day.ask_capacity_cushion
            self.ask_change_cushion_usd = prev_day.ask_capacity_cushion * self.upper_target_cushion
                        
        # ASK: Real Ask Capacity - Totals
        if (sum(self.ask_counter) >= params.min_counter_reinstate or params.with_reinstate_window == 'No') and natural_price < self.upper_target_cushion:
            self.ask_capacity = self.ask_capacity_target
        elif natural_price > self.upper_target_wall:
            self.ask_capacity = self.upper_target_wall and prev_day.ask_capacity - (self.net_flow - self.reserves_in + prev_day.liq_stables) / self.upper_target_wall + (self.k / self.upper_target_wall) ** (1/2) or 0
        else:
            self.ask_capacity = prev_day.ask_capacity - self.ask_change_cushion_ohm # update capacity total to account for the cushion

        if self.ask_capacity < 0:
            self.ask_capacity = 0
        elif self.ask_capacity > self.ask_capacity_target:
            self.ask_capacity = self.ask_capacity_target

        if self.ask_capacity_cushion > self.ask_capacity:
            self.ask_capacity_cushion = self.ask_capacity

        # ASK: Effective Ask Capacity Changes - Totals
        if natural_price <= self.upper_target_wall: #if wall wasn't used, update with cushion
            self.ask_change_ohm = self.ask_change_cushion_ohm
            self.ask_change_usd = self.ask_change_cushion_usd
        else:
            self.ask_change_ohm = prev_day.ask_capacity - self.ask_capacity
            self.ask_change_usd = self.ask_change_cushion_usd + (prev_day.ask_capacity - self.ask_capacity - self.ask_change_cushion_ohm) * self.upper_target_wall
        
        if self.ask_change_ohm > prev_day.ask_capacity:  # ensure that change is smaller than capacity left
            self.ask_change_ohm = prev_day.ask_capacity
            self.ask_change_usd = prev_day.ask_capacity * self.upper_target_wall

    def update_treasury_metrics(self, params:ModelParams, prev_day=None):
        # Liquidity
        self.liq_stables = max(prev_day.liq_stables + self.net_flow - self.reserves_in + self.bid_change_usd - self.ask_change_usd, 0)
        self.liq_ohm = self.liq_stables and self.k / self.liq_stables or 0  # ensure that if liq_stables is 0 then liq_ohm is 0 as well
        self.price = self.liq_ohm and self.liq_stables / self.liq_ohm or 0  # ensure that if liq_ohm is 0 then price is 0 as well

        # Reserves
        self.reserves_out = self.liq_stables - prev_day.liq_stables - self.net_flow  # - self.reserves_in (error caught by blockscience)
        self.reserves_stables = max(prev_day.reserves_stables - self.reserves_out, 0)
        self.prev_reserves = prev_day.reserves_stables

        self.ohm_traded = (self.price + prev_day.price) and (-2) * self.reserves_out / (self.price + prev_day.price) or 0
        self.cum_ohm_purchased = prev_day.cum_ohm_purchased - self.ohm_traded
        self.cum_ohm_burnt = prev_day.cum_ohm_burnt + self.bid_change_ohm
        self.cum_ohm_minted = prev_day.cum_ohm_minted + self.ask_change_ohm
