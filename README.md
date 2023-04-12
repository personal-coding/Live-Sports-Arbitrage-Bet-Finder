# Live Sports Arbitrage Bet Finder

## Summary

![Live sports arbitrage bet finder in action](https://github.com/ScrapeWithYuri/Live-Sports-Arbitrage-Bet-Finder/blob/main/Program_in_action.gif)

_**This code is provided for informational purposes, and I do not take responsibility for potential losses or gains. Bet at your own risk.**_


## Introduction

This Python program that scrapes live data off betting websites every 10 milliseconds to find arbitrage opportunities, calculates the exact wagering amounts needed, and places bets. With three different programs for FanDuel, DraftKings, and William Hill, and two-person or multi-person events, this program can handle a wide variety of sports events.

The program uses multithreading to find arbitrage opportunities as quickly as possible and employs the [undetected-chromedriver](https://pypi.org/project/undetected-chromedriver/) package to help avoid bot detection. Keep in mind that most sportsbooks include a bet delay and that there may be a delay between placing your bets at different sportsbooks.

You can also personalize the program by changing the sport, adjusting the bet amount, and modifying the arbitrage return and odds limits. See additional information below.

## Troubleshooting Error

If you run into an error that states `AttributeError: 'ArbFinder' object has no attribute 'driver'` go to `chrome://settings/help` in your URL bar. There may be a relaunch option where your Chrome version is. Otherwise, try to upgrade your Chrome version. Your Chrome version may be different from the ChromeDriver version downloaded by the program.

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
