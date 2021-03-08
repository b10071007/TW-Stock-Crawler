import numpy as np

class StockCalculator():
    """
    Calculate various indicator for a stock
    
    Parameters
    ----------
    stockRecord : DataFrame
        the record for a stock
    """
    def __init__(self, stockRecord):
        self.stockRecord = stockRecord
        self.buy_Record = stockRecord[stockRecord["Buy"]==True]
        self.sell_Record = stockRecord[stockRecord["Buy"]!=True]
        
        # Basic measure
        self.totalBuyAmount = np.sum(self.buy_Record["Amount"])
        self.totalBuyValue = np.sum(self.buy_Record["Price"] * self.buy_Record["Amount"] + 20)
        self.totalSellAmount = np.sum(self.sell_Record["Amount"])
        self.totalSellValue = np.sum(self.sell_Record["Price"] * self.sell_Record["Amount"] * (1-0.003) - 20)
        self.holdAmount = np.sum(self.buy_Record["Amount"]) - np.sum(self.sell_Record["Amount"])
        
    def GetHoldCost(self):
        """
        Returns
        -------
        holdCost : float
            return the holding cost
        holdCostValue : float
            return the holding cost value
        """
        holdCost = (self.totalBuyValue - self.totalSellValue)/ self.holdAmount if self.holdAmount>0 else 0
        holdCostValue = holdCost * self.holdAmount
        return holdCost, holdCostValue

    def GetBuyAvgPrice(self):
        BuyAvgPrice = self.totalBuyValue / self.totalBuyAmount
        BuyAvgPrice = round(BuyAvgPrice, 4)
        return BuyAvgPrice
    
    def GetSellAvgPrice(self):
        SellAvgPrice = self.totalSellValue / self.totalSellAmount if self.totalSellAmount>0 else 0
        SellAvgPrice = round(SellAvgPrice, 4)
        return SellAvgPrice
    
    def GetTotalSellAmount(self):
        return self.totalSellAmount
    
    def GetTotalSellValue(self):
        return self.totalSellValue
    
    def GetStockProfit(self, price):
        # holdCost and Unrealized profit
        holdLatestValue = price * self.holdAmount
        _, holdCostValue = self.GetHoldCost()
        holdProfit = holdLatestValue - holdCostValue
        holdProfitRatio = holdProfit / (holdLatestValue-holdProfit) * 100 if self.holdAmount>0 else 0
        holdProfitRatio = round(holdProfitRatio,2)
        
        # Realized Profit
        if (self.totalSellValue!=0):
            profit = self.totalSellValue - (self.totalBuyValue-self.holdCostValue)
        else:
            profit = 0
        return holdLatestValue, holdCostValue, holdProfit, holdProfitRatio, profit
        
        