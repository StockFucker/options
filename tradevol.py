# -*- coding: utf-8 -*-

import QuantLib as ql
import matplotlib.pyplot as plt
import datetime
import pandas as pd

from nowquotes import download
from wmDownloader import getOptionsInfo,getHistoryQuotesInfo

risk_free_rate = 0.03 #无风险利率 优化点1  0.005 利率差 对应期权0.1%价格波动，变化不大
dividend_rate =  0
day_count = ql.Actual365Fixed()  #一年的日期数 优化点2  


class VolTrader:
    def __init__(self):
        downloader = download()
        self.data = downloader.all
        self.spot_price = downloader.targetPrice #标的价格 优化点3
        self.options_info = getOptionsInfo(True)

    def calculate(self):
        delta_se = pd.Series()  #这个delta是差价
        vol_se = pd.Series()
        call_delta = pd.Series()  #这个delta是希腊值delta
        put_delta = pd.Series()
        strike_price_se = pd.Series()

        call_df = self.data[0]
        put_df = self.data[4]
        call_df = call_df.drop_duplicates(subset="strike_price")
        put_df = put_df.drop_duplicates(subset="strike_price")

        for i in range(-20,20):
            fix_spot_price = self.spot_price + float(i)/1000
            call_vol_df = self.get_vol(call_df,ql.Option.Call,fix_spot_price)
            put_vol_df = self.get_vol(put_df,ql.Option.Put,fix_spot_price)
            delta = (call_vol_df["ask"] - put_vol_df["ask"]).abs().dropna()
            delta_se[fix_spot_price] = delta.min()
            vol_se[fix_spot_price] = call_vol_df["ask"][delta.idxmin()]
            call_delta[fix_spot_price] = call_vol_df["ask_delta"][delta.idxmin()]
            put_delta[fix_spot_price] = put_vol_df["ask_delta"][delta.idxmin()]
            strike_price_se[fix_spot_price] = delta.idxmin()

        vol_se = vol_se.astype(float)
        df = pd.DataFrame()
        df["vol"] = vol_se
        df["delta"] = delta_se
        df["put_delta"] = put_delta
        df["call_delta"] = call_delta
        df["strike_price"] = strike_price_se
        idx = df["delta"].idxmin()
        vol = df["vol"][idx]
        put_delta = df["put_delta"][idx]
        call_delta = df["call_delta"][idx]
        strike_price = df["strike_price"][idx]
        call_code = list(call_df[call_df["strike_price"] == strike_price].index)[0]
        put_code = list(put_df[put_df["strike_price"] == strike_price].index)[0]
        return call_code,put_code,vol,call_delta,put_delta

    def get_vol(self,df,option_type,spot_price):
        vol_df = pd.DataFrame(index=list(df["strike_price"]),columns=['bid','ask','bid_delta','ask_delta'])
        for index,row in df.iterrows():
            buy_price = row["buy_price"]
            sell_price = row["sell_price"]
            strike_price = row["strike_price"]
            exer_date = self.options_info["exerDate"][index]
            exer_datetime = datetime.datetime.strptime(exer_date,"%Y-%m-%d")
            maturity_date = ql.Date(exer_datetime.day, exer_datetime.month, exer_datetime.year) #交割日
            update_time = row["update_time"]
            update_datetime = datetime.datetime.strptime(update_time,"%Y-%m-%d %H:%M:%S")
            calculation_date = ql.Date(update_datetime.day, update_datetime.month, update_datetime.year) #交割日
            try:
                buy_vol,buy_delta = self.calculateImpliedVolatility(buy_price,spot_price,strike_price,calculation_date,maturity_date,option_type)
                sell_vol,sell_delta = self.calculateImpliedVolatility(sell_price,spot_price,strike_price,calculation_date,maturity_date,option_type)
                vol_df.set_value(strike_price,"bid",buy_vol)
                vol_df.set_value(strike_price,"ask",sell_vol)
                vol_df.set_value(strike_price,"bid_delta",buy_delta)
                vol_df.set_value(strike_price,"ask_delta",sell_delta)
    #             print buy_vol,sell_vol
            except Exception,e:
                continue
    #             print buy_price,spot_price,strike_price
        vol_df = vol_df.sort_index()
        return vol_df

    def calculateImpliedVolatility(self,option_price,spot_price,strike_price,calculation_date,maturity_date,option_type):
        volatility = 0
        calendar = ql.China() 
        payoff = ql.PlainVanillaPayoff(option_type, strike_price)  
        exercise = ql.EuropeanExercise(maturity_date) 
        european_option = ql.VanillaOption(payoff, exercise) 
        spot_handle = ql.QuoteHandle(  
            ql.SimpleQuote(spot_price)
        )
        flat_ts = ql.YieldTermStructureHandle( 
            ql.FlatForward(calculation_date, risk_free_rate, day_count)
        )  
        dividend_yield = ql.YieldTermStructureHandle(
            ql.FlatForward(calculation_date, dividend_rate, day_count)
        ) 
        flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(calculation_date, calendar, volatility, day_count)  
        )
        bsm_process = ql.BlackScholesMertonProcess(spot_handle, 
                                                   dividend_yield, 
                                                   flat_ts, 
                                                   flat_vol_ts)
        vol = european_option.impliedVolatility(option_price,bsm_process)
        
        flat_vol_ts2 = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(calculation_date, calendar, vol, day_count)  
        )
        bsm_process2 = ql.BlackScholesMertonProcess(spot_handle, 
                                               dividend_yield, 
                                               flat_ts, 
                                               flat_vol_ts2)
        european_option2 = ql.VanillaOption(payoff, exercise) 
        european_option2.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process2))
    #     print european_option2.NPV() - option_price
        return vol,european_option2.delta()


if __name__ == '__main__':
    voltrader = VolTrader()
    print voltrader.calculate()