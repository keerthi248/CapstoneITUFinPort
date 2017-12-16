import json
#import argparse
import requests
from lxml import html  
from collections import OrderedDict
from datetime import datetime
from pytz import timezone
import time
#from lxml import etree
#from pprint import pprint

start = time.time()
######## Getting the ticker symbols from Web API#############
r = requests.get("http://52.226.130.180/FinancePortfolioAPI/api/TickerSymbol/GetAllTickerSymbols")
data_file = r.text
#print (data_file)```````````
data = json.loads(data_file)
#print (data)

###########Start-- convert ticker symbols json to a list of ticker symbols################
#Extracting the ticker symbols and saving it as a list
TickList = []
SummaryList = []
Output = OrderedDict()

for dict in data:
    #print (dict)
    for x,y in dict.items():
        #print (x,y)
        if x == "ticker":
            #print (y)
            TickList.append(y)  
length = len(TickList)
print ("Data for", length, " ticker symbols to be fetched from Yahoo! Finance" )
Output.update({'Tickers':length})
###########End-- convert ticker symbols json to a list of ticker symbols

###########Start-- method to convert time stamp parameters to proper time
def TimeConversion(a):
    timestamp = a
    dt_obj = datetime.utcfromtimestamp(timestamp)
    DateStr1 = str(dt_obj)
    #print (DateStr1)
    gmt = timezone('GMT')
    eastern = timezone('US/Eastern')
    date = datetime.strptime(DateStr1, '%Y-%m-%d %H:%M:%S')
    dategmt = gmt.localize(date)
    dateeastern = dategmt.astimezone(eastern)
    #print (dateeastern)
    DateStr2 = str(dateeastern)
    #print (DateStr2)
    List1 = DateStr2.strip("").split(" ")
    #print (List1)
    #DateObj = List1[0]
    TimeObj1 = List1[1].strip("").split("-")
    TimeObj2 = TimeObj1[0]
    #print (DateObj)
    #print (TimeObj2)

    d = datetime.strptime(TimeObj2, "%H:%M:%S")
    DisplayTime = str(d.strftime("%I:%M%p") + " " + "EDT")
    if DisplayTime.startswith("0"):
        DisplayTime = DisplayTime[1:]
        
    return(DisplayTime)
###########End-- method to convert time stamp parameters to proper time
  
