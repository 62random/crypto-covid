import pandas as pd
from Adafruit_IO import Client
import ast
import sys
from sklearn import preprocessing
from collections import deque
import numpy as np
import random
import time
import datetime
import os

IO_USERNAME = os.environ.get('IO_USERNAME')
IO_KEY = os.environ.get('IO_KEY')
IO_FEED = 'crypto-covid'

# Instance adafruit client and get data from specific feed
aio = Client(IO_USERNAME, IO_KEY)
data = aio.data(IO_FEED)


df = pd.DataFrame()

for d in data:
    row = ast.literal_eval(d.value)
    date = datetime.datetime.fromtimestamp(row['time'])
    arr = str(date)[:10].split('-')
    del row['time']
    row['timestamp'] = f"{int(arr[0]):02d}-{int(arr[1]):02d}-{int(arr[2]):02d}"
    df = df.append(row, ignore_index=True)

df = df.sort_values(['timestamp'], ascending=[1])
df.set_index('timestamp', inplace=True)


for c in df.columns:
    if '_tdeaths' in c:
        df = df.rename(columns={c: c[:-8] + '_deaths'})
    elif '_tcases' in c:
        df = df.rename(columns={c: c[:-7] + '_confirmed'})
    elif '_ncases' in c:
        df.drop(c, axis=1, inplace=True)

external = pd.read_csv('external_dataset.csv', index_col='timestamp')
external.index.rename('timestamp', inplace=True)



df = pd.concat([external, df])

df.fillna(0, inplace=True)

df.to_csv('dataset.csv', index=True)
