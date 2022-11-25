# Live Sports Arbitrage Bet Finder - FanDuel, DraftKings, William Hill

## Summary

![Live sports arbitrage bet finder in action](https://github.com/ScrapeWithYuri/Live-Sports-Arbitrage-Bet-Finder/blob/main/Program_in_action.gif)

_**I've provided this code for informational purposes, and do not take responsibility for potential losses or gains. Bet at your own risk.**_

This program will find arbitrage betting opportunities during live sports events. The program will scrape live data off betting websites every 10 milliseconds, find if an arbitrage exists, calculate the exact wagering amounts needed, and place bets.

There are four Python programs in this repository.

- The program names start with F & D or F & W. F stands for FanDuel, D stands for DraftKings, and W stands for William Hill.
- Programs that end with "Two Person" are for two person or two team events that include only moneyline bets (such as tennis).
- Programs that do not end with this phrase are for sports that include over / under bets, moneyline and spread bets (such as baseball).
- The automated bot only looks for standard bet types.

The program will first scrape all live event names and odds based on the sport selected in the program. The live event names are matched against each sportsbook in order to compare live odds. Using a Nash equilibrium, the program will find if there are arbitrage betting opportunities. If an arbitrage is found, then the program will select that wager, enter the calculated wager amounts and place the bet.

The programs use multithreading to make them as fast as possible to find arbitrage opportunities. Also, the programs use the [undetected-chromedriver-modified](https://pypi.org/project/undetected-chromedriver-modified/) package to help avoid bot detection.

**Please note** that most sportsbooks include a bet delay. After a bet is placed, the sportsbook will take several seconds to validate the bet. During this time, one sportsbook may accept your bet, while the other sportsbook may update its odds.

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
self.odds_limit = 750  # The program will not wager above these odds (i.e. +750)
```

Most references state that wagers should be rounded to the dollar to help avoid arbitrage detection. Update the round function below to zero decimal places if you need:

```
self.result = [round(x, 2) for x in self.result]
```

Submitting a wager has been commented out in the programs. You can submit a wager by uncommenting this section of code:

```
self.pool.apply_async(self.process, args=(9, 0, 0, 0,))
self.pool.apply_async(self.process, args=(10, 0, 0, 0,))
# Join the pools so they run in parallel
self.pool.join()
```

## Additional information about the programs

The programs use the naming convention "bid" and "ask." I built the programs from a framework that traded binary options and did not update the naming convention. "Bid" means DraftKings or William Hill, while "ask" means FanDuel.
