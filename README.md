# forward-guidance
This jupyter notebook aims to provide a playground to simulate different scenarios for the so-called "Forward Guidance", a model ideated by Zeus.

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
 -
 - `arb_factor`: sets the initial arbitrage factor.
 - `demand_factor`: sets a demand factor that will directly impact assumptions for market demand for OHM. Can be seen as a parameter that reflects constant buy pressure regardless of general market sentiment.
 - `supply_factor`: sets a supply factor that will directly impact assumptions for market demand for OHM. Can be seen as a parameter that reflects constant sell pressure regardless of general market sentiment.
 - `short_cycle`: expected duration of short market cycles. It can be seen as "protocol cycles" (OHM has historically had a quite cyclical behavior).
 - `long_cycle`: expected duration of long market cycles. It can be seen as "broader crypto market cycles" (these cycles have historically been highly correlated with bitcoin's halving).
 - `long_sin_offset`: helps model market demand in combination with the `long_cycle` value.
 - `long_cos_offset`: helps model market supply in combination with the `long_cycle` value.
 - 
 - `initial_supply`: initial protocol supply.
 - `initial_reserves`: initial protocol reserves.
 - `initial_liq_usd`: initial usd liquidity (excluding OHM).
 - `initial_price`: initial OHM price.
 - `initial_target`: initial target price.

## how to plot the results?
After configuring the scenario parameters and running the simulation, the results can be already plotted.

Before plotting any charts, it is important to build a dataframe containing all the results. The first cell under **plot results** must be run to do so.

After the dataframe is created, it is only necessary to run those cells that contain the desired information.
