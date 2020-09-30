import requests
import sklearn
from sklearn import svm
from sklearn.neural_network import MLPClassifier
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging
import ConfigParser
import os
from datetime import datetime

def get_config(config_file_name):
   # Read config file and return config object
   options = ConfigParser.ConfigParser()
   options.read(config_file_name)
   return options

def prepare_dataset(base_url, api_key, ticker):
   url = base_url + 'function=TIME_SERIES_DAILY&symbol=' + ticker.upper() + '&outputsize=full&apikey=' + api_key
   package_json = requests.get(url).json()
   dates = list(package_json['Time Series (Daily)'].keys())
   l = package_json['Time Series (Daily)']

   url_s = base_url + 'function=SMA&symbol=' + ticker.upper() + '&interval=daily&time_period=50&series_type=close&apikey=' + api_key
   package_json_s = requests.get(url_s).json()

   url_e = base_url + 'function=EMA&symbol=' + ticker.upper() + '&interval=daily&time_period=50&series_type=close&apikey=' + api_key
   package_json_e = requests.get(url_e).json()

   url_m = base_url + 'function=MACD&symbol=' + ticker.upper() + '&interval=daily&series_type=close&apikey=' + api_key
   package_json_m = requests.get(url_m).json()

   url_st = base_url + 'function=STOCH&symbol=' + ticker.upper() + '&interval=daily&apikey=' + api_key
   package_json_st = requests.get(url_st).json()

   url_r = base_url + 'function=RSI&symbol=' + ticker.upper() + '&interval=daily&time_period=40&series_type=close&apikey=' + api_key
   package_json_r = requests.get(url_r).json()

   url_a = base_url + 'function=ADX&symbol=' + ticker.upper() + '&interval=daily&time_period=14&apikey=' + api_key
   package_json_a = requests.get(url_a).json()

   url_c = base_url + 'function=CCI&symbol=' + ticker.upper() + '&interval=daily&time_period=20&apikey=' + api_key
   package_json_c = requests.get(url_c).json()

   url_ar = base_url + 'function=AROON&symbol=' + ticker.upper() + '&interval=daily&time_period=25&apikey=' + api_key
   package_json_ar = requests.get(url_ar).json()

   url_b = base_url + 'function=BBANDS&symbol=' + ticker.upper() + '&interval=daily&time_period=20&series_type=close&apikey=' + api_key
   package_json_b = requests.get(url_b).json()

   url_ad = base_url + 'function=AD&symbol=' + ticker.upper() + '&interval=daily&time_period=50&series_type=close&apikey=' + api_key
   package_json_ad = requests.get(url_ad).json()

   url_o = base_url + 'function=OBV&symbol=' + ticker.upper() + '&interval=daily&apikey=' + api_key
   package_json_o = requests.get(url_o).json()
   labels = []
   arr = []
   for i in range(len(dates) - 1):
       ts = dates[i + 1]

       gap = float(l[dates[i]]['1. open']) - float(l[ts]['4. close'])
       high = float(l[ts]['2. high'])
       low = float(l[ts]['3. low'])
       volume = float(l[ts]['5. volume'])
       sma = get_sma(package_json_s, ts)
       ema = get_ema(package_json_e, ts)
       macd = get_macd(package_json_m, ts)
       stoch1, stoch2 = get_stoch(package_json_st, ts)
       rsi = get_rsi(package_json_r, ts)
       adx = get_adx(package_json_a, ts)
       aroon1, aroon2 = get_aroon(package_json_ar, ts)
       bbands1, bbands2, bbands3 = get_bbands(package_json_b, ts)
       ad = get_ad(package_json_ad, ts)
       obv = get_obv(package_json_o, ts)
       cci = get_cci(package_json_c, ts)
       temp = [gap, high, low, volume, sma, ema, macd, stoch1, stoch2, rsi, adx, cci, aroon1, aroon2, bbands1, bbands2, bbands3, ad, obv]
       arr.append(temp)
       if float(l[dates[i]]['1. open']) >= float(l[dates[i]]['4. close']):
           labels.append(0)
       else:
           labels.append(1)
   X = np.array(arr)
   Y = labels
   x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(X, Y, test_size=0.2, random_state=73)
   scaler = StandardScaler()
   x_train_scaled = scaler.fit(x_train).transform(x_train)
   x_test_scaled = scaler.fit(x_test).transform(x_test)
   clf = MLPClassifier(hidden_layer_sizes=1500, alpha=1, max_iter=6000, random_state=42)
   model = clf.fit(x_train_scaled, y_train)
   print(clf.score(x_train_scaled, y_train))
   print(clf.score(x_test_scaled, y_test))

def get_sma(package_json, ts):
   l = package_json['Technical Analysis: SMA']
   if ts not in l:
       return 0.0
   return float(l[ts]['SMA'])

def get_ema(package_json, ts):
   l = package_json['Technical Analysis: EMA']
   if ts not in l:
       return 0.0
   return float(l[ts]['EMA'])
def get_macd(package_json, ts):
   l = package_json['Technical Analysis: MACD']
   if ts not in l:
       return 0.0
   return float(l[ts]['MACD'])

def get_stoch(package_json, ts):
   l = package_json['Technical Analysis: STOCH']
   if ts not in l:
       return 0.0, 0.0
   return float(l[ts]['SlowD']), float(l[ts]['SlowK'])

def get_rsi(package_json, ts):
   l = package_json['Technical Analysis: RSI']
   if ts not in l:
       return 0.0
   return float(l[ts]['RSI'])

def get_adx(package_json, ts):
   l = package_json['Technical Analysis: ADX']
   if ts not in l:
       return 0.0
   return float(l[ts]['ADX'])
def get_cci(package_json, ts):
   l = package_json['Technical Analysis: CCI']
   if ts not in l:
       return 0.0
   return float(l[ts]['CCI'])

def get_aroon(package_json, ts):
   l = package_json['Technical Analysis: AROON']
   if ts not in l:
       return 0.0, 0.0
   return float(l[ts]['Aroon Up']), float(l[ts]['Aroon Down'])

def get_bbands(package_json, ts):
   l = package_json['Technical Analysis: BBANDS']
   if ts not in l:
       return 0.0, 0.0, 0.0
   return float(l[ts]['Real Upper Band']), float(l[ts]['Real Lower Band']), float(l[ts]['Real Middle Band'])

def get_ad(package_json, ts):
   l = package_json['Technical Analysis: Chaikin A/D']
   if ts not in l:
       return 0.0
   return float(l[ts]['Chaikin A/D'])

def get_obv(package_json, ts):
   l = package_json['Technical Analysis: OBV']
   if ts not in l:
       return 0.0
   return float(l[ts]['OBV'])

def main():  # pragma: no cover
   """This function is where execution starts"""

   project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
   conf_rel = os.path.join(project_path, 'etc', 'config.ini')
   conf = get_config(conf_rel)
   var_dir = os.path.join(project_path, 'var')
   date = datetime.now().strftime('%Y_%m_%d')
   log_file = os.path.join(var_dir, 'log', 'technical_analysis_logfile' + date)
   logging.basicConfig(
       filename=log_file,
       level=logging.DEBUG)

   api_key = conf.get('technical', 'api_key')
   url = conf.get('technical', 'base_url')

   prepare_dataset(url, api_key, 'AAPL')

if __name__ == "__main__":  # pragma: no cover
   main()
