import numpy as np
import pandas as pd

def ReadStockRecord(path_stockRecord):
    """
    Read stock record
    
    Parameters
    ----------
    path_stockRecord : str
        The path to read stock record
        
    Returns
    -------
    stockRecord : Dict
        Return the stock record dictionary
            - keys -> stockID list
            - values -> stock record data frame for each stock
                - columns = ["Date", "Stock", "Price",　"Buy", "Amount"]
                
    """
    stockRecord_raw = pd.read_excel(path_stockRecord, dtype=str, sheet_name = "Record")
    stockRecord_raw[["Price", "Amount"]] = stockRecord_raw[["Price", "Amount"]].apply(pd.to_numeric)
    stockRecord_raw["Stock"] = stockRecord_raw["Stock"].astype(str)
    stockRecord_raw["Date"] = stockRecord_raw["Date"].apply(pd.to_datetime)
    stockRecord_raw["Buy"] = stockRecord_raw["Buy"]=="True"
    
    stockList = np.unique(stockRecord_raw['Stock'])
    
    stockRecord = {}
    for idx, stockID in enumerate(stockList):
        select_stockRecord = stockRecord_raw[stockRecord_raw['Stock']==stockID]
        stockRecord[stockID] = select_stockRecord
    return stockRecord


def ReadDividendRecord(path_dividendRecord):
    """
    Read dividend record
    
    Parameters
    ----------
    path_dividendRecord : str
        The path to read dividend record
        
    Returns
    -------
    1. dividendRecord : Dict
        Return the dividend record dictionary 
         - keys -> stockID list
         - values -> dividend data frame for each stock
             - columns = ['Year', 'Amount', 'Dividend_unit', 'Dividend_value']
    2. years : Array
        Return the years list
    3. stockNames : List
        Return the stock name list
    
    """
    dividendRecord_raw = pd.read_excel(path_dividendRecord, dtype=str, sheet_name = "Record")
    years = np.array(dividendRecord_raw.iloc[1:,0])

    select_index = list(range(1, len(dividendRecord_raw.columns), 3))
    stockList = [dividendRecord_raw.columns[i] for i in select_index]
    
    dividendRecord = {}
    stockNames = []
    for idx, stockID in enumerate(stockList):
        stock_position_idx = select_index[idx]
        selectDividend = dividendRecord_raw.iloc[1:, (1+stock_position_idx-1):(1+stock_position_idx-1+3)]
        stockName = selectDividend.columns[1]
        
        selectDividend = selectDividend.set_axis(["Amount", "Dividend_unit", "Dividend_value"], axis=1)
        selectDividend.insert(0, "Year", years)
        
        dividendRecord[stockID] = selectDividend
        stockNames.append(stockName)
    
    
    return dividendRecord, years, stockNames
    
    
    
