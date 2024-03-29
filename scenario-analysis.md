# Exploring how RBS impacts the future of Olympus: A Simulation-Based Analysis
*Read the [published article](https://hackmd.io/poMqzoWzRVyAhn49ilrsCg) on hackmd.io*

After the public launch of the Range Bound Stability (RBS) system, I thought I would share a complementary document to the [simulations report](https://olympusdao.notion.site/RBS-Report-fd88cb37208d4b0f9abaca4e276f9ddd). The aim of such document is to showcase some interesting scenarios (based on randomly simulated market behavior) so that people can better understand its mechanics.

Nevertheless, I had to postpone its public release to re-run the simulations with the [changes implemented in OIP-125](https://forum.olympusdao.finance/d/1676-oip-125-rbs-parameter-changes). Now, a couple of weeks after the implementation of the system enhancements in production, it is time to publicly share the data.

### Disclaimer

*The conclusions reached in this report reflect my own understanding of the simulation results. My opinions shouldn't be taken as endorsement or financial advice.*

*The presented results are based on simulated data and shouldn't be taken as certain. Reality will depend on market conditions that might not have been considered.*

*The created model aims to be representative of reality, but some simplifications have been assumed for the sake of efficiency and mass simulation.*

*I decided to showcase 6 completely different scenarios to cover the spectrum of possibilities. Some of the scenarios are extremely unlikely to happen, but still useful understand the system mechanics.*

### Notes on the presented data
*If you are not familiar with the RBS system yet, make sure to check the [official docs](https://docs.olympusdao.finance/main/overview/range-bound) first*.

*The simulations showcased in this document are some of the ones used in the [simulations report](https://olympusdao.notion.site/RBS-Report-fd88cb37208d4b0f9abaca4e276f9ddd). Because of that, the same design principles, assumptions, and simplifications described in the report should be taken into account when reading this document.*

*On top of everything described in the report, the new model also accounts for Liquid Backing. Since Liquid Backing partly relies on volatile reserves, some simplifications have been implemented to deal with such assets:*
- *The value of volatile assets is assumed to remain constant (in USD terms) during the whole simulation timespan.*.
- *The value of volatile assets has been undermined to ensure a robust design that accounts for potential asset depreciation.*

*Another consideration worth having into account is that, since the RBS simulations were intended with robustness in mind (to stress-test the system), **the assumed volumes and volatility in the simulations are considerably higher than the ones we are currently seeing** in this apathetic market.*

*Remember that [the source code is public](https://github.com/0xRusowsky/liquidity-olympus) and you can run your own simulations!*

## A. Neutral market behavior
Most of the time, simulations with neutral market behavior are usually produced by a combination of:
- Lack of clear market directionality during sustained periods of time.
- Lower volatility (despite not always being the case, neutral scenarios often showcased lower volatility values).

### A.1. Neutral-bearish scenario with final recovery
#### Market Netflows
- In this seed, we can see a brief initial uptrend of $12M cumulative net flows in the first month.
- After that, there is a shift in market sentiment and a continuous sell-off of $38M over a time span of 200 days.
- Then, the market recovers $30M in just 80 days, only to have a final pullback of $20M in 30 days.
- The overall balance for the year is a negative net flow of $10M.
![](https://i.imgur.com/QTlrkfG.png)
![](https://i.imgur.com/Jn9wV61.png)

#### Price Action
- During 190 days (52% of the year), the 30-day MA is lower than the liquid backing price.
- We can see that when cushions and walls are set relative to LB, the system presents noticeable stability thanks to its ability to absorb unlimited sell pressure.
- Finally, we can also see a really interesting property of RBS when using LB as the price target. By suppressing the price downside, the system is able to see price appreciation despite seeing a cumulative negative net flow.
![](https://i.imgur.com/CbPzSgO.png)
![](https://i.imgur.com/YWOBtQa.png)
![](https://i.imgur.com/frAZrRk.png)

#### Supply
- As the system generally buys back tokens and burns them, the supply decreases.
![](https://i.imgur.com/vGfDUt0.png)

#### Comparison
- It is clear that when performing market operations, the system consumes a lot of reserves to sustain price close to its liquid backing.
- In the scenario without any market operations (other than treasury rebalances), the price and market cap trade at multiples above and below the liquid backing, and suffer quite large swings. - The RBS system, on the other hand, is able to minimize drawdowns from its liquid backing, providing protection by guaranteeing a minimum price and reducing overall volatility.
![](https://i.imgur.com/AicITnZ.png)
![](https://i.imgur.com/aTkAFBP.png)
![](https://i.imgur.com/OxTbgG3.png)


### A.2. Neutral scenario with initial bullish impulse
- In this seed, we can see a brief initial uptrend of $24M cumulative netflows over 105 days.
- After that, there is a flip in market sentiment and a sharp sell-off, resulting in $37M leaving the system in just 80 days.
- The market then recovers $15M over the next 20 days, followed by a period of lower volatility for 120 days.
- Finally, there is a final pullback of $21M in the last 30 days of the year.
- The overall balance for the year is a net outflow of $10M.
![](https://i.imgur.com/NQmuvGO.png)
![](https://i.imgur.com/TCiJjPf.png)

#### Price Action
- During 109 days (30% of the year), the 30-day MA is lower than the liquid backing price.
- We can see that when cushions and walls are set relative to the liquid backing, the system presents noticeable stability thanks to its ability to absorb unlimited sell pressure.
- As has happened in the production system during its first weeks, price can go to irrational levels when there isn't a hard stop for the LB. Nevertheless, as soon as the market is able to swap with the treasury at infinite capacity, it quickly arbitrages the difference.
- Finally, we can again see that when using LB as the price target, the downside is suppressed, and any bullish impulse directly translates into price appreciation, bringing the MA above LB.
![](https://i.imgur.com/LI9ZhhE.png)
![](https://i.imgur.com/WpV1h0q.png)
![](https://i.imgur.com/vEiiWbF.png)

#### Supply
- The dynamic is clear. When the system is minting new OHM in exchange for reserves (upper wall/cushion), supply expands quickly. When the system is buying back and burning OHM, supply decreases.
![](https://i.imgur.com/zVCzrGY.png)

#### Comparison
- In this case, despite the RBS system consuming slightly more reserves, the overall treasuries in both scenarios are quite similar.
- In the scenario without any market operations (other than treasury rebalances), price and market cap experience large swings above and below LB.
- The RBS system is able to minimize drawdowns from its liquid backing, providing protection by guaranteeing a minimum price and reducing overall volatility.
![](https://i.imgur.com/PgSNYRl.png)
![](https://i.imgur.com/xUWer52.png)
![](https://i.imgur.com/W1OU2Yp.png)




## B. Directional market behavior
Simulations with a directional market behavior are usually the result of:
- A consensus on market directionality over long periods of time.
- Lower volatility, as directional scenarios often exhibit similar volatility to neutral scenarios.

### B.1. Bearish scenario with final semi-recovery
- In this seed, we can see a continuous downtrend with several failed redemption attempts during the first half of the year. After 230 days, the cumulative outflows reach $40M.
- After that, there is a stronger recovery attempt, which translates to a positive net flow of $25M in only 50 days.
- Finally, the market starts ranging until the end of the simulation lifespan.
- The overall balance for the year is a cumulative outflow of $30M.
![](https://i.imgur.com/G4MVGsw.png)
![](https://i.imgur.com/DXMhrIB.png)

#### Price Action
- Despite facing continuous selling pressure, the 30-day MA only trades below LB during 176 days (48% of the year).
- The system is able to deal with market volatility quite decently. The ask capacity is depleted twice, and the bid capacity only once. Nevertheless, it is important to keep in mind that this behavior is possible thanks to the fact that bid capacity is unlimited when the MA trades below the LB.
- Thanks to the relentless treasury bid, we can see how, despite the continuous outflows, the system is able to reprice and see growth with every small run-up.
![](https://i.imgur.com/J1pGBY8.png)
![](https://i.imgur.com/F6Ij8Qg.png)
![](https://i.imgur.com/PdN7fXI.png)

#### Supply
In this case, the supply of OHM continuously decreases due to the treasury buying back and burning it.
![](https://i.imgur.com/xqhW37R.png)

#### Comparison
- It is clear that when performing market operations, the system consumes a lot of reserves in order to sustain a price close to its liquid backing.
- In a scenario without any market operations (other than treasury rebalances), the price and market cap would collapse and trade at a multiple below the liquid backing. The treasury would be protected quite well, but the protocol would be unable to capitalize on its large reserve.
- The RBS system, on the other hand, is able to minimize drawdowns from its liquid backing by providing protection through a guaranteed minimum price and reducing overall volatility.
- Finally, we can see how the RBS system is able to grow above its backing whenever there is a market rally.
![](https://i.imgur.com/Cw9f89n.png)
![](https://i.imgur.com/VHu1uxT.png)
![](https://i.imgur.com/zTcgSjV.png)



### B.2. Bullish scenario with sudden sell-off
- In this seed, we can see a continuous uptrend without major pullbacks during the first half of the year. After 170 days, the cumulative net flows reach $52M.
- After that, there is a sharp downturn in market sentiment and a massive sell-off that results in a net cumulative outflow of $47M in only 50 days.
- Finally, the market recovers and starts another leg up with a net flow of $27M during the last 120 days of the year.
- The overall balance of the year is a positive net flow of $25M.
![](https://i.imgur.com/iARi8or.png)
![](https://i.imgur.com/YzTnl9O.png)


#### Price Action
- Thanks to the conitnuous buy pressure, we see that the 30 day MA is usually above liquid backing. In fact LB is only 32 days (9% of the year) below the MA.
- The continuous buy pressure ends up outweighting the system capacity, and the upper walls break in 2 occasions. In fact, they are depleated for a total of 150 days (41% of the year).
- The sudden pull-back drains all the bid capacity in a matter of days. Price breaks the lower wall and crashes below LB. The system runs out of bid capacity for only 33 days (9% of the year).
![](https://i.imgur.com/IDH9ysp.png)
![](https://i.imgur.com/Z1yLATX.png)
![](https://i.imgur.com/6DeVp8f.png)


#### Supply
- Again, when there is high demand for OHM, the treasury ask is filled and supply is expands quickly. When the system is high supply for stables, the treasury bid is filled, burning OHM and reducing supply.
![](https://i.imgur.com/0cZIzna.png)

#### Comparison
- In this case, the RBS system is able to capitalize on market inflows by selling OHM on the ask side of the range. This dynamic ends up in bigger reserves in the scenario with market operations.
- The scenario without any market operations (other than treasury rebalances) is extremely volitile in price terms. Despite OHM almost always trades above LB, there are huge price swings.
- The RBS system, instead, is able to absorb a noticeable portion of volatility. Despite price trades occasionaly below LB, the system is able to recover and never stops working as it is expected.
![](https://i.imgur.com/XO7xbl0.png)
![](https://i.imgur.com/dzG3xyi.png)
![](https://i.imgur.com/tXq5bqQ.png)




## C. Extreme market behavior
Simulations with extremely directional market behavior are the outcome of:
- Sustained market directionality consensus during long periods of time.
- High volatility.

### C.1. Bearish scenario with continuous sell pressure
![](https://i.imgur.com/MjvC36D.png)
![](https://i.imgur.com/wV41Z2B.png)

#### Price Action
- Similar to other bearish scenarios. Since the system is able to absorb unlimited sell pressure below LB, it is able effectively protect price regardless of the how volatile the market is.
- Again, any small recovery period translates into price appreciation above LB. During these periods the treasury runs out of bid capacity and price comes back to its "hard floor".
![](https://i.imgur.com/qUk0H1V.png)
![](https://i.imgur.com/jZA9g9i.png)
![](https://i.imgur.com/xX9VWf8.png)

#### Supply
- As the system is generally buying back tokens and burning them, supply decreases.
![](https://i.imgur.com/DQSv9mm.png)

#### Comparison
- In the RBS scenario we can see how the treasury protects price at the expense of reserves.
- The scenario without market operations spends a similar amount of reserves trying to rebalance and adding liquidity into the pools.
- We can conclude that, at such levels, it is much more effective for the treasury to spend its funds in direct market operations (protecting price), rather than providing exit liquidity via the liquidity pools.
![](https://i.imgur.com/sORZ0RR.png)
![](https://i.imgur.com/biU9g7c.png)
![](https://i.imgur.com/Zzn3F8j.png)


### C.2. Bullish run without major pullbacks
- This seed starts with $27M exiting the system during the first 80 days.
- After that, there is a sudden shift in market sentiment which initiates a bullish up-trend that will last until the very end of the year and inject a net total of $76M.
- The overall balance of the year is a positive net flow of $49M.
![](https://i.imgur.com/7nY6FQp.png)
![](https://i.imgur.com/uJPPQ2L.png)

#### Price Action
- The system is only able to handle low-volatility situations (at the very beginning and the very end of the year).
- When the market is trending, the system runs out of capacity quite fast, and OHM ends-up trading without any upper bound during 165 days (45% of the year).
- Since the system runs out of ask capacity but still has bid capacity, it showcases a weird dynamic where it protects price but lets it go up freely.
- By the end of the year, price has done a 50x. Nevertheless, the treasury has been unable to capitalize a big part of the buy pressure because it ran out of capacity. 
![](https://i.imgur.com/URSrYy8.png)
![](https://i.imgur.com/4mFhYxM.png)
![](https://i.imgur.com/SXD1EOh.png)

#### Supply
- Despite price is going up sharply, the treasury is unable to mint new OHM once it runs out of capacity.
![](https://i.imgur.com/i0HEKxr.png)


#### Comparison
- While both scenarios see similar behavior in terms of treasury reserves, we see a really interesting dynamic in price/marketcap terms.
- Unlike with RBS, the scenario without market operations is unable to protect its price in the initial leg down, and its price ends up trading way below LB.
- After that, both systems reprice to the upside, but the one without market operations needs to first recover all the depreciation it initially suffered.
![](https://i.imgur.com/tLqWOig.png)
![](https://i.imgur.com/P6gbPcH.png)
![](https://i.imgur.com/XEBnMDQ.png)



# Personal Takeaways

### System Benefits
The implementation of the Range Bound Stability system has brought several improvements for Olympus.

One of the most notable benefits is the stabilizing effect that RBS has on price. In comparison to scenarios where no market operations are in place, RBS has consistently shown an stabilizing influence.

With the implementation of OIP-125, liquid backing serves as a strong foundation for the price of OHM, since it creates a hard floor that helps protect the asset against steep drops in value. This dynamic further reduces price volatility in extremely adverse market conditions.

Finally, the algorithmic framework also offers predictability for users, who can take advantage of market inefficiencies through arbitrage opportunities. By understanding the behavior of the system, investors can make informed decisions about when and how to buy or sell OHM.

### Areas of improvement
As with any nascent system that is still developing, the implementation of RBS comes with some limitations and areas of improvement. *Remember that the goal is to automate and iterate.*

Unlike in the past, when the system continuously issued bonds, it currently has limited capacity for market operations and is unable to capitalize on all the demand. Despite this mechanic helps control OHM issuance, it also leaves money on the table that could otherwise end in the protocol's treasury.

By narrowing the spreads (as per OIP-125), the community implemented a more restrictive strategy with increased treasury intervention. Despite this is beneficial at current prices and the low-volatility conditions we are experiencing, it will make the system less able to handle volatile events in the future. So, we can conclude that the system is unable to dynamically adapt to market volatility and implements arbitrary moving average and spreads (despite they can be manually adjusted by the community via OIP, it is not a scalable approach).

To address these improvement areas, there are several opportunities worth considering. With the most appealing ones (to me) being:
- The implementation of Bollinger Bands to dynamically adjust the spreads based on recent market volatility.
- The implementation of layered TWAMMs, which would stack on top of each other the further the price deviates from its target.

These measures would help improve the system performance when considering the listed weak points.

### Closing Thoughts

By implementing the RBS system, Olympus has enhanced its currency-related features and taken a significant step towards becoming a truly algorithmic free-floating currency.

After thoroughly analyzing the outputs of numerous seeds, I have drawn the following key conclusions about the behavior of OHM:

First and foremost, it is important to note that OHM's properties fluctuate over time depending on market conditions. This means that its value and usefulness as a financial instrument can vary significantly depending on the state of the market at a given time.

Another key takeaway from this research is that the smaller the premium on OHM, the more stable it becomes. When the premium is inexistent at all, OHM has limited downside and great store of value properties, making it a particularly good collateral for borrowing against. Additionally, the fact that it can reprice to the upside further enhances its usefulness as collateral.

On the other hand, when the premium is larger, it is generally better to borrow OHM, since the chances of its value going down increase, making repayment cheaper (similar to the concept of shorting).

Overall, Olympus appears to be heading towards an interesting direction where it may start to resemble a currency more than just a tech-growth stock. With the implementation of the new mechanics and the added stability it has achieved, OHM has the potential to enter lending markets and maximize growth through supply expansion rather than just price appreciation. This is exemplified by its recent integrations with platforms such as Silo and Fraxlend.

![](https://i.imgur.com/p8f33CK.jpg)
*Just like water, OHM adapts to its environment. It offers different properties according to the market conditions. When trading at (or below) its liquid backing, it becomes a stable and solid asset, similar to ice. In this state, it offers limited downside and a decreasing supply. As premium increases, its properties evolve and it becomes a more volatile asset, like liquid water. Finally, in times of market exuberance, it can even reach its most volatile state, resembling steam.*


In conclusion, the research on the Range Bound Stability system highlights really interesting dynamics and useful properties as a currency and a financial instrument. Its ability to adapt to market conditions, to further stabilize, and to enter lending markets will be key for its future success.
