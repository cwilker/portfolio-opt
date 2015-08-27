#First load your stock data in from the other python file, stockload.py
#Then run this code.
#The main function is optimport(), and the description of the variables can be found around line 186
#Example code to run:
# optimport(openprices,closeprices,4,51,50,10,10000)

#At the bottom of this file are a few testing functions
#An example to run:
# bootopt(10,20,openprices,closeprices,4,51,50,10,10000)



import pandas as pd
import numpy as np


#The print_fill() function can be used to force IPython to print out 
#the entire data frame
#def print_full(x):
#    pd.set_option('display.max_rows', len(x))
#    print(x)
#    pd.reset_option('display.max_rows')


#The buysellfunc() goes through and determines when something is buyable or sellable
#Currently this is based on the short term moving average vs. the this value minus 2.5 * the rolling STD over the same time period
#The long term moving average is only used for the function for deciding the order to buy.
#These algorithms are the most important things to improve on.
def buysellfunc(closeprice, shortavg, longavg, buysell,nomstock):
    shortmean = pd.rolling_mean(closeprice,shortavg)
    shortmean = shortmean.fillna(0)
    longmean = pd.rolling_mean(closeprice,longavg)
    longmean = longmean.fillna(0)
    shortstd = pd.rolling_std(shortmean,shortavg)
    shortstd = shortmean - (2.5 * shortstd)

    submean = shortmean.values - longmean.values

    buysell = pd.DataFrame(submean,index=buysell.index,columns=buysell.columns)
   
    #
    return shortmean, shortstd, buysell 
    
    
#Goes through each day and buys purchaseable stock based on the buysell dataframe in the order of the prefbuy list
#depending on whether or not there is room in the portfolio and whether or not the stock is already owned             
def buyfunc(day,y,nomstock,nomdays,prefbuy,ownnot,anyowned,bsevent,buysell,closeprice):
    
    for n in range(0,y): #the range here is the # of stock possible in portfolio
    #finds how many can be purchased based on portfolio split limit
    #compared to how many are currently owned
        nompurchase = y - anyowned.ix[day].sum()
        #if room in portfolio
        if nompurchase >= 1:
            #if stock not currently owned
            if anyowned.ix[day,n] == 0:
                own = list(ownnot.ix[day])
                bstoday = list(buysell.ix[day])
                bsyesterday = list(buysell.ix[day-1])
                pricetoday = list(closeprice.ix[day])
                priceyesterday = list(closeprice.ix[day-1])
                #### This is part of the buy algorithm that also needs to be worked on for bottom line improvement
                #Checks to see if its a cross point from the end of day price going below the short term moving ave. minus the short term STD
                buylist = [x for x in range(0,nomstock) if own[x] == 0 and pricetoday[x] < bstoday[x] and priceyesterday[x] > bsyesterday[x]]
                if len(list(buylist)) > 0:
                    done = False
                    for y in prefbuy:
                        for z in buylist:
                            if y == z:                            
                                nompurchase = nompurchase - 1
                                anyowned.ix[range(day,nomdays),n] = 1
                                bsevent.ix[day,y] = 1
                                ownnot.ix[range(day,nomdays),y] = 1
                                done = True
                                break
                        if done == True:
                            break
                else:
                    return ownnot,anyowned,bsevent

        else:
            return ownnot,anyowned,bsevent


    return ownnot,anyowned,bsevent     
    

    
#Below is a function from an earlier version that might be useful someday, after it's been optimized for speed
#It creates a dataframe that tells how long a stock has been owned  
                
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
    

#Function that sells any stock that has a crossover point from the price yesterday being above the 
#short term moving average to the close price today being below the short term moving average.     
def sellfunc(day,nomstock,nomdays,ownnot,anyowned,bsevent,shortmean,closeprice):
    #finds how many can be sold
    own = list(ownnot.ix[day])
    sellcon = list(shortmean.ix[day])
    pricetoday = list(closeprice.ix[day])
    priceyesterday = list(closeprice.ix[day-1])
    selllist = (x for x in range(0,nomstock) if own[x] == 1 and priceyesterday[x] > sellcon[x] and pricetoday[x] < sellcon[x])

    for n in selllist:
        ownnot.ix[range(day,nomdays),n] = 0
        bsevent.ix[day,n] = -1
        #finds the first split in portfolio currently full and 
        #sets it to 0
        b = anyowned.ix[day] == 1
        c = b.argmax()
        anyowned.ix[range(day,nomdays),c] = 0
    return ownnot,anyowned,bsevent
    



        
def cashfunc(day,y,nomstock,nomdays,cashtotal,cashavail,investedcash,bsevent,anyowned,nomshares,openprice,closeprice):
    
    #initialize how much money should be put in each bought stock per day
    buyamount = cashtotal.ix[day,0] / y
    buytotal = 0
    selltotal = 0
    
    #populates the various cash dataframes
    #All buys occur at start of trading on that day and sells occur at end.
    blist = list(bsevent.ix[day-1])
    buylist = list((x for x in range(0,nomstock) if blist[x] == 1))
    for n in buylist:
        #Sets the # of shares bought in nomshares and sets the cost of investment at open for that # of shares in investedcash
        nomshares.ix[range(day,nomdays),n] = buyamount // openprice.ix[day,n] 
        investment = nomshares.ix[day,n] * openprice.ix[day,n]
        buytotal = buytotal + investment
    buynum = len(buylist)
    

    #sets the amount in investedcash at end of trading day
    #by multiplying the end of day price times the number of shares owned    
    investedcash.ix[day] = np.array(nomshares.ix[day]) * np.array(closeprice.ix[day])
      

    #remove investedcash and nomshares on sell event at end of day
    slist = list(bsevent.ix[day])
    selllist = list((x for x in range(0,nomstock) if slist[x] == -1))
    sellnum = len(selllist)

    
    for n in selllist:
        selltotal = selltotal + investedcash.ix[day,n]
        investedcash.ix[day,n] = 0 
        nomshares.ix[range(day,nomdays),n] = 0 
              
    #subtracts investment from cashavail on buy
    if buynum >= 1:
        cashavail.ix[range(day,nomdays)] = cashavail.ix[day,0] - buytotal
        
    #adds sold investments to cashavail
    if sellnum >= 1:
        cashavail.ix[range(day,nomdays)] = cashavail.ix[day,0] + selltotal 

    #keeps track of portfolio value
    cashtotal.ix[day+1,0] = cashavail.ix[day,0] + investedcash.ix[day].sum()

    return nomshares,cashtotal,cashavail,investedcash


#Used in determining the order to buy stock.
#Currently although it works, the logic is not sound 
#due to how I changed the buysell dataframe to be based on crossover points 
def rankfunc(buysell):
    buyorder = buysell.rank(axis=1,method='first',ascending=True)
    return np.round(buyorder)



#optimport() function variables:
    #openprice is the imported dataframe of daily open price
    #closeprice is the imported dataframe of daily close price        
    #y is the number of splits in the portfolio
    #r is the starting day, which must be after t
    #t is the long moving average
    #q is the short moving average
    #s is the very short moving average for sell
    #mon is the starting value of the portolio in dollars
def optimport(openprice,closeprice,y,r,t,q,mon):
    nomdays = len(openprice)-1
    nomstock = len(openprice.columns)
    buysell = pd.DataFrame(index=[range(0,nomdays+1)],columns=[range(0,nomstock)])
    ownnot = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    ownnot = pd.DataFrame.fillna(ownnot,0)
    bsevent = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    bsevent = pd.DataFrame.fillna(bsevent,0)
    anyowned = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,y)])
    anyowned = pd.DataFrame.fillna(anyowned,0)
    cashtotal = pd.DataFrame([[mon]],index=[range(0,nomdays)])
    cashavail = pd.DataFrame([[mon]],index=[range(0,nomdays)])
    investedcash = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    investedcash = pd.DataFrame.fillna(investedcash,0)
    daysowned = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    daysowned = pd.DataFrame.fillna(daysowned,0)
    nomshares = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    nomshares = pd.DataFrame.fillna(nomshares,0)

    
    shortmean, shortstd, buysell = buysellfunc(closeprice,q,t,buysell,nomstock)
    buyorder = rankfunc(buysell)
    
    for i in range(r,nomdays):
        
        #Create a list of the buy order preference to be used in buyfunc()
        #Needs improvement
        prefbuy = list(buyorder.ix[i])
        
        #Buying
        ownnot,anyowned,bsevent = buyfunc(i,y,nomstock,nomdays,prefbuy,ownnot,anyowned,bsevent,shortstd,closeprice)
        
        #selling
        ownnot,anyowned,bsevent = sellfunc(i,nomstock,nomdays,ownnot,anyowned,bsevent,shortmean,closeprice)
        
        #populates daysowned (Currently not used. See daysfunc() comments.
        #daysowned = daysfunc(i,daysowned,bsevent,nomstock)
        
        #calculate money
        nomshares,cashtotal,cashavail,investedcash = cashfunc(i,y,nomstock,nomdays,cashtotal,cashavail,investedcash,bsevent,anyowned,nomshares,openprice,closeprice)
        
    #Function returns the final portfolio total value
    return cashtotal.ix[nomdays,0]

    
