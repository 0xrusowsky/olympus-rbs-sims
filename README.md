# range-bound-stability
This repo contains all the code behind the modeling tools used to simulate the so-called "Range Bounds Stability" (RBS), a model ideated by Zeus.

**Disclaimers:**
- _The model aims to be representative of reality, but some simplifications have been assumed._
- _Since the idea has been evolving and maturing with time, this implementation may contain some outdated functions that are not used anymore. Over time, I will try to get rid of these deprecated items._



# design principles

- The main goal of this initiative is to understand how the different parameters of the RBS model impact protocol variables such as price, marketcap, liquidity, reserves, and volatility. This goal will be achieved by performing millions of simulations with different parameter configurations and market conditions.

- After the completion of this goal the policy team should be able to propose a parameter configuration to perform further simulations/tests using the testnet smartcontract implementation of the RBS.

- Since the model is governed by a lot of different parameters and it is unfeasible to analyze and understand the impact of all of them at once, the study approach has been to:
  1. Analyze the parameters that are believed to be more influential and fix the rest of the parameters.
  2. Reach conclusions on the best performing values for the tested parameters.
  3. Perform another round of simulations, by fixing the parameters for which some good-performing values have been found, and analyze the rest of the parameters.

- Since the policy team aims to come up with a robust parameter configuration, no agent-modeling behavior assumptions have been done. Instead, a Montecarlo (random market behavior) approach has been followed. Theoretically, this design choice ensures that a wider variety of market conditions (including edge cases and "not realistic" market behaviors) have been tested.

- The simulated data has been stored in BigQuery tables and analyzed using Tableau.
  
- To initially verify the model implementation and to give users more flexibility, a fully customizable jupyter notebook to run single simulations has been created.

- To verify the accuracy of the model implementation vs the testnet implementation of smart contracts, a second jupyter notebook has been created.



# scripts

- `liquidity-olympus/src/utils.py`: Contains all the equations that govern the RBS model. Also contains auxiliar functions such as the reward rate framework.
- `liquidity-olympus/src/price.txt`: Contains the name of the BQ tables to be created and the values for the initial protocol variables.
- `liquidity-olympus/src/init_functions.py`: Reads and loads the values from `price.txt`.
- `liquidity-olympus/simulation_random_XX.py`: Scripts with the configuration of a simulation batch is set up. Determine the seeds and the parameter configuration for each trial within that seed. Write this configuration in a BQ table.
- `liquidity-olympus/simulation_variables_XX.py`: Scripts that write the daily variable values in another BQ table. Use the trial configurations determined in `simulation_random_XX.py`.
- `model_sim.js`: Paralellizes the execution of the `simulation_random_XX.py` scripts.
- `model_daily.js`: Paralellizes the execution of the `simulation_variables_XX.py` scripts.
- `simulation.ipynb`: Notebook designed for exploration of the RBS system by playing with different system parameters and netflow seeds.
- `python-vs-testnet.ipynb`: Notebook designed to ensure that the python model and the bot used to interact with the contracts deployed on testnet are aligned.
- `testnet-vs-testnet.ipynb`: Notebook designed to finetune the testnet bot implementation.



# simulation.ipynb
## how to set up new scenarios?
Scenarios are defined by objects that belong to the class `ModelParams`.

To define a scenario, the values used to construct the `params` object (under the section **set scenario parameters**) must be defined. This object has the following attributes:

### Simulation framework
 - `horizon`: Determines the time horizon of the simulation (in days)
 - `netflow_type`: Determines the netflow types. Either 'historical', 'enforced', 'random', or 'cycles' (sin/cos waves)
 - `demand_factor`: % of OHM supply expected to drive market demand
 - `supply_factor`: % of OHM supply expected to drive market sell preasure
 - `arb_factor`: Initial arb factor
 - `release_capture`: % of reweight taken immediately by the market (Deprecated)
 - `short_cycle`: Short market cycle duration (only relevant for netflow_type == cycles)
 - `cycle_reweights`: Reweights per short market cycle (Deprecated)
 - `long_cycle`: Long market cycle duration (only relevant for netflow_type == cycles)
 - `long_sin_offset`: Demand function offset (only relevant for netflow_type == cycles)
 - `long_cos_offset`: Supply function offset (only relevant for netflow_type == cycles)
 - `supply_amplitude`: Supply function amplitude (only relevant for netflow_type == cycles)

### Initial Protocol Variables
 - `initial_supply`: Initial protocol supply
 - `initial_reserves`: Initial protocol reserves
 - `initial_liq_usd`: Initial usd liquidity (excluding OHM)
 - `initial_price`: Initial OHM price
 - `initial_target`: Initial price target

### System configuration
 - `max_liq_ratio`: LiquidityUSD : reservesUSD ratio, calculated as `LiquidityUSD / Treasury`
 - `min_premium_target`: Minimum premium for mint&sync --> to keep adding liquidity as supply grows 
 - `max_outflow_rate`: Max % of reservesUSD that can be released on a single day
 - `reserve_change_speed`: Directly related to the speed at which reserves are released/captured by the treasury. The higher the slower
 - `ask_factor`: % of floating supply that the treasury can deploy when price is trading above the upper target
 - `bid_factor`: % of the reserves that the treasury can deploy when price is trading below the lower target
 - `cushion_factor`: The percentage of a bid or ask to offer as a cushion
 - `target_price_function`: determines the function used by the price controller. Despite different price controllers were tested, the model will use a simple moving average `price_moving_avg`.
 - `target_ma`: Length of the price target moving average (in days)
 - `lower_wall`: Determines lower wall price target at x% below the target price
 - `upper_wall`: Determines upper wall price target at x% above the target price
 - `lower_cushion`: Determines lower cushion price target at x% below the target price
 - `upper_cushion`: Determines upper cushion price target at x% above the target price
 - `reinstate_window`: The window of time (in days) to reinstate a bid or ask
 - `min_counter_reinstate`: Number of days within the reinstate window that conditions are true to reinstate a bid or ask
 - `with_reinstate_window`: Wheather the reinstate is necessary to refill capacity or not
 - `with_dynamic_reward_rate`: Wheather the default reward rate framework is used (`No`) or not (`Yes` --> custom emissions controller)

## how to plot the results?
After configuring the scenario parameters and running the simulation, the results can be already plotted.

Before plotting any charts, it is important to build a dataframe containing all the results. The first cell under **plot results** must be run to do so.

After the dataframe is created, it is only necessary to run those cells that contain the desired information.