# Live Sports Arbitrage Bet Finder - FanDuel, DraftKings, William Hill

## Summary

![Live sports arbitrage bet finder in action](https://github.com/ScrapeWithYuri/Live-Sports-Arbitrage-Bet-Finder/blob/main/Program_in_action.gif)

_**I've provided this code for informational purposes, and do not take responsibility for potential losses or gains. Bet at your own risk.**_

There are four Python programs in this repository.

- The program names start with F & D or F & W. F stands for FanDuel, D stands for DraftKings, and W stands for William Hill.
- Programs that end with "Two Person" are for two person or two team events that include only moneyline bets (such as tennis).
- Programs that do not end with this phrase are for sports that include over / under bets, moneyline and spread bets (such as baseball).
- The automated bot only looks for standard bet types.

The program will first scrape all live event names and odds based on the sport selected in the program. The live event names are matched against each sportsbook in order to compare live odds. Using a Nash equilibrium, the program will find if there are arbitrage betting opportunities. If an arbitrage is found, then the program will select that wager, enter the calculated wager amounts and place the bet.

**Please note** that most sportsbooks include a bet delay. After a bet is placed, the sportsbook will take several seconds to validate the bet. During this time, one sportsbook may accept your bet, while the other sportsbook may update its odds. During my tests, the average acceptance on both legs of the bet was ~70%. This is not high enough to maintain a profitable arbitrage betting strategy.

## Personalizing the programs

Update this section of the code if you want to bet on a different sport:

```
self.sport = 'Baseball'
```

Update these sections of the code if you want to change your bet amount, lower & upper arbitrage return limit and max odd limit:

```
self.main_bet_amount = 100  # Total amount to wager. The program will split the two bets, so that the total wager is this amount
self.lower_limit = 0.000  # Lower arbritage limit to bet on, as a percentage
self.upper_limit = 0.070  # Upper arbritage limit to bet on, as a percentage (0.070 = 7%)
self.bet_limit = 0.10  # Most websites require a minimum of $0.10 a wager on each bet
self.odds_limit = 750  # The upper odds limit that you want to wager on (i.e. +750)
```

Submitting a wager has been commented out in the programs. You can submit a wager but uncommenting this section of code:

```
self.pool.apply_async(self.process, args=(9, 0, 0, 0,))
self.pool.apply_async(self.process, args=(10, 0, 0, 0,))
# Join the pools so they run in parallel
self.pool.join()
```
