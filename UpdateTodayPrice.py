
import os
import requests
from datetime import date, timedelta
from io import StringIO

import numpy as np
import pandas as pd

DEBUG = True

def GetStockInfo(date, stock_list):

    # Download stock information
    r = requests.post('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + date + '&type=ALL')
    
    # Convert data to table
    df = pd.read_csv(StringIO(r.text.replace("=", "")), 
                header=["證券代號" in l for l in r.text.split("\n")].index(True)-1)
    
    preserve_col = df.columns[[0,1,5,8]]
    df = df[preserve_col]
    
    # Get interesting stock
    select_df = pd.DataFrame(columns=preserve_col)  
    for i in range(len(df)):
        if df.iloc[i,0] in stock_list:
            select_df = select_df.append(df.iloc[i])
    select_df.reset_index(drop=True, inplace=True)
    
    return select_df
    
def UpdateTodayPrice():
    
    # Get select stock list
    rootPath = os.getcwd()
    out_dir = os.path.join(rootPath, "data")
    
    with open(os.path.join(rootPath,"stock_list.txt"), 'r') as fObj:
        stock_list = fObj.readlines()
    stock_list = [elem.replace('\n', '') for elem in stock_list]
    
    # Get date today
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    if DEBUG:
        today = "20200717"
        yesterday = "20200716"
        
    else:
        if today.weekday() in [5,6]:
            raise ValueError("Today is a weekend day. The stock market don't open.")
        else:
            today = today.strftime("%Y%m%d")
            yesterday = yesterday.strftime("%Y%m%d")
    
    df_today = GetStockInfo(today, stock_list)
    df_yesterday = GetStockInfo(yesterday, stock_list)
    
    # Calculate price change
    price_today = np.array(df_today.iloc[:,-1]).astype(float)
    price_yesterday = np.array(df_yesterday.iloc[:,-1]).astype(float)
    df_today["漲跌"] = np.round((price_today-price_yesterday)/price_yesterday*100,2)
    
    # Output as csv file
    df_today.iloc[:,0] =  df_today.iloc[:,0].apply(lambda x: 's'+x)
    
    os.makedirs(out_dir, exist_ok=True)
    df_today.to_csv(os.path.join(out_dir, "TodayPrice.csv"),
                     index=False,
                     encoding="utf_8_sig")

if __name__ == '__main__':
    UpdateTodayPrice()
    





