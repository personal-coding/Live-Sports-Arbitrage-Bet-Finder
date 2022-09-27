from gevent.pool import Pool
from gevent import monkey

monkey.patch_all()

import time, logging, sys, linecache, random
import undetected_chromedriver.v2 as uc
from tkinter import *
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import nashpy as nash
import numpy as np

logging.disable(logging.CRITICAL)

class ArbFinder(object):
    """docstring for ClassName"""

    def __init__(self, URL):
        try:
            # Setup ChromeDriver
            self.URL = URL
            self.driver = uc.Chrome()
            # elf.driver.set_window_size(1400, 5000)
            self.driver.implicitly_wait(5)
            self.driver.get(URL)
        except:
            pass
        self.sport = 'Baseball'

    def set_type(self, ASK=0, BID=1):
        # time.sleep(1)
        # Logging in

        try:
            if (ASK):
                # Change to ask view since the default is the bid view
                self.type = "ASK"
                self.driver.find_element(By.XPATH, "//a[contains(@href,'/live') and @title='" + self.sport + "']").click()

            elif (BID):
                # Nothing to update since the default is the bid view
                self.type = "BID"
                self.driver.find_element(By.XPATH, "//a[@role='tab']/span[text()='" + self.sport + "']").click()
        except Exception as e:
            print(e)

