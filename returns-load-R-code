library(tseries)
library(zoo)


#Function to import daily stock price
wp <- function(x) {
  quote <- get.hist.quote(x, start = "2014-07-21", end = "2015-07-20", quote="Close", provider = "yahoo",  compression = "d")
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
#nrow should equal the number of days from wp 
combineddaily <- function(x){
  combinedstock <- data.frame(matrix(0, nrow=217, ncol=length(x)),check.rows=FALSE)
  for(i in 1:length(x)) {
    combinedstock[,i] <- wp(x[i])
  }
  return(combinedstock)}



#Function for importing multiple stock prices from Yahoo to one dataframe
#nrow should equal the number of days from wp 
combineddailyopen <- function(x){
  combinedstock <- data.frame(matrix(0, nrow=217, ncol=length(x)),check.rows=FALSE)
  for(i in 1:length(x)) {
    combinedstock[,i] <- wpopen(x[i])
  }
  return(combinedstock)}



#Example 1: using S&P stocks. This takes the longest since there are so many.
closeprices <- combineddaily(sandp[,2])
openprices <- combineddailyopen(sandp[,2])
returns <- wr(closeprices)
write.csv(closeprices,'closeprices.csv')
write.csv(openprices,'openprices.csv')
write.csv(returns,'returns.csv')


#Example 2: using a smaller subset of stocks.
closeprices1 <- combineddaily(c("MMM","ABT","ACE","ACN","ACT","AES","AET","AFL","AMG","A","GAS","APD","ARG","AKAM","AA","ALXN"))
openprices1 <- combineddailyopen(c("MMM","ABT","ACE","ACN","ACT","AES","AET","AFL","AMG","A","GAS","APD","ARG","AKAM","AA","ALXN"))
returns1 <- wr(closeprices1)
write.csv(closeprices1,'closeprices.csv1')
write.csv(openprices1,'openprices.csv1')
write.csv(returns1,'returns.csv1')