###########Start-- Looping tickers list to to fetch quote data and convert to Json
for idx,tick in enumerate(TickList):
    try:
        ############Build the Url with ticker symbol
        print (idx,": ", tick)
        Output.update({idx:tick})
        url = "http://finance.yahoo.com/quote/%s?p=%s"%(tick,tick) #URL for the website, ticker is passed as argument
        headers = {'Accept-Encoding': 'deflate'}
        response = requests.get(url) #Requests will add strings and format the URL
        #print ("Parsing %s"%(url)) # Printing url for ticker
        Parser = html.fromstring(response.text) #response.text will have all the html content for URL built from requests
        #print (response.text)
        
        ###########Getting summary table from parser response
        #QuoteHeader = Parser.xpath('//div[contains(@data-test,"quote-header")]//tr')
        #print (QuoteHeader)
        SummaryTable = Parser.xpath('//div[contains(@data-test,"summary-table")]//tr')
        #print (SummaryTable)
        
        ########### Getting header and other details from query2 urls
        QuoteHeaderjsonLink = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&crumb=F3spv1P9A49&lang=en-US&region=US&modules=price%2CsummaryDetail&corsDomain=finance.yahoo.com".format(tick)
        QuotejsonResponse = requests.get(QuoteHeaderjsonLink)
        #print (QuotejsonResponse.text)
        LoadedjsonQuote = json.loads(QuotejsonResponse.text)
        #print (LoadedjsonQuote)
        '''
        SummaryDetailsjsonLink = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com".format(tick)
        SummaryjsonResponse = requests.get(SummaryDetailsjsonLink)
        #print (SummaryjsonResponse.text)
        LoadedjsonSummary =  json.loads(SummaryjsonResponse.text)
        #print (LoadedjsonSummary)
        '''
        ########## Extracting the values , populating to right params and building the response json
        SummaryData = OrderedDict() 
        if not LoadedjsonQuote["quoteSummary"]["result"]  :
            errorDesc = LoadedjsonQuote["quoteSummary"]["error"]['description']
            SummaryData.update({'Error Description':errorDesc, 'Ticker':tick})
    
            print (idx,":", errorDesc)
        else:
            '''
            for quote_data in quote_header:
                raw_table_key = quote_data.xpath('.//td[contains(@class,"C(black)")]//text()')
                raw_table_value = quote_data.xpath('.//td[contains(@class,"Ta(end)")]//text()')
                print (raw_table_key)
                print (raw_table_value)
            
            max_Age = " "   
            if "maxAge" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["maxAge"] == "":
                    max_Age = " "
                else:
                    max_Age = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["maxAge"]
            #print (max_Age)
            pre_MarketChange = " "
            if "preMarketChange" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["preMarketChange"] == {} :
                    pre_MarketChange = " "
                else:
                    pre_MarketChange = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["preMarketChange"]["fmt"]
            #print (pre_MarketChange)
            pre_MarketPrice = " "
            if "preMarketPrice" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["preMarketPrice"] == {} :
                    pre_MarketPrice = " "
                else:
                    pre_MarketPrice = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["preMarketPrice"]["fmt"]
            #print (pre_MarketPrice)
            pre_MarketSource = " "
            if "preMarketSource" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["preMarketSource"] == "" :
                    pre_MarketSource = " "
                else:
                    pre_MarketSource = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["preMarketSource"]
            #print (pre_MarketSource)
            pre_MarketTime = " "
            if "preMarketTime" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["preMarketTime"] == "" :
                    pre_MarketTime = " "
                else:
                    pre_MarketTime = TimeConversion(LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["preMarketTime"])
            #print (pre_MarketTime)
            post_MarketChange_Percent = " "
            if "postMarketChangePercent" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["postMarketChangePercent"] == {} :
                    post_MarketChange_Percent = " "
                else:
                    post_MarketChange_Percent = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["postMarketChangePercent"]["fmt"]
            #print (post_MarketChange_Percent)
            post_MarketChange = " "        
            if "postMarketChange" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["postMarketChange"] == {} :
                    post_MarketChange = " "
                else:
                    post_MarketChange = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["postMarketChange"]["fmt"]
            #print (post_MarketChange)
            post_MarketTime = " "
            if "postMarketTime" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["postMarketTime"] == "" :
                    post_MarketTime = " "
                else:
                    post_MarketTime = TimeConversion(LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["postMarketTime"])
            #print (post_MarketTime)
            post_MarketPrice = " "
            if "postMarketPrice" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["postMarketPrice"] == {} :
                    post_MarketPrice = " "
                else:
                    post_MarketPrice = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["postMarketPrice"]["fmt"]
            #print (post_MarketPrice)
            post_MarketSource = " "
            if "postMarketSource" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["postMarketSource"] == "" :
                    post_MarketSource = " "
                else:
                    post_MarketSource = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["postMarketSource"]
            #print (post_MarketSource)
            '''
            regular_MarketChange_Percent = " "
            if "regularMarketChangePercent" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["regularMarketChangePercent"] == {} :
                    regular_MarketChange_Percent = " "
                else:
                    regular_MarketChange_Percent = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["regularMarketChangePercent"]["fmt"]
            #print (regular_MarketChange_Percent)
            regular_MarketChange = " "  
            if "regularMarketChange" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["regularMarketChange"] == {} :
                    regular_MarketChange = " "
                else:
                    regular_MarketChange = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["regularMarketChange"]["fmt"]
            #print (regular_MarketChange)
            regular_MarketTime = " "        
            if "regularMarketTime" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["regularMarketTime"] == "" :
                    regular_MarketTime = " "
                else:
                    regular_MarketTime = TimeConversion(LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["regularMarketTime"])
            #print (regular_MarketTime)
            regular_MarketPrice = " "
            if "regularMarketPrice" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["regularMarketPrice"] == {} :
                    regular_MarketPrice = " "
                else:
                    regular_MarketPrice = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["regularMarketPrice"]["fmt"]
            #print (regular_MarketPrice)
            '''
            regular_MarketSource = " "
            if "regularMarketSource" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["regularMarketSource"] == "" :
                    regular_MarketSource = " "
                else:
                    regular_MarketSource = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["regularMarketSource"]
            #print (regular_MarketSource)
            exchange = " "
            if "exchange" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["exchange"] == "" :
                    exchange = " "
                else:
                    exchange = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["exchange"]
            #print (exchange)
            exchange_Name = " "
            if "exchangeName" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["exchangeName"] == "" :
                    exchange_Name = " "
                else:
                    exchange_Name = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["exchangeName"]
            #print (exchange_Name)
            market_State = " "
            if "marketState" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["marketState"] == "" :
                    market_State = " "
                else:
                    market_State = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["marketState"]
            #print (market_State)
            quote_Type = " "
            if "quoteType" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["quoteType"] == "" :
                    quote_Type = " "
                else:
                    quote_Type = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["quoteType"]
            #print (quote_Type)
            '''
            short_Name = " "
            if "shortName" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["shortName"] == "" :
                    short_Name = " "
                else:
                    short_Name = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["shortName"]
            #print (short_Name)
            long_Name = " "
            if "longName" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["longName"] == "" :
                    long_Name = " "
                else:
                    long_Name = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["longName"]
            #print (long_Name)
            '''
            currency = " "
            if "currency" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["currency"] == "" :
                    currency = " "
                else:
                    currency = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["currency"]
            #print (currency)
            quote_SourceName = " "
            if "quoteSourceName" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["quoteSourceName"] == "" :
                    quote_SourceName = " "
                else:
                    quote_SourceName = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["quoteSourceName"]
            #print (quote_SourceName)
            currency_Symbol = " "
            if "currencySymbol" in LoadedjsonQuote["quoteSummary"]["result"][0]["price"]:
                if LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["currencySymbol"] == "" :
                    currency_Symbol = " "
                else:
                    currency_Symbol = LoadedjsonQuote["quoteSummary"]["result"][0]["price"]["currencySymbol"]
            #print (currency_Symbol)
            
            SummaryData.update({'maxAge':max_Age,'preMarketChange':pre_MarketChange, 'preMarketPrice':pre_MarketPrice,'preMarketSource':pre_MarketSource,'preMarketTime':pre_MarketTime,'PostMarketChangePercent':post_MarketChange_Percent,'PostMarketChange':post_MarketChange,
        	'postMarketTime':post_MarketTime, 'postMarketPrice':post_MarketPrice,'postMarketSource':post_MarketSource,'RegularMarketChangePercent': regular_MarketChange_Percent,'RegularMarketChange': regular_MarketChange,'regularMarketTime':regular_MarketTime,'regularMarketPrice':regular_MarketPrice,
        	'regularMarketSource':regular_MarketSource,'exchange':exchange,'exchangeName':exchange_Name,'marketState':market_State,'quoteType':quote_Type,'shortName':short_Name,
        	'longName':long_Name,'currency':currency,'quoteSourceName':quote_SourceName, 'currencySymbol':currency_Symbol,'ticker':tick,'url':url})
            '''
            SummaryData.update({'RegularMarketChangePercent': regular_MarketChange_Percent,'RegularMarketChange': regular_MarketChange,'regularMarketTime':regular_MarketTime,'regularMarketPrice':regular_MarketPrice,
        	'shortName':short_Name,'longName':long_Name,'ticker':tick,'url':url})
            
            '''
            if not LoadedjsonSummary["quoteSummary"]["result"]  :
                errorDescSummary = LoadedjsonSummary["quoteSummary"]["error"]['description']
                SummaryData.update({'Error Description':errorDescSummary, 'Ticker':tick})
                print (errorDescSummary)
            else:
                
                if "financialData" in LoadedjsonSummary["quoteSummary"]["result"]:
    
                    if "targetMeanPrice" in LoadedjsonSummary["quoteSummary"]["result"][0]["financialData"]:
                        if LoadedjsonSummary["quoteSummary"]["result"][0]["financialData"]["targetMeanPrice"] == {}:
                            y_Target_Est = "N/A"
                        else:
                            y_Target_Est = LoadedjsonSummary["quoteSummary"]["result"][0]["financialData"]["targetMeanPrice"]['raw']
                        #print (y_Target_Est)
                else:
                     y_Target_Est = "N/A"
                    
                datelist = []
                earnings_date = "N/A"
            
                if "calendarEvents" in LoadedjsonSummary["quoteSummary"]["result"][0]:
                        earnings_list = LoadedjsonSummary["quoteSummary"]["result"][0]["calendarEvents"]['earnings']
                              
                        for i in earnings_list['earningsDate']:
                                if earnings_list['earningsDate'] == {}:
                                    earnings_date == "N/A"
                                else:
                                    datelist.append(i['fmt'])
                                    earnings_date = ' to '.join(datelist)
                else:
                        earnings_date = "N/A"
            
                #print (earnings_list)
                
                if "defaultKeyStatistics" in LoadedjsonSummary["quoteSummary"]["result"][0]:
                    if "trailingEps" in LoadedjsonSummary["quoteSummary"]["result"][0]["defaultKeyStatistics"]:
                        if LoadedjsonSummary["quoteSummary"]["result"][0]["defaultKeyStatistics"]["trailingEps"] == {}:
                            eps = "N/A"
                        else:
                            eps = LoadedjsonSummary["quoteSummary"]["result"][0]["defaultKeyStatistics"]["trailingEps"]['raw']
                else:
                    eps = "N/A"
                #print (eps)
                           
                '''        
            for table_data in SummaryTable:
                raw_table_key = table_data.xpath('.//td[contains(@class,"C(black)")]//text()')
                raw_table_value = table_data.xpath('.//td[contains(@class,"Ta(end)")]//text()')
                table_key = ''.join(raw_table_key).strip()
                table_value = ''.join(raw_table_value).strip()
                SummaryData.update({table_key:table_value})
            #SummaryData.update({'1y Target Est':y_Target_Est,'EPS (TTM)':eps,'Earnings Date':earnings_date,'ticker':tick,'url':url})
            #print (SummaryData)
            SummaryList.append(SummaryData)    
    except:
        pass
