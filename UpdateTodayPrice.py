
import os
import requests
from datetime import date, timedelta
from io import StringIO

import numpy as np
import pandas as pd

def GetStockInfo(date, stock_list):

    ### TSE ### 
    # Download stock information
    url = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={}&type=ALL'.format(date)
    r = requests.post(url)

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
    # select_df.reset_index(drop=True, inplace=True)

    ### OTC ### 
    # Download stock information
    url = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d={}'.format(date)
    page = requests.get(url)
    result = page.json()

    for table in [result['mmData'], result['aaData']]:
        for tr in table:
            if tr[0] in stock_list:
                tr = np.array(tr)
                select_col_idx = [0,1,4,2]
                tr = tr[select_col_idx]
                tr = tr.reshape(1,4)
                tr = pd.DataFrame(data=tr, columns=preserve_col)
                select_df = select_df.append(tr)

    select_df.reset_index(drop=True, inplace=True)
    
    return select_df

def UpdateStockListByRecord(path_stockRecord, path_stockList, update=True):

    stockRecord = pd.read_excel(path_stockRecord, dtype=str, sheet_name = "Record")
    stockList_bought = pd.unique(stockRecord["Stock"])

    with open(path_stockList, 'r') as fObj:
        stock_list = fObj.readlines()
    stock_list = [elem.replace('\n', '') for elem in stock_list]

    for stock_b in  stockList_bought:
        if stock_b not in stock_list:
            stock_list.append(stock_b)

    if update:
        with open(path_stockList, 'w') as fObj:
            for elem in stock_list:
                fObj.writelines(elem + "\n")

    return stock_list
    
    
def UpdateTodayPrice(outFName = "TodayPrice.xlsx"):
    
    print("\n[Update Today Price]")
    # Get select stock list
    print("Get stock information ...")
    rootPath = os.getcwd()
    out_dir = os.path.join(rootPath, "data")
    path_stockRecord = os.path.join(rootPath, "data", "UserDefine", "StockRecord.xlsx")
    path_stockList = os.path.join(rootPath, "data", "UserDefine", "stock_list.txt")

    # Read Stock List (After Update Stock List By Record)
    stock_list = UpdateStockListByRecord(path_stockRecord, path_stockList)
    
    # Get date today
    today = date.today()
    while True:
        today_str = today.strftime("%Y%m%d")
        try:
            df_today = GetStockInfo(today_str, stock_list)
            print("[Today] Update {} price".format(today_str))
            break
        except:
            print("[Today] {} is a holiday. The stock market don't open.".format(today_str))
            today = today - timedelta(days=1)

    yesterday = today - timedelta(days=1)
    while True:
        yesterday_str = yesterday.strftime("%Y%m%d")
        try:
            df_yesterday = GetStockInfo(yesterday_str, stock_list)
            print("[Yesterday] Update {} price".format(yesterday_str))
            break
        except:
            print("[Yesterday] {} is a holiday. The stock market don't open.".format(yesterday_str))
            yesterday = yesterday - timedelta(days=1)

    # Calculate price change
    print("Write data to \"{}\"".format(os.path.join(out_dir, outFName)))
    price_today = np.array(df_today.iloc[:,-1]).astype(float)
    price_yesterday = np.array(df_yesterday.iloc[:,-1]).astype(float)
    df_today["漲跌"] = np.round((price_today-price_yesterday)/price_yesterday*100,2)
    
    # Output as csv file
#    df_today.iloc[:,0] =  df_today.iloc[:,0].apply(lambda x: 's'+x)
    os.makedirs(out_dir, exist_ok=True)
    df_today.to_excel(os.path.join(out_dir, outFName),
                     index=False,
                     encoding="utf_8_sig")

    print("Done")

if __name__ == '__main__':
    UpdateTodayPrice()
    





