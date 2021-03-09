import os
import sys
import pandas as pd
import numpy as np

from utils.data import ReadStockRecord, ReadDividendRecord
from utils.analysis import StockCalculator

def EvaluateDividend():
    # rootPath = os.getcwd()
    rootPath = "D:/Coding/python/project/TW-Stock-Crawler/"
    path_stockRecord = os.path.join(rootPath, "data", "UserDefine", "StockRecord.xlsx")
    path_dividendRecord = os.path.join(rootPath, "data", "UserDefine", "DividendRecord.xlsx")
    path_dividendSummary = os.path.join(rootPath, "data", "DividendSummary_{}.xlsx")

    
    stockRecord = ReadStockRecord(path_stockRecord)
    dividendRecord, years, stockNames = ReadDividendRecord(path_dividendRecord)
        
    stock_list = list(dividendRecord.keys())
    for year in years:
        dividendSummary_year = pd.DataFrame(
            columns=["股票代號", "股票名稱", "持有股份", "股息", "持倉成本", "殖利率"])
        holdCostValue_Total = 0
        dividend_Total = 0
        for idx, stock in enumerate(stock_list):
            stockRecord_select = stockRecord[stock]
            
            dividendRecord_select = dividendRecord[stock]
            dividendRecord_select = dividendRecord_select[dividendRecord_select['Year'] == year]
            
            ex_dividend_amount = dividendRecord_select['Amount']
            if ex_dividend_amount.isnull().any(): # no that stock
                continue
            ex_dividend_amount = int(dividendRecord_select['Amount'])
            dividend = int(float(dividendRecord_select["Dividend_value"]))
            
            hold_amount = np.cumsum((stockRecord_select['Buy']*2-1) * stockRecord_select['Amount'])
            match_amount = np.array(hold_amount == ex_dividend_amount)
            match_year = np.array([str(elem.year) for elem in stockRecord_select['Date']]) <= year
            
            if np.sum(match_amount * match_year)>1:
                print("Warning: hold cost is probabily wrong (same hold amount in same year)")
                print(" - Stock: {}, Year: {}, Amount: {}".format(stock, year, ex_dividend_amount))
                
            idx_range = np.where(match_amount * match_year)[0][-1]
            stockRecord_select = stockRecord_select[:idx_range+1]
            
            stockCalculate = StockCalculator(stockRecord_select)
            _, holdCostValue = stockCalculate.GetHoldCost()
            dividend_yield = dividend / holdCostValue
            dividend_yield = str(round(dividend_yield*100, 2)) + "%"
            
            holdCostValue_Total += holdCostValue
            dividend_Total += dividend
            dividendSummary_year.loc[idx] = [stock, stockNames[idx], ex_dividend_amount, 
                                             dividend, holdCostValue, dividend_yield]
        
        dividend_yield_Total = dividend_Total / holdCostValue_Total
        dividend_yield_Total = str(round(dividend_yield_Total*100, 2)) + "%"
        dividendSummary_year.loc[idx+1] = ["Total", "-", "-", dividend_Total, 
                                           holdCostValue_Total, dividend_yield_Total]
        
        dividendSummary_year.to_excel(path_dividendSummary.format(year), index=False)
            
if __name__ == '__main__':
    EvaluateDividend()
    
    
    