#Example function run:
# optimport(openprices,closeprices,4,51,50,10,10000)



#This function calculates how much you would have at the end of the defined period 
#if the starting money was evenly split over all the stocks in the list
#I mean for this to be a benchmark that mimics how an ETF works
def benchmark(openprice,closeprice,startdate,mon):
    nomdays = len(openprice)
    nomstock = len(openprice.columns)
    investedcash = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    investedcash = pd.DataFrame.fillna(investedcash,0)
    nomshares = pd.DataFrame(index=[range(0,nomdays)],columns=[range(0,nomstock)])
    nomshares = pd.DataFrame.fillna(nomshares,0)

    startinvestment = mon / nomstock
    
    for n in range(0,nomstock):
        #Sets the # of shares bought in nomshares and sets the cost of investment at open for that # of shares in investedcash
        nomshares.ix[range(startdate,nomdays),n] = startinvestment / openprice.ix[startdate,n] 

    for i in range(startdate,nomdays):
        investedcash.ix[i] = np.array(nomshares.ix[i]) * np.array(closeprice.ix[i])
            
    return investedcash.ix[nomdays-1].sum()






####From here down are testing functions###



#This function does a (sort of) bootstrap sampled testing of the main model
#It creates 'models' number of tests, with 'boots' number of randomly selected stocks from your list without replacement
#All the other variables are the same as optimport()
#It outputs a CSV with the test in the first column and the benchmark using those same stocks in the second column
#Be sure to insert your save directory for the file
def bootopt(boots,models,openprice,closeprice,y,r,t,q,mon):
    resultlist = np.array([[0,0,0]])
    for i in range(0,models):
        sample = list(np.random.choice(range(0,len(openprice.columns)),boots,replace=False))
        result = optimport(openprice.ix[:,sample],closeprice.ix[:,sample],y,r,t,q,mon)
        bench = benchmark(openprice.ix[:,sample],closeprice.ix[:,sample],r,mon)
        comparison = result - bench
        resultlist = np.append(resultlist,[[result,bench,comparison]],axis=0)
    #Insert your save to directory here
    np.savetxt('\\bootresult.csv',resultlist,delimiter=",")






#I used this to play around with optimizing the moving average number of days
#t1 and t2 are the ranges of the long moving average
#and q1 and q2 are the ranges of the short moving averages to be tested
def movingopt(openprice,closeprice,y,r,t1,t2,q1,q2,mon):
    resultlist = np.array([[0,0,0]])
    for i in range(t1,t2):
        for n in range(q1,q2):
            result = optimport(openprice,closeprice,y,r,i,n,mon)
            resultlist = np.append(resultlist,[[i,n,result]],axis=0)
    np.savetxt('\\simresult.csv',resultlist,delimiter=",")
    #print resultlist

#I used this to play around with optimizing the number of splits in the portfolio
#with y1 and y2 the range of the number of splits to be testsed    
def sizeopt(openprice,closeprice,y1,y2,r,t,q,mon):
    resultlist = np.array([[0,0]])
    for i in range(y1,y2):
        result = optimport(openprice,closeprice,i,r,t,q,mon)
        resultlist = np.append(resultlist,[[i,result]],axis=0)
    np.savetxt('\\sizeresult.csv',resultlist,delimiter=",")

#A combination of the previous two functions.
#This can take a long time to run if you put big ranges to be tested     
def bigopt(openprice,closeprice,y1,y2,r,t1,t2,q1,q2,mon):
    resultlist = np.array([[0,0,0,0]])
    for i in range(t1,t2,5):
        for n in range(q1,q2):
            for y in range(y1,y2):
                result = optimport(openprice,closeprice,y,r,i,n,mon)
                resultlist = np.append(resultlist,[[y,i,n,result]],axis=0)
    np.savetxt('C:\Users\Thomas\Desktop\\bigsimresult3.csv',resultlist,delimiter=",")
