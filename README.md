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
  
- To initially verify the model and to give users more flexibility, a fully customizable jupyter notebook to run single simulations has been created.

- Since the policy team aims to come up with a robust parameter configuration, no agent-modeling behavior assumptions have been done. Instead, a Montecarlo (random market behavior) approach has been followed. Theoretically, this design choice ensures that a wider variety of market conditions (including edge cases and "not realistic" market behaviors) have been tested.

- The simulated data has been stored in BigQuery tables and analyzed using Tableau. Since it is unfeasible to analyze all the seeds independently, they have been grouped into market scenarios (`a-really-bullish`, `b-bullish`, `c-neutral-bullish`, `d-neutral-bearish`, `e-bearish`, `e-really-bearish`)

# scripts
- `liquidity-olympus/src/utils.py`: Contains all the equations that govern the RBS model. Also contains relevant functions such as the reward rate framework.
- `liquidity-olympus/src/price.txt`: Contains the name of the BQ tables to be created and the initial protocol variables' values.
- `liquidity-olympus/src/init_functions.py`: Reads and loads the values from `price.txt`.
- `liquidity-olympus/simulation_random_XXX.py`: Scripts where the configuration of a simulation batch is set up. Determines the seeds and the parameter configuration for each trial within that seed. Write this configuration in a BQ table.
- `liquidity-olympus/simulation_variables_XXX.py`: Scripts that write the daily variable values in another BQ table. Use the trial configurations determined in `simulation_random_XXX.py`.
- `model_sim.js`: Paralellizes the execution of the `simulation_random_XXX.py` scripts.
- `model_daily.js`: Paralellizes the execution of the `simulation_variables_XXX.py` scripts.

---
# old readme

jupyter notebook aims to provide a playground to simulate different scenarios for the so-called "Forward Guidance", a model ideated by Zeus.

The notebook is created in such a way that different price controllers can be tested. The only requirement is to create new price controlling functions to calculate the `price_target` using different methods.

## how to use jupyter notebooks?
Jupyter notebooks allow users to run portions of the code (cells) asynchronously. This feature is really handy to perform data analysis and simulations.

Because of that, the cells that contain the model equations only need to be run once. After that, new simulations with different scenarios can be performed without having to run all the code all over again.

## how to set up new scenarios?
Scenarios are defined by objects that belong to the class `ModelParams`.

To define a scenario, the values used to construct the `params` object (under the section **set scenario parameters**) must be defined. This object has the following attributes:

 - `horizon`: determines the time horizon of the simulation (in days).
 - `max_liq_ratio`: establishes the `liq_usd / reserves` ratio that the treasury will try to maintain to have a balanced treasury.
 - `max_liq_fmcap_ratio`:  establishes the `liq_usd / floating_mcap` ratio that the treasury will try to maintain to match liquidity with supply growth.
 - `cycle_reweights`: determines the amount of reweights that the treasury will perform in a `short_cycle`.
 - `release_caputre`: 
 - `target_price_function`: determines the function used by the price controller.
 ---
 - `arb_factor`: sets the initial arbitrage factor.
 - `demand_factor`: sets a demand factor that will directly impact assumptions for market demand for OHM. Can be seen as a parameter that reflects constant buy pressure regardless of general market sentiment.
 - `supply_factor`: sets a supply factor that will directly impact assumptions for market demand for OHM. Can be seen as a parameter that reflects constant sell pressure regardless of general market sentiment.
 - `short_cycle`: expected duration of short market cycles. It can be seen as "protocol cycles" (OHM has historically had a quite cyclical behavior).
 - `long_cycle`: expected duration of long market cycles. It can be seen as "broader crypto market cycles" (these cycles have historically been highly correlated with bitcoin's halving).
 - `long_sin_offset`: helps model market demand in combination with the `long_cycle` value.
 - `long_cos_offset`: helps model market supply in combination with the `long_cycle` value.
 ---
 - `initial_supply`: initial protocol supply.
 - `initial_reserves`: initial protocol reserves.
 - `initial_liq_usd`: initial usd liquidity (excluding OHM).
 - `initial_price`: initial OHM price.
 - `initial_target`: initial target price.

## how to plot the results?
After configuring the scenario parameters and running the simulation, the results can be already plotted.

Before plotting any charts, it is important to build a dataframe containing all the results. The first cell under **plot results** must be run to do so.

After the dataframe is created, it is only necessary to run those cells that contain the desired information.
