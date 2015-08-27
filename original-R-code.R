#Copywrite 2015 Thomas Cantrell
#For more information, see torchdata.com

#Run all libraries and functions. Then run the functions starting on line 230. 

library(tseries)#cool
library(zoo)


#Function to import daily stock price
wp <- function(x) {
  quote <- get.hist.quote(x, start = "2011-02-06", end = "2015-02-05", quote="Close", provider = "yahoo",  compression = "d")
  quote <- na.locf(quote)
  
  df <- as.data.frame(quote)
  colnames(df) <- c(x)
  return(df)
}

#Function to import end of day percent change
wr <- function(x) {
  y <- as.matrix(x)
  df <- as.data.frame(diff(log(y)))
  colnames(df) <- colnames(x)
  return(df)
}

#Function for importing multiple stock prices from Yahoo to one dataframe
combineddaily <- function(x){
  combinedstock <- data.frame(matrix(0, nrow=1005, ncol=length(x)),check.rows=FALSE)
  for(i in 1:length(x)) {
    combinedstock[,i] <- wp(x[i])
  }
  return(combinedstock)}



###Below is the simulation function.

#The description for the imputs to the function:
#daily is the output from the above function wr
#combinedstock is the output from the above function combineddaily
#x is the stock list, y is the number of splits in portfolio (ie, how many possible different stocks owned simultaniously)
#r is how many days into the period does it start, t is rolling average long, q is rolling average short
#mon is the total money invested, sell is the sell multiplyer, buy is the buy multiplyer
optimport <- function(daily,combinedstock,y,r,t,q,mon,sell,buy){
  
  
  nomdays <- dim(daily)[1]
  nomstock <- length(combinedstock)

  #buysell keeps track of when my model thinks is a possible time to buy or sell for all stocks
  buysell <- data.frame(matrix(0, nrow=nomdays, ncol=nomstock))
  #ownnot has 1s for all days that a stock is held
  ownnot <- data.frame(matrix(0, nrow=nomdays, ncol=nomstock))
  #bsevent keeps track of the points buys and sells occur with 1 and -1
  bsevent <- data.frame(matrix(0, nrow=nomdays, ncol=nomstock))
  #anyowned keeps track of if partitions of portfolio are being used or not
  anyowned <- data.frame(matrix(0, nrow=nomdays, ncol=y))
  #buyorder keeps track of the ranking for which stock should be bought each day
  buyorder <- data.frame(matrix(0,nrow=nomdays,ncol=nomstock))
  #cashtotal keeps track of the total value of the portfolio each day
  cashtotal <- data.frame(matrix(mon,nrow=nomdays,ncol=1))
  #cashavail keeps track of how much onhand cash is available
  cashavail <- data.frame(matrix(mon,nrow=nomdays,ncol=1))
  #cashgained keeps tracked of cash from liquidations each day
  cashgained <- data.frame(matrix(0,nrow=nomdays,ncol=1))
  #investedcash keeps track of much money is in each stock
  investedcash <- data.frame(matrix(0, nrow=nomdays, ncol=nomstock))
  #daysowned records the number of days a stock is owned everyday
  daysowned <- data.frame(matrix(0, nrow=nomdays, ncol=nomstock))
  
  
  #Populate the returns list
  
  for(i in r:nomdays) {
    
    avglong <- i - t
    avgshort <- i - q
    
    #Populate rolling average list of potential buys/sells
    for(n in 1:nomstock) {
      
      
      #Populate potential sells with multiplier of (sell)
      if(mean(daily[avgshort:i,n]) >= abs(mean(daily[avglong:i,n])) * sell){
        buysell[i,n] <- -1
      }
      #Populate potential buys with multiplier of (buy)
      else if(mean(daily[avgshort:i,n]) <= mean(daily[avglong:i,n]) * buy) {
        buysell[i,n] <- 1
      }
      
      else {buysell[i,n] <- 0}
      
      
      #Ranks order of buying preferance in dataframe buyorder (The lower the better)
      buyorder[i,n] <- (mean(daily[avgshort:i,n]) / abs(mean(daily[avglong:i,n])))
    }
    
    #Buying
    for(n in 1:y){
      
      #Finds how many need purchased
      nompurchase <- y - sum(anyowned[i,]) 
      
      if(nompurchase >= 1){ #If there is room for more stock to be bought
        
        #Finds column # of stock not owned
        possiblebuys <- which(ownnot[i,] %in% 0)
        #Finds stocks that meets the buy threshold
        canbuys <- which(buysell[i,] %in% 1)
        #Finds stocks that are both not owned and meet threshold
        buyable <- intersect(possiblebuys,canbuys)
        #Finds the column number of the optimum purchases on that day, in order
        bestbuy <- order(buyorder[i,])[1:nomstock]
        #Puts the buyables in bestbuy order
        buylist <- intersect(bestbuy,buyable)
        #buylist <- intersect(intersect(bestbuy,possiblebuys),canbuys)
        #Stops errors by putting 0 at end in case of no matches
        buylist <- append(buylist,-3)
        #Defines most desireable stock reference
        buyit <- buylist[1]
        
        #buying <- append(buying,buyit)
        #possiblebuying[i,] <- possiblebuys
        
        if(buyit >= 0){
          
          ownnot[i:nomdays,buyit] <- 1
          bsevent[i,buyit] <- 1
          
          #Finds the column # of funds not used and changes its value to 1
          possiblecolb <- match(0,anyowned[i,])  
          anyowned[i:nomdays,possiblecolb] <- 1
        }
      }
    } 
    
    #Selling
    
    #Populates daysowned
    for(n in 1:nomstock) {
      
      if(daysowned[i-1,n] >= 1){
        daysowned[i,n] <- daysowned[i-1,n] + 1
      }
      if(bsevent[i,n] == 1){
        daysowned[i,n] <- 1
      } 
      if(bsevent[i,n] == -1){
        daysowned[i,n] <- 0
      }
    }
    
    
    for(n in 1:y){
      
      #Finds how many can be sold
      nomcansell <- sum(anyowned[i,]) 
      
      if(nomcansell != 0){ #If there is stock to sell
        
        #Finds column # of stock owned
        possiblesells <- which(ownnot[i,] %in% 1)
        #Finds stocks that meets the sell threshold
        cansells <- which(buysell[i,] %in% -1)
        #Finds stocks that are both not owned and meet threshold
        sellable <- intersect(possiblesells,cansells)
        #Stops errors by putting 0 at end in case of no matches
        selllist <- append(sellable,0)
        #Defines stock to be sold
        sellit <- selllist[1]
        
        if(sellit>=1){
          
          ownnot[i:nomdays,sellit] <- 0
          bsevent[i,buyit] <- -1
          
          #Finds the column # of funds used and changes its value to 0
          possiblecol <- match(1,anyowned[i,])  
          anyowned[i:nomdays,possiblecol] <- 0
        }
      }
    }
    
    #Calculating money
    buyamount <- (1/y) * cashtotal[i,1]
    for(n in 1:nomstock) {
      
      #Calculates daily returns and inserts them into investedcash
      investedcash[i,n] <- (investedcash[i-1,n] * combinedstock[i,n]) + investedcash[i-1,n]
      
      #Applies the invested amount to investedcash on buy (This assumes stock is bought at beginning of day)
      buypoints <- match(1, bsevent[i,n], nomatch=0)
      if(buypoints >= 1) {investedcash[i,n] <- (buyamount * combinedstock[i,n]) + buyamount}
      
      #Removes cash from investedcash on sell and adds to cash avail
      sellpoints <- match(-1, bsevent[i,n], nomatch=0)
      if(sellpoints >= 1) {
        cashgained[i,1] <- cashgained[i,1] + investedcash[i,n]
        investedcash[i,n] <- 0
      }
      
      
    }  
    
    #Subtracts investment from cashavail for each day's purchases
    buynum <- which(bsevent[i,] %in% 1)
    investedamount <- length(buynum) * buyamount
    cashavail[i,1] <- cashavail[i-1,1] - investedamount
    
    #Adds liquidation amount from each day's sells
    cashavail[i,1] <- cashavail[i,1] + cashgained[i,1]
    
    #Keeps track of total portfolio value
    cashtotal[i,1] <- cashavail[i,1] + sum(investedcash[i,])
    
    
  }  
  

  return(cashtotal)

}




#Creates data frame of daily stock prices from the input ticker symbols
#The more tickers input, the longer the simulation takes to run
prices <- combineddaily(c("MMM","ABT","ACE","ACN","ACT","AES","AET","AFL","AMG","A","GAS","APD","ARG","AKAM","AA","ALXN")
#Creates data frame of daily returns
returns <- wr(prices)

#Create a list of daily balance based on model
#Order of inputs: price list, returns list, portfolio splits, start day, long avg, short avg, start value, sell multiplier, buy multiplier.
#The output is the total value of the whole portfolio on a day-by-day basis.
check <- optimport(prices,returns,8,210,200,4,10000,1.31,.945)
check