class App(object):
    def __init__(self):
        global URL
        self.old_list = ''
        self.num_worker_threads = 2
        self.pool = Pool(self.num_worker_threads)

        self.main_bet_amount = 100  # Total amount to wager. The program will split the two bets, so that the total wager is this amount
        self.lower_limit = 0.000  # Lower arbritage limit to bet on, as a percentage
        self.upper_limit = 0.070  # Upper arbritage limit to bet on, as a percentage (0.070 = 7%)
        self.bet_limit = 0.10  # Most websites require a minimum of $0.10 a wager on each bet
        self.odds_limit = 750  # The upper odds limit that you want to wager on (i.e. +750)

        self.ask = ArbFinder('https://il.sportsbook.fanduel.com/live')
        self.ask.driver.implicitly_wait(5)
        self.ask.set_type(ASK=1, BID=0)
        self.running = False

        self.bid = ArbFinder('https://sportsbook.draftkings.com/live')
        self.bid.driver.implicitly_wait(5)
        self.bid.set_type(ASK=0, BID=1)
        self.running = False

        self.ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)

    def PrintException(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def process(self, number, looper, bet_amount, match_number):
        try:
            match number:
                # Find live odds from the website
                case 1:
                    self.bid.results = self.bid.driver.find_elements(By.XPATH,
                         "(//tbody[@class='sportsbook-table__body'])[1]//tr")
                    for i in range(0, len(self.bid.results), 2):
                        self.team1_bid, self.team2_bid = \
                            self.bid.results[i], self.bid.results[i + 1]

                        self.team1_wagers_bid, self.team2_wagers_bid = \
                            self.team1_bid.find_elements(By.XPATH, self.wagers), \
                            self.team2_bid.find_elements(By.XPATH, self.wagers)

                        self.team1_bid, self.team2_bid = \
                            self.team1_bid.find_element(By.XPATH, self.find_name).text, \
                            self.team2_bid.find_element(By.XPATH, self.find_name).text

                        if 'Sox' in self.team1_bid:
                            self.team1_bid = ' '.join(self.team1_bid.split(' ')[-2:])
                        else:
                            self.team1_bid = self.team1_bid.split(' ')[-1]

                        if 'Sox' in self.team2_bid:
                            self.team2_bid = ' '.join(self.team2_bid.split(' ')[-2:])
                        else:
                            self.team2_bid = self.team2_bid.split(' ')[-1]

                        self.bid_wager_1_first, \
                        self.bid_wager_2_first, \
                        self.bid_wager_1_second, \
                        self.bid_wager_2_second, \
                        self.bid_wager_1_third, \
                        self.bid_wager_2_third = \
                            self.team1_wagers_bid[0], \
                            self.team2_wagers_bid[0], \
                            self.team1_wagers_bid[2], \
                            self.team2_wagers_bid[2], \
                            self.team1_wagers_bid[1], \
                            self.team2_wagers_bid[1]

                        self.bid_wager_1_first = ('' if 'disabled' in self.bid_wager_1_first.get_attribute('innerHTML') else self.bid_wager_1_first.text.replace('\n', ' '))
                        self.bid_wager_2_first = ('' if 'disabled' in self.bid_wager_2_first.get_attribute('innerHTML') else self.bid_wager_2_first.text.replace('\n', ' '))
                        self.bid_wager_1_second = ('' if 'disabled' in self.bid_wager_1_second.get_attribute('innerHTML') else self.bid_wager_1_second.text.replace('\n', ' '))
                        self.bid_wager_2_second = ('' if 'disabled' in self.bid_wager_2_second.get_attribute('innerHTML') else self.bid_wager_2_second.text.replace('\n', ' '))
                        self.bid_wager_1_third = ('' if 'disabled' in self.bid_wager_1_third.get_attribute('innerHTML') else self.bid_wager_1_third.text.replace('\n', ' '))
                        self.bid_wager_2_third = ('' if 'disabled' in self.bid_wager_2_third.get_attribute('innerHTML') else self.bid_wager_2_third.text.replace('\n', ' '))

                        self.l2[self.team1_bid.lower() + " vs "
                                + self.team2_bid.lower()] = \
                            [
                                [self.bid_wager_1_first.replace('  ', ' '),
                                 self.bid_wager_2_first.replace('  ', ' ')],
                                [self.bid_wager_1_second.replace('  ', ' '),
                                 self.bid_wager_2_second.replace('  ', ' ')],
                                [self.bid_wager_1_third.replace('  ', ' '),
                                 self.bid_wager_2_third.replace('  ', ' ')],
                                self.team1_bid,
                                self.team2_bid
                            ]
                    self.bid.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                # Find live odds from the website
                case 2:
                    self.ask.results = self.ask.driver.find_elements(By.XPATH,
                         "//a[@target='_self' and contains(@title,'@') and not(contains(.,'live event'))]/..")
                    for n, el in enumerate(self.ask.results):
                        self.ask_teams = self.ask.results[n].find_elements(By.XPATH, self.teams)
                        self.team1_ask, self.team2_ask = \
                            self.ask_teams[0].text, self.ask_teams[1].text

                        if 'Sox' in self.team1_ask:
                            self.team1_ask = ' '.join(self.team1_ask.split(' ')[-2:])
                        else:
                            self.team1_ask = self.team1_ask.split(' ')[-1]

                        if 'Sox' in self.team2_ask:
                            self.team2_ask = ' '.join(self.team2_ask.split(' ')[-2:])
                        else:
                            self.team2_ask = self.team2_ask.split(' ')[-1]

                        self.ask_team_wager = self.ask.results[n].find_elements(By.XPATH, self.second_wagers)
                        self.team1_wagers_ask, self.team2_wagers_ask = \
                            self.ask_team_wager[0], self.ask_team_wager[1]
                        self.team1_wagers_ask, self.team2_wagers_ask = \
                            self.team1_wagers_ask.find_elements(By.XPATH, "./div"), \
                            self.team2_wagers_ask.find_elements(By.XPATH, "./div")

                        self.l1[self.team1_ask.lower() + " vs " + self.team2_ask.lower()] = \
                            [
                                [self.team1_wagers_ask[0].text.replace('\n', ' ').replace('  ', ' '),
                                 self.team2_wagers_ask[0].text.replace('\n', ' ').replace('  ', ' ')],
                                [self.team1_wagers_ask[1].text.replace('\n', ' ').replace('  ', ' '),
                                 self.team2_wagers_ask[1].text.replace('\n', ' ').replace('  ', ' ')],
                                [self.team1_wagers_ask[2].text.replace('\n', ' ').replace('  ', ' '),
                                 self.team2_wagers_ask[2].text.replace('\n', ' ').replace('  ', ' ')],
                                self.team1_ask,
                                self.team2_ask
                            ]
                # Find the wager to select and click it
                case 3:
                    self.wager1 = self.bid.driver.find_elements(By.XPATH,
                        "(//tbody[@class='sportsbook-table__body'])[1]//tr[contains(.,'" +
                        self.wagering[1][4-looper] + "')]//td[contains(@class,'sportsbook-table__column-row')]")[match_number]

                    self.bid.driver.execute_script("arguments[0].scrollIntoView();", self.wager1)
                    self.wager1.click()

                    self.bid.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)

                    while self.bid_wager == '':
                        self.bid_wager = self.bid.driver.find_element(By.XPATH,
                          "//div[contains(@class,'betslip-odds__display-standard')]/span").text.strip()
                # Find the wager to select and click it
                case 4:
                    self.wager2 = self.ask.driver.find_elements(By.XPATH,
                        "//a[@target='_self' and contains(@title,' ') and contains(.,'live event')]/..//a[@target='_self' and contains(@title,' ') and not(contains(.,'live event')) and contains(.,'" +
                        self.wagering[0][3] + "') and contains(.,'" +
                        self.wagering[0][4] + "')]/../div/div")[looper]

                    self.wager2 = self.wager2.find_elements(By.TAG_NAME, 'div')[match_number]

                    self.ask.driver.execute_script(
                        "const mouseoverEvent = new Event('mouseover');arguments[0].dispatchEvent(mouseoverEvent)",
                        self.wager2)

                    self.ask.driver.execute_script("arguments[0].click();", self.wager2)

                    #self.wager2.click()

                    self.ask.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)

                    self.ask_wager = self.ask.driver.find_element(By.XPATH,
                      "//*[contains(@id,'cashout')]/../..//div[contains(@style,'transform')]").text.strip()
                # Remove all bets, if the odds have changed after the wager was selected
                case 5:
                    for elem in self.bid.driver.find_elements(By.XPATH,
                      "//div[contains(@class,'betslip-outcome-card')]/*[@aria-label='Close' and @role='img']"):
                        elem.click()
                # Remove all bets, if the odds have changed after the wager was selected
                case 6:
                    for elem in self.ask.driver.find_elements(By.XPATH, "//*[contains(@id,'remove-circle')]/.."):
                        elem.click()
                # Enter the stake amount
                case 7:
                    self.bet_input_bid = self.bid.driver.find_element(By.XPATH, "//input[@name='stake']")
                    # self.bet_input_bid.click()
                    self.bet_input_bid.send_keys(bet_amount)
                    try:
                        self.bid_button = self.bid.driver.find_element(By.XPATH, "//div[contains(@class,'place-bet-button__wrapper') and contains(.,'Place Bet')]")
                    except:
                        self.bid_button = None
                # Enter the stake amount
                case 8:
                    self.bet_input_ask = self.ask.driver.find_element(By.XPATH, "//span[text()='WAGER']/..//input")
                    # self.bet_input_ask.click()
                    self.bet_input_ask.send_keys(bet_amount)
                    try:
                        self.ask_button = self.ask.driver.find_element(By.XPATH,"//span[contains(text(),'Place')]/../../../..")
                    except:
                        self.ask_button = None
                # Submit the wager
                case 9:
                    self.bid_button.click()
                # Submit the wager
                case 10:
                    self.ask_button.click()
        except Exception as e:
            self.bid.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
            self.ask.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
            if self.show_error:
                # print(e)
                self.PrintException()
            else:
                pass

    def trading(self):
        # Bid XPATH
        self.find_name, self.wagers, self.bets = \
            ".//div[@class='event-cell__name-text']", \
            ".//td[contains(@class,'sportsbook-table__column-row')]", \
            "./../.."

        # Ask XPATH
        self.teams, self.second_wagers = \
            ".//div[contains(@style,'background-image')]/../div[2]/span",\
            "./div/div"

        if self.running:
            try:
                #self.tic = time.perf_counter()
                self.show_error, self.l1, self.l2, self.shared_keys, self.dict_intersection_2 = \
                    False, dict(), dict(), None, dict()

                # Find all live wagers for the sport
                self.pool.apply_async(self.process, args=(1, 0, 0, 0,))
                self.pool.apply_async(self.process, args=(2, 0, 0, 0,))
                # Join the pools so they run in parallel
                self.pool.join()

                #print(self.l1)
                #print(self.l2)

                # Combine all of the wagers based on the wager name in order to find matches between the websites
                self.shared_keys = self.l1.keys() & self.l2.keys()
                self.dict_intersection_2 = {k: [self.l1[k], self.l2[k]] for k in self.shared_keys}

                # Print the latest live matched wagers, if the live matched wagers have changed
                self.new_list = self.shared_keys
                if self.new_list != self.old_list:
                    print(self.new_list)
                    self.old_list = self.new_list
                # print(self.dict_intersection_2)

                self.show_error = True
                for k in self.dict_intersection_2:
                    self.wagering = self.dict_intersection_2[k]
                    #print(self.wagering)

                    # Convert negative odds to positive values
                    for i in range(1):
                        for j in range(3):  # len(self.wagering[i])
                            for q in range(2):
                                self.wager_val_text, self.wager_val_text2 = \
                                    self.wagering[i][j][q].split(' '), self.wagering[i+1][j][q].split(' ')

                                self.wager_val, self.wager_val2 = self.wager_val_text[-1], self.wager_val_text2[-1]

                                if j != 2:
                                    self.wager_val_text.pop()
                                    self.wager_val_text2.pop()

                                    self.wager_val_text, self.wager_val_text2 = \
                                        ' '.join(self.wager_val_text), ' '.join(self.wager_val_text2)

                                    self.wager_val_text, self.wager_val_text2 = \
                                        self.wager_val_text.replace(' ', '')[1:], \
                                        self.wager_val_text2.replace(' ', '')[1:]

                                    if self.wager_val_text != self.wager_val_text2:
                                        self.wager_val, self.wager_val2 = '',  ''

                                #print(self.wager_val, self.wager_val2)

                                if self.wager_val == '':
                                    self.wager_val = 0
                                else:
                                    self.wager_val = int(float(self.wager_val))

                                    if self.wager_val < 0:
                                        self.wager_val = 100 / -self.wager_val * 100
                                    else:
                                        self.wager_val = self.wager_val  # / 100

                                self.wagering[i][j][q] = self.wager_val

                                if self.wager_val2 == '':
                                    self.wager_val2 = 0
                                else:
                                    self.wager_val2 = int(float(self.wager_val2))

                                    if self.wager_val2 < 0:
                                        self.wager_val2 = 100 / -self.wager_val2 * 100
                                    else:
                                        self.wager_val2 = self.wager_val2  # / 100

                                self.wagering[i+1][j][q] = self.wager_val2

                    #print(self.wagering)

                    #self.toc = time.perf_counter()
                    #print(self.toc - self.tic)

                    # Using the Nash equilibrium, find if there are arbitrage opportunities
                    # If there are opportunities, click the wagers
                    # If the odds have not changed after the wager has been selected, then enter a stake amount
                    # If the odds still have not changed, then submit the wager
                    for q in range(3):
                        for i in range(2):
                            self.make_bet = True

                            if self.wagering[0][q][i] <= self.odds_limit and self.wagering[1][q][1 - i] <= self.odds_limit:
                                self.A = np.array([[self.wagering[0][q][i], -100],
                                                   [-100, self.wagering[1][q][1 - i]]])

                                self.matching = 0
                                match q:
                                    case 0:
                                        self.matching = 0
                                    case 1:
                                        self.matching = 2
                                    case 2:
                                        self.matching = 1

                                self.rps = nash.Game(self.A)

                                self.eqs = self.rps.support_enumeration()
                                self.result = list(self.eqs)[0][0]
                                # print(self.result)

                                self.bet_amount = self.main_bet_amount
                                self.result = self.bet_amount * self.result
                                self.result = [round(x, 2) for x in self.result]
                                self.betamount_ask, self.betamount_bid = self.result[0], self.result[1]

                                self.bet_amount, self.sum_val = sum(self.result), 0
                                # print(self.result)

                                # Make sure both bets have a positive return
                                for m in range(len(self.result)):
                                    if (self.result[m] * self.A[m][m] / 100 + self.result[m]) <= self.bet_amount:
                                        self.make_bet = False
                                    self.sum_val += sum(self.result[m] * self.A[m])

                                self.return_val = self.sum_val / len(self.result) / 100

                                if self.make_bet and self.betamount_bid >= self.bet_limit \
                                        and self.betamount_ask >= self.bet_limit \
                                        and (self.return_val / self.bet_amount) >= self.lower_limit\
                                        and (self.return_val / self.bet_amount) <= self.upper_limit:
                                    self.bid_wager, self.ask_wager = '', ''

                                    self.pool.apply_async(self.process, args=(3, i, 0, self.matching, ))
                                    self.pool.apply_async(self.process, args=(4, i, 0, q, ))
                                    # Join the pools so they run in parallel
                                    self.pool.join()

                                    self.bid_wager, self.ask_wager = \
                                        self.bid_wager.replace(' ', '').replace(',', '').replace('−', '-'), \
                                        self.ask_wager.replace(' ', '').replace(',', '').replace('−', '-')

                                    if self.bid_wager == '':
                                        self.bid_wager = 0

                                    if self.ask_wager == '':
                                        self.ask_wager = 0

                                    self.bid_wager, self.ask_wager = \
                                        int(float(self.bid_wager)), int(float(self.ask_wager))

                                    if self.bid_wager < 0:
                                        self.bid_wager = -100 / self.bid_wager * 100
                                    elif self.ask_wager < 0:
                                        self.ask_wager = -100 / self.ask_wager * 100

                                    self.A = np.array([[self.ask_wager, -100],
                                                       [-100, self.bid_wager]])

                                    self.rps = nash.Game(self.A)

                                    self.eqs = self.rps.support_enumeration()
                                    self.result = list(self.eqs)[0][0]
                                    # print(self.result)

                                    self.bet_amount = self.main_bet_amount
                                    self.result = self.bet_amount * self.result
                                    self.result = [round(x, 2) for x in self.result]
                                    self.betamount_ask, self.betamount_bid = self.result[0], self.result[1]

                                    self.bet_amount, self.sum_val = sum(self.result), 0
                                    # print(self.result)

                                    for m in range(len(self.result)):
                                        if (self.result[m] * self.A[m][m] / 100 + self.result[m]) <= self.bet_amount:
                                            self.make_bet = False
                                        self.sum_val += sum(self.result[m] * self.A[m])

                                    self.return_val = self.sum_val / len(self.result) / 100

                                    self.bid_button, self.ask_button = None, None

                                    if self.make_bet and self.betamount_bid >= self.bet_limit and \
                                            self.betamount_ask >= self.bet_limit \
                                            and (self.return_val / self.bet_amount) >= self.lower_limit\
                                            and (self.return_val / self.bet_amount) <= self.upper_limit:
                                        self.pool.apply_async(self.process, args=(7, 0, self.betamount_bid, 0,))
                                        self.pool.apply_async(self.process, args=(8, 0, self.betamount_ask, 0,))
                                        # Join the pools so they run in parallel
                                        self.pool.join()

                                        if self.ask_button != None and self.ask_button != None:
                                            '''
                                            self.pool.apply_async(self.process, args=(9, 0, 0, 0,))
                                            self.pool.apply_async(self.process, args=(10, 0, 0, 0,))
                                            # Join the pools so they run in parallel
                                            self.pool.join()
                                            '''

                                            print(True)
                                            print(k, self.wagering)
                                            print(self.bid_wager, self.ask_wager)
                                            print(self.return_val)
                                            time.sleep(60 * random.randint(1, 1))
                                        else:
                                            #time.sleep(5)

                                            self.pool.apply_async(self.process, args=(5, 0, 0, 0,))
                                            self.pool.apply_async(self.process, args=(6, 0, 0, 0,))
                                            # Join the pools so they run in parallel
                                            self.pool.join()

                                            print(False)
                                    else:
                                        time.sleep(5)

                                        self.pool.apply_async(self.process, args=(5, 0, 0, 0,))
                                        self.pool.apply_async(self.process, args=(6, 0, 0, 0,))
                                        # Join the pools so they run in parallel
                                        self.pool.join()

                                        print(False)
            except Exception as e:
                self.bid.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                self.ask.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
                if self.show_error:
                    # print(e)
                    self.PrintException()
                else:
                    pass

        # Run again after 1ms
        self.root.after(10, self.trading)

    def run(self):
        # Create buttons so we can start and stop the model from running
        self.root = Tk()
        self.root.title("Arb Finder")
        self.root.geometry("300x100")

        app = Frame(self.root)
        app.grid()

        start = Button(app, text="Start", command=self.start)
        stop = Button(app, text="Stop", command=self.stop)
        start.grid(row=0, column=0, padx=(40, 40), pady=(40, 40))
        stop.grid(row=0, column=1, padx=(40, 40), pady=(40, 40))

        start.grid()
        stop.grid()

        self.root.after(1, self.trading)  # After 1 second, call scanning
        self.root.mainloop()


# Create the app and run it
app = App()
app.run()