#!/usr/bin/python2
# -*- coding: utf-8 -*-

class Parser:

    @classmethod
    def extractDataSingle(self,response):
        index = response.find("=")
        html = response[index+2:-3]
        if html[-1:] == ",":
            html = html[:-1]
        return html

    @classmethod
    def extractSingleETFData(self,response):
        index = response.find("=")
        contentstr = response[index+2:-1]
        stock = contentstr.split(",")
        stock_dict = dict(
                name=stock[0],
                now=float(stock[3]),
        )
        return stock_dict

    @classmethod
    def extractMultipleOptionData(self,response):
        lines = response.split(";")
        data = {}
        for line in lines:
            index = line.find("=")
            code = line[index-8:index]
            contentstr = line[index+2:-1]
            content = contentstr.split(",")
            if len(content) < 43:
                continue
            data[code] = {
                "buy_volume":content[0],
                "buy_price":float(content[1]),
                "now_price":content[2],
                "sell_price":float(content[3]),
                "sell_volume":content[4],
                "hold_volume":content[5],
                "change_pct":content[6],
                "strike_price":float(content[7]),
                "prev_close":content[8],
                "open":content[9],
                "high_limit":content[10],
                "low_limit":content[11],
                # "ask5":content[12],
                # "ask5_volume":content[13],
                # "ask4":content[14],
                # "ask4_volume":content[15],          
                # "ask3":content[16],
                # "ask3_volume":content[17],
                # "ask2":content[18],
                # "ask2_volume":content[19],
                # "ask1":content[20],
                # "ask1_volume":content[21],
                # "bid1":content[22],
                # "bid1_volume":content[23],
                # "bid2":content[24],
                # "bid2_volume":content[25], 
                # "bid3":content[26],
                # "bid3_volume":content[27], 
                # "bid4":content[28],
                # "bid4_volume":content[29], 
                # "bid5":content[30],
                # "bid5_volume":content[31], 
                "update_time":content[32],
                "target":content[36],
                "name":content[37],
                "high":content[39],
                "low":content[40],
                "volume":content[41],
                "amount":content[42],
                "status":content[43]
            }
        return data