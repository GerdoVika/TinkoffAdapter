from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from TinkoffAdapter.settings import SANDBOX_TOKEN
import tinvest as ti
import json
import yfinance as yf


class MarketDetail(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker):
        client = ti.SyncClient(SANDBOX_TOKEN, use_sandbox=True)
        register = client.register_sandbox_account(ti.SandboxRegisterRequest.tinkoff())
        response = client.get_market_search_by_ticker(ticker)
        return Response(json.loads(response.json()))


class MarketCurrencies(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request):
        client = ti.SyncClient(SANDBOX_TOKEN, use_sandbox=True)
        register = client.register_sandbox_account(ti.SandboxRegisterRequest.tinkoff())
        data = client.get_market_currencies().dict()['payload']['instruments']
        data_json = []
        for item in data:
            res = {}
            res['name'] = item['name']
            res['ticker'] = item['ticker']
            res['currency'] = item['currency']
            data_json.append(res)
        return Response(json.dumps(data_json, ensure_ascii=False))


class QuartEarnings(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker_name):
        tick = yf.Ticker(ticker_name)
        data = tick.quarterly_earnings
        data_json = None
        if data is not None:
            data_json = data.to_json(orient="index")
        return Response(data_json)


class Info(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker_name):
        tick = yf.Ticker(ticker_name)
        data = tick.info
        data_json = None
        if data is not None:
            if data['trailingEps'] != None:
                EPS = round(data['trailingEps'], 2)
            else:
                EPS = None
            if data['beta'] != None:
                Beta = round(data['beta'], 2)
            else:
                Beta = None
            if data['debtToEquity'] != None:
                DebtToEquity = round(data['debtToEquity'], 2)
            else:
                DebtToEquity = None
            data_json = {
                'MarketCap': data['marketCap'],
                'SharesOutstanding': data['sharesOutstanding'],
                'Revenue': data['totalRevenue'],
                'EPS': EPS,
                'Beta': Beta,
                'Cash': data['totalCash'],
                'Debt': data['totalDebt'],
                'DebtToEquity': DebtToEquity
            }
        return Response(json.dumps(data_json))


class Dividends(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker_name):
        tick = yf.Ticker(ticker_name)
        data = tick.dividends
        if data is not None:
            data_json = data.to_json()
        else:
            data_json = None
        return Response(data_json)


class NextDivs(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker_name):
        tick = yf.Ticker(ticker_name)
        data = tick.info
        data_json = None
        if data is not None:
            time = data['exDividendDate']
            data_json = {'next_div_day': time}
        return Response(json.dumps(data_json))


class NextEarns(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker_name):
        tick = yf.Ticker(ticker_name)
        data = tick.calendar
        data_json = None
        if data is not None:
            col = data.columns.values[1]
            data_json = {
                'Date': data.loc[data.index.values[0], col].value // 10 ** 9,
                'EPS': data.loc[data.index.values[1], col],
                'Revenue': data.loc[data.index.values[4], col]
            }
        return Response(json.dumps(data_json))