#print (SummaryList)
#print ("Writing data to output file")

###########End-- Looping tickers list to to fetch quote data and convert to Json

###########start- save to file
moment=time.strftime("%Y-%b-%d__%H_%M_%S",time.localtime())
with open('C:\\ParserOutput\\Quote_'+moment+'.json','w') as SummaryFile:
     json.dump(SummaryList,SummaryFile,indent = 4)
with open('C:\\ParserOutput\\Quote_'+moment+'.json','r') as SummaryFile:
     SummaryText = SummaryFile.read()
    # SummaryText = SummaryText.replace("[", "")
    # SummaryText = SummaryText.replace("]", "")
    # SummaryText = "\n".join([i.rstrip() for i in SummaryText.splitlines() if i.strip()])
#print (SummaryText)
with open('C:\\ParserOutput\\Quote_'+moment+'.json','w') as SummaryFile:
    SummaryFile.write(SummaryText) 
    
###########end- save to file

##########start -post to web api
try:
    url = 'http://52.226.130.180/FinancePortfolioAPI/api/TickerSymbol/InsertUpdateTickerSymbols'
    headers = {'Authorization' : '(some auth code)', 'Accept' : 'application/json', 'Content-Type' : 'application/json'}
    response = requests.post(url, data = SummaryText, headers=headers)
    code = response.status_code
    if code == 204:
        print("Successfully posted data on server :", response.status_code )
        Output.update({'Successfully posted data on server':response.status_code})
    else:
        if code == 500:
            print("Internal server error :",response.status_code)
            Output.update({'Internal server error':response.status_code})
        else:    
            print(code)
            Output.update({'Response Coder':response.status_code})
except requests.exceptions.Timeout:
    print (response.status_code, "Timeout")    
except requests.exceptions.RequestException as e:
    print(response.status_code, e)         
except requests.exceptions.TooManyRedirects:
    print (response.status_code, "TooManyRedirects")
##########end -post to web api

end = time.time()
print("Execution Time in Seconds:" , end - start)
Output.update({'Execution Time in Seconds':end - start})
#print (Output)
with open('C:\\ParserOutput\\Output'+moment+'.json','w') as OutputFile:
     json.dump(Output,OutputFile,indent = 4)