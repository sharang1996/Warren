from datetime import datetime, timedelta
import pickle
import pysentiment as ps
import tweepy
import time
import re
import ConfigParser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
def get_config(config_file_name):
   # Read config file and return config object
   options = ConfigParser.ConfigParser()
   options.read(config_file_name)
   return options
def get_twitter_sentiment(ticker, company):
   # fetch oath tokens from config.ini to secure them
   conf = get_config('config.ini')
   ckey = conf.get('twitter', 'ckey')
   csecret = conf.get('twitter', 'csecret')
   atoken = conf.get('twitter', 'atoken')
   asecret = conf.get('twitter', 'asecret')
   auth = tweepy.OAuthHandler(ckey, csecret)
   auth.set_access_token(atoken, asecret)
   api = tweepy.API(auth)

   hiv4 = ps.HIV4()
   ss = '!!'  # cleaning mark
   t = ""
   s = ''
   d = datetime.today()
   d7 = d - timedelta(days=7)
   d = d.strftime("%Y-%m-%d")
   d7 = d7.strftime("%Y-%m-%d")
   try:
       for tweet in tweepy.Cursor(api.search, q=company, since=str(d7), until=str(d), lang="en").items():
           s = ss + tweet.text
           print(s)
           # cleaning the tweets
           s = s.replace(ss + 'RT ', '')
           result = re.sub(r"http\S+", "", s)
           # http  matches literal characters
           # \S+ matches all non-whitespace characters (the end of the url)
           t = t + result + '\n'
   except Exception as e:
       time.sleep(10)
       try:
           for tweet in tweepy.Cursor(api.search, q=ticker, since=d7, until=d, lang="en").items():
               s = ss + tweet.text
               print(s)
               # cleaning the tweets
               s = s.replace(ss + 'RT ', '')
               result = re.sub(r"http\S+", "", s)
               # http  matches literal characters
               # \S+ matches all non-whitespace characters (the end of the url)
               t = t + result + '\n'
       except Exception as e:
           time.sleep(10)
   tokens = hiv4.tokenize(t)
   score = hiv4.get_score(tokens)
   return score
# print(get_twitter_sentiment('aapl', 'apple'))
def get_news_sentiment(ticker):
   ticker = ticker.upper()
   hiv4 = ps.HIV4()
   # -- Setup
   options = Options()
   options.add_argument("--headless")
   browser = webdriver.Firefox(firefox_options=options)
   # -- Parse
   #browser.get("https://seekingalpha.com/symbol/" + ticker + "/analysis-and-news?analysis_tab=focus&news_tab=news-all")
   browser.get("https://simulationstock.000webhostapp.com/MSFT.html")
   soup = BeautifulSoup(browser.page_source, "html5lib")
   x = ''
   for div_tag in soup.find_all('div', attrs={"class": "mc_list_texting right bullets"}, limit=7):
       for span_tag in div_tag.find_all('span', attrs={"class": "general_summary light_text bullets"}):
           x = x + span_tag.text
   print(x)
   tokens = hiv4.tokenize(x)
   score = hiv4.get_score(tokens)
   browser.close()
   return score
score = get_news_sentiment('msft')
print(score)
ratio = float(float(score['Positive'])/ float(score['Negative']))
print('\n SENTIMENT RATIO : ' + str(ratio))
