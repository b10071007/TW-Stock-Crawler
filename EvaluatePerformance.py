# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd

def EvaluatePerformance():
    
    print("[Evaluate Performance]")
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
            columns=["股票代號", "股票名稱", "持有股份", "買入均價", 
                     "市場價格", "賣出股份", "賣出均價", "賣出金額", 
                     "持倉總成本", "持倉總價值", "未實現損益", "已實現總損益", "總損益", "總損益率"])
    
    # Read latest price information
    latestPrice = pd.read_excel(path_todayPrice, dtype=str)

    totalValue = 0
    totalCost = 0
    totalHoldProfit = 0
    totalRealizedProfit = 0
    for idx, stock in enumerate(stockList):

        # Get stock information
        stockRecord_select = stockRecord[stockRecord["Stock"]==stock]
        buy_Record = stockRecord_select[stockRecord_select["Buy"]=="True"]
        sell_Record = stockRecord_select[stockRecord_select["Buy"]!="True"]
        
        # Basic measure
        totalBuyAmount = np.sum(buy_Record["Amount"])
        totalBuyValue = np.sum(buy_Record["Price"] * buy_Record["Amount"] + 20)
        totalSellAmount = np.sum(sell_Record["Amount"])
        totalSellValue = np.sum(sell_Record["Price"] * sell_Record["Amount"] * (1-0.003) - 20)
        holdAmount = np.sum(buy_Record["Amount"]) - np.sum(sell_Record["Amount"])

        BuyAvgPrice = totalBuyValue / totalBuyAmount
        BuyAvgPrice = round(BuyAvgPrice, 4)

        SellAvgPrice = totalSellValue / totalSellAmount if totalSellAmount>0 else 0
        SellAvgPrice = round(SellAvgPrice, 4)

        # Get latest information
        latestPrice_select = latestPrice[latestPrice["證券代號"]==stock]
        name_select = str( latestPrice_select.iloc[0,1] )
        price_select = float( latestPrice_select.iloc[0,-2] )
        latestValue = int( price_select * holdAmount )

        # holdCost and Unrealized profit
        # (保本價)
        # holdCost = (totalBuyValue - totalSellValue)/ holdAmount if holdAmount>0 else 0
        # holdCostValue = holdCost * holdAmount

        # holdProfit = (price_select - holdCost) * holdAmount
        # holdProfitRatio = holdProfit / (latestValue-holdProfit) * 100 if holdAmount>0 else 0
        # holdProfitRatio = round(holdProfitRatio,2)

        # (持倉成本)
        holdCost = BuyAvgPrice
        holdCostValue = int( BuyAvgPrice * holdAmount )
        holdProfit = int( (price_select - holdCost) * holdAmount )
        
        # Realized Profit
        if (totalSellValue!=0):
            realizedProfit = int( totalSellValue - (BuyAvgPrice * totalSellAmount) )
        else:
            realizedProfit = 0

        profit = holdProfit + realizedProfit
        profitRate = str( round(profit / totalBuyValue * 100, 1) ) + "%"

        totalHoldProfit += holdProfit
        totalRealizedProfit += realizedProfit
        totalValue += latestValue
        totalCost += holdCostValue
        
        # ["股票代號", "股票名稱", "持有股份", "買入均價",
        #  "市場價格", "賣出股份", "賣出均價", "賣出總金額", 
        #  "持倉總成本", "持倉總價值", "未實現損益", "已實現總損益", "總損益", "總損益率"]
        stockReturnSummary.loc[idx] = [
                stock, name_select, holdAmount, BuyAvgPrice,
                price_select, totalSellAmount, SellAvgPrice, totalSellValue, 
                holdCostValue, latestValue, holdProfit, realizedProfit, profit, profitRate]
    
    
    # Calculate Total Value
    UnrealizedProfitRate = (totalValue-totalCost)/totalCost if totalCost!=0 else 0 
    UnrealizedProfitRate = str(round(UnrealizedProfitRate*100, 1)) + "%"

    totalProfit = totalHoldProfit + totalRealizedProfit

    totalProfitRate = totalProfit / totalCost
    totalProfitRate = str(round(totalProfitRate*100, 1)) + "%"
    
    stockReturnSummary.loc[idx+1] = [
            "Total", "-", "-", "-", "-", "-", "-", "-",
            totalCost,  totalValue, totalHoldProfit, totalRealizedProfit, totalProfit, totalProfitRate,
            ]

    # stockReturnSummary.loc[idx+2] = [
    #         "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-",
    #         "Total Value",  totalValue+totalRealizedProfit, totalProfitRate,
    #         ]
    
    stockReturnSummary.to_excel(path_stockSummary, index=False)

    print("Done")

    
if __name__ == '__main__':
    EvaluatePerformance()
    
    
    