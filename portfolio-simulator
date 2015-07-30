import pandas as pd
import numpy as np


def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')


def buysellfunc(avgshort, daily):

    nomstock = len(daily[0]) 
    x = len(daily)

    #initialize a blank buysell and buyorder list
    buysell = list()
    buyorder = list()
    
    #buy/sell algorithm. This part needs tuning and rewritten to be more easily tunable
    #originally had buy and sell multipliers
    for n in range(0,nomstock):
        if np.mean(daily[(x-avgshort):x,n]) > np.mean(daily[0:x,n]):
            buysell.append(-1)
        elif np.mean(daily[(x-avgshort):x,n]) < np.mean(daily[0:x,n]):
            buysell.append(1)
        else:
            buysell.append(0)
        #This list shows the program which stock to buy first when there are multiple 1's on the buysell dataframe
        buyorder.append(np.mean(daily[0:x,n])/np.mean(daily[(x-avgshort):x,n]))

    return buysell, buyorder


def get_col_order(row,stocks,buyorder,nomstock):
    buyorderrow = list()
    for i in range(0,nomstock):
        b = buyorder.ix[row]==stocks[i]
        buyorderrow.append(b.argmax())
    return buyorderrow
    
            
def buyfunc(day,y,nomstock,nomdays,prefbuy,ownnot,anyowned,bsevent,buysell):
    #purchases stock
    for n in range(0,y): #the range here is the # of stock possible in portfolio
        #finds how many can be purchased based on portfolio split limit
        #compared to how many are currently owned
        nompurchase = y - anyowned.ix[day].sum()
        if nompurchase >= 1:
            for i in range(0,len(prefbuy)):
                if nompurchase >= 1:
                    if ownnot.ix[day,prefbuy[i]] == 0 and buysell.ix[day,prefbuy[i]] == 1 and anyowned.ix[day,n] == 0:
                        nompurchase = nompurchase - 1
                        anyowned.ix[range(day,nomdays),n] = 1
                        bsevent.ix[day,prefbuy[i]] = 1
                        ownnot.ix[range(day,nomdays),prefbuy[i]] = 1
                else:
                    return ownnot,anyowned,bsevent
        else:
            return ownnot,anyowned,bsevent
    return ownnot,anyowned,bsevent
    
    
                
#def daysfunc(day,daysowned,bsevent,nomstock):
    #finds how long each stock has been owned
    #for n in range(0,nomstock):
        #if owned previous day, adds one to that in todays position
        #if bsevent.ix[day,n] == 0:
            #if daysowned.ix[day-1,n] >= 1:
                #daysowned.ix[day,n] = daysowned.ix[day-1,n] + 1
        #if stock purchased today, sets daysowned to 1
        #elif bsevent.ix[day,n] == 1:
            #daysowned.ix[day,n] = 1
        #if stock sold today, sets daysowned to 0
        #elif bsevent.ix[day,n] == -1:
            #daysowned.ix[day,n] = 0
    #return daysowned
    
    
def sellfunc(day,nomstock,nomdays,ownnot,anyowned,bsevent,buysell):
    #finds how many can be sold
    nomcansell = anyowned.ix[day].sum()
    #if any stock owned, matches owned stock with stock that needs to be
    #sold according to buysell
    if nomcansell != 0:
        for n in range(0,nomstock):
            if ownnot.ix[day,n] == 1:
                if buysell.ix[day,n] == -1:
                    ownnot.ix[range(day,nomdays),n] = 0
                    bsevent.ix[day,n] = -1
                    #finds the first split in portfolio currently full and 
                    #sets it to 0
                    b = anyowned.ix[day] == 1
                    c = b.argmax()
                    anyowned.ix[range(day,nomdays),c] = 0
    else:
        return ownnot,anyowned,bsevent
    return ownnot,anyowned,bsevent
    
    
def cashfunc(day,y,nomstock,nomdays,cashtotal,cashavail,investedcash,bsevent,anyowned,nomshares,daily,openprice,closeprice):
    
    #initialize how much money should be put in each bought stock per day
    buyamount = cashtotal.ix[day,0] / y
    buynum = 0
    buytotal = 0
    sellnum = 0
    selltotal = 0
    
    #populates the various cash dataframes
    #All buys occur at start of trading on that day and sells occur at end.
    for n in range(0,nomstock):
        #Sets the # of shares bought in nomshares and sets the cost of investment at open for that # of shares in investedcash
        if bsevent.ix[day-1,n] == 1:
            nomshares.ix[range(day,nomdays),n] = buyamount // openprice.ix[day,n] 
            investedcash.ix[range(day,nomdays),n] = nomshares.ix[day,n] * openprice.ix[day,n]
            buynum = buynum + 1
            buytotal = buytotal + investedcash.ix[day,n]
            
        #sets the amount in investedcash at end of trading day
        investedcash.ix[range(day,nomdays),n] = (investedcash.ix[day,n] * daily.ix[day,n]) + investedcash.ix[day,n]
        
        #remove investedcash and nomshares on sell event at end of day
        if bsevent.ix[day,n] == -1:
            selltotal = selltotal + investedcash.ix[day,n]
            investedcash.ix[range(day,nomdays),n] = 0
            sellnum = sellnum + 1 
            nomshares.ix[range(day,nomdays),n] = 0
            
            
    #subtracts investment from cashavail on buy
    if buynum >= 1:
        cashavail.ix[range(day,nomdays)] = cashavail.ix[day,0] - buytotal
        
    #adds sold investments to cashavail
    if sellnum >= 1:
        cashavail.ix[range(day,nomdays)] = cashavail.ix[day,0] + selltotal 

    #keeps track of portfolio value
    cashtotal.ix[range(day,nomdays),0] = cashavail.ix[day,0] + investedcash.ix[day].sum()
    
    return nomshares,cashtotal,cashavail,investedcash

#openprice is the imported dataframe of daily open price
#closeprice is the imported dataframe of daily close price        
#daily is the imported dataframe of daily returns on stocks
#y is the number of splits in the portfolio
#r is the starting day, which must be after t
#t is the long moving average
#q is the short moving average
#mon is the starting value of the portolio in dollars
def optimport(openprice,closeprice,daily,y,r,t,q,mon):
    nomdays = len(daily)
    nomstock = len(daily.columns)
    buysell = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    ownnot = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    ownnot = pd.DataFrame.fillna(ownnot,0)
    bsevent = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    bsevent = pd.DataFrame.fillna(bsevent,0)
    anyowned = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,y)])
    anyowned = pd.DataFrame.fillna(anyowned,0)
    buyorder = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    cashtotal = pd.DataFrame([[mon]],index=[range(0,nomdays)])
    cashavail = pd.DataFrame([[mon]],index=[range(0,nomdays)])
    investedcash = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    investedcash = pd.DataFrame.fillna(investedcash,0)
    daysowned = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    daysowned = pd.DataFrame.fillna(daysowned,0)
    nomshares = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    nomshares = pd.DataFrame.fillna(nomshares,0)
    for i in range(r,nomdays):
        #populate buysell and buyorder
        x = np.array(closeprice[(i-t):i])
        j,v = buysellfunc(q,x)
        buysell.ix[i,0:nomstock-1] = j
        buyorder.ix[i,0:nomstock-1] = v
        #buying
        u = np.sort(buyorder.ix[i])
        prefbuy = get_col_order(i,u,buyorder,nomstock)
        ownnot,anyowned,bsevent = buyfunc(i,y,nomstock,nomdays,prefbuy,ownnot,anyowned,bsevent,buysell)
        #selling
        ownnot,anyowned,bsevent = sellfunc(i,nomstock,nomdays,ownnot,anyowned,bsevent,buysell)
        #populates daysowned
        #daysowned = daysfunc(i,daysowned,bsevent,nomstock)
        #calculate money
        nomshares,cashtotal,cashavail,investedcash = cashfunc(i,y,nomstock,nomdays,cashtotal,cashavail,investedcash,bsevent,anyowned,nomshares,daily,openprice,closeprice)
        
    #You can change these to get various insights on what is happening.    
    print_full(nomshares)
    print_full(cashtotal)

#Import the csv files from R using:
#openprices = pd.read_csv('...\openprice.csv')        
#Example function run:
# optimport(openprices,closeprices,returns,4,51,50,10,10000)
