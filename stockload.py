#Run this code first, to get the dataframes of the adjusted open and close prices
#The getstocks() function variables are start date (y,m,d), end date(y,m,d), and list of ticker symbols
#Example code to run:
#tickers = ["MMM","ABT","ACE","ACN","ACT","AES","AET","AFL","AMG","A","GAS","APD","ARG","AKAM","AA","ALXN"]
#closeprices,openprices = getstocks(2010,1,1,2011,1,1,tickers)


import pandas.io.data as web
import pandas as pd
import datetime
import numpy as np


def getstocks(starty,startm,startd,endy,endm,endd,stocklist):
    start =  datetime.datetime(starty,startm,startd)
    end = datetime.datetime(endy,endm,endd)
    
    stockdata = dict((stock,web.DataReader(stock,'yahoo',start,end,pause=1)) for stock in stocklist)
    panel = pd.Panel(stockdata).swapaxes('items','minor')
    adjclose = panel['Adj Close'].dropna()
    closeprice = panel['Close'].dropna()
    openprice = panel['Open'].dropna()
    adjopen = pd.DataFrame((np.array(adjclose) / np.array(closeprice)) * np.array(openprice),index=adjclose.index,columns=adjclose.columns)

    return adjclose, adjopen


#When using the big list of ticker symbols I'll post:
#sandp = pd.read_csv('C:\Users\Thomas\SkyDrive\Documents\Programming Projects\Python Learning\\sandp.csv')
#sandp = list(sandp.ix[:,1])
#closeprices,openprices = getstocks(2010,1,1,2011,1,1,sandp)
