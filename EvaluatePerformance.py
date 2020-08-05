# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd

def EvaluatePerformance():
    
    # Set file path
    rootPath = os.getcwd()
    path_stockRecord = os.path.join(rootPath, "data", "UserDefine", "StockRecord.xlsx")
    path_stockSummary = os.path.join(rootPath, "data", "StockSummary.xlsx")
    path_todayPrice = os.path.join(rootPath, "data", "TodayPrice.xlsx")
    
    # Read transaction record
    stockRecord = pd.read_excel(path_stockRecord, dtype=str, sheet_name = "Record")
    stockRecord["Date"] = stockRecord["Date"].apply(lambda x: x.split(" ")[0])
    
    stockRecord = stockRecord.astype({"Price": float, "Amount": int})
    
    stockList = pd.unique(stockRecord["Stock"])
    stockReturnSummary = pd.DataFrame(
            columns=["Stock", "HoldAmount", "BuyAvgPrice", "SellAmount", "SellAvgPrice", "SellReturn"])
    
    # Read latest price information
    # latestPrice = pd.read_excel(path_todayPrice, dtype=str)

    for idx,stock in enumerate(stockList):

        stockRecord_select = stockRecord[stockRecord["Stock"]==stock]
        buy_Record = stockRecord_select[stockRecord_select["Buy"]=="True"]
        sell_Record = stockRecord_select[stockRecord_select["Buy"]!="True"]
    
        buyCost = np.sum(buy_Record["Price"] * buy_Record["Amount"] + 20)
        sellReturn = np.sum(sell_Record["Price"] * sell_Record["Amount"] * (1-0.003) - 20)
        holdAmount = np.sum(buy_Record["Amount"]) - np.sum(sell_Record["Amount"])
        
        BuyAvgPrice = (buyCost-sellReturn)/holdAmount if holdAmount!=0 else 0
        BuyAvgPrice = round(BuyAvgPrice,2)
        
        sellAmount = np.sum(sell_Record["Amount"])
        sellAvgPrice = sellReturn / sellAmount if sellAmount!=0 else 0

        stockReturnSummary.loc[idx] = [stock, holdAmount, BuyAvgPrice, sellAmount, sellAvgPrice, round(sellReturn)]
    
    
    stockReturnSummary.to_excel(path_stockSummary, index=False)

    
if __name__ == '__main__':
    EvaluatePerformance()
    
    
    