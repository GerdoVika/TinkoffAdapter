from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from TinkoffAdapter.settings import SANDBOX_TOKEN
import tinvest as ti
from tinvest.exceptions import UnexpectedError
import yfinance as yf
import adapter.services as services


response_sample = {
    'code': 200,
    'detail': 'ok',
    'payload': [],
    'total': 0,
}


class MarketStocksList(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request):
        client = ti.SyncClient(SANDBOX_TOKEN, use_sandbox=True)
        register = client.register_sandbox_account(ti.SandboxRegisterRequest.tinkoff())
        response = client.get_market_stocks().dict()['payload']
        stocks = response['instruments']
        r = response_sample.copy()

        for item in stocks:
            res = {
                'name': item['name'],
                'ticker': item['ticker'],
                'currency': item['currency'],
            }
            r['payload'].append(res)

        r['total'] = int(response['total'])

        return Response(r)


class MarketStocksDetail(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker):
        client = ti.SyncClient(SANDBOX_TOKEN, use_sandbox=True)
        register = client.register_sandbox_account(ti.SandboxRegisterRequest.tinkoff())
        response = client.get_market_search_by_ticker(ticker).dict()['payload']
        r = response_sample.copy()

        if response['total'] != 0:
            response = response['instruments'][0]
            data_price = client.get_market_orderbook(response['figi'], 0)
            response['last_price'] = data_price.dict()['payload']['last_price']
            r['payload'] = [response]
            r['total'] = len(r['payload'])

        return Response(r)


class MarketCurrenciesList(APIView):
    permission_classes = [AllowAny, ]
    
    def get(self, request):
        client = ti.SyncClient(SANDBOX_TOKEN, use_sandbox=True)
        register = client.register_sandbox_account(ti.SandboxRegisterRequest.tinkoff())
        data = client.get_market_currencies().dict()['payload']['instruments']
        r = response_sample.copy()
        data_json = []

        for item in data:
            data_price = client.get_market_orderbook(item['figi'], 0)
            res = {
                'name': item['name'],
                'ticker': item['ticker'],
                'currency': item['currency'],
                'last_price': data_price.dict()['payload']['last_price']
            }
            data_json.append(res)
        
        r['payload'] = data_json
        r['total'] = len(r['payload'])

        return Response(r)


class MarketCurrenciesDetail(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, currency):
        client = ti.SyncClient(SANDBOX_TOKEN, use_sandbox=True)
        register = client.register_sandbox_account(ti.SandboxRegisterRequest.tinkoff())
        data = client.get_market_currencies().dict()['payload']['instruments']
        r = response_sample.copy()
        data_json = []

        for item in data:
            if item["ticker"][:3] == currency.upper():
                data_price = client.get_market_orderbook(item['figi'], 0)
                item['last_price'] = data_price.dict()['payload']['last_price']
                data_json += [item]

        r['payload'] = data_json
        r['total'] = len(r['payload'])

        return Response(r)


class QuartEarnings(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker_name):
        tick = yf.Ticker(ticker_name)
        data = tick.quarterly_earnings
        r = response_sample.copy()
        data_json = []

        if data is not None:
            data_json.append(data.to_dict(orient='index'))
            r['payload'] = data_json
            r['total'] = len(r['payload'])

        return Response(r)


class Info(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker_name):
        tick = yf.Ticker(ticker_name)
        data = tick.info
        r = response_sample.copy()

        if len(data) > 2:
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
            r['payload'] = [data_json]
            r['total'] = len(r['payload'])

        return Response(r)


class Dividends(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker_name):
        tick = yf.Ticker(ticker_name)
        data = tick.dividends
        r = response_sample.copy()
        data_json = []

        if len(data) > 0:
            data = data.to_dict()

            for item in data:
                res = {
                    'data': item.value // 10 ** 9,
                    'value': data[item],
                }
                data_json.append(res)

        r['payload'] = data_json
        r['total'] = len(r['payload'])

        return Response(r)


class NextDivs(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker_name):
        tick = yf.Ticker(ticker_name)
        data = tick.info
        r = response_sample.copy()

        if len(data) > 2:
            time = data['exDividendDate']
            data_json = {'next_div_day': time}
            r['payload'] = [data_json]
            r['total'] = len(r['payload'])

        return Response(r)


class NextEarns(APIView):
    permission_classes = [AllowAny, ]

    def get(self, request, ticker_name):
        tick = yf.Ticker(ticker_name)
        data = tick.calendar
        r = response_sample.copy()
        
        if data is not None:
            col = data.columns.values[1]
            data_json = {
              'Date': data.loc[data.index.values[0], col].value // 10 ** 9,
              'EPS': data.loc[data.index.values[1], col],
              'Revenue': data.loc[data.index.values[4], col],
            }
           
            r['payload'] = [data_json]
            r['total'] = len(r['payload'])

        return Response(r)


class Insiders(APIView):
    permission_classes = [AllowAny,]

    def get(self, request, ticker, days=10):
        data = services.get_insiders(ticker, days)
        return Response(services.pd_insiders(data))


class SandboxAccountRegister(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        data = request.data
        r = response_sample.copy()

        if 'sandbox_token' in data:
            try:
                client = ti.SyncClient(data['sandbox_token'], use_sandbox=True)
                response = client.register_sandbox_account(ti.SandboxRegisterRequest.tinkoff())
                r['payload'] = [{
                    'broker_account_id': response.payload.broker_account_id
                }]

            except UnexpectedError:
                r['code'] = 401
                r['detail'] = 'invalid sandbox_token'

        else:
            r['code'] = 400
            r['detail'] = 'sandbox token not provided'

        return Response(r)


class SandboxAccountRemove(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        data = request.data
        r = response_sample.copy()

        if 'sandbox_token' in data:
            try:
                client = ti.SyncClient(data['sandbox_token'], use_sandbox=True)
                accounts = client.get_accounts().payload.accounts

                if accounts[0].broker_account_type == 'Tinkoff':
                    client.remove_sandbox_account(accounts[0].broker_account_id)
                else:
                    r['code'] = '500'
                    r['detail'] = 'account not registered'

            except UnexpectedError:
                r['code'] = 401
                r['detail'] = 'invalid sandbox_token'

        else:
            r['code'] = 400
            r['detail'] = 'sandbox token not provided'

        return Response(r)


class SandboxAccountClear(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        data = request.data
        r = response_sample.copy()

        if 'sandbox_token' in data:
            try:
                client = ti.SyncClient(data['sandbox_token'], use_sandbox=True)
                accounts = client.get_accounts().payload.accounts

                if accounts[0].broker_account_type == 'Tinkoff':
                    client.clear_sandbox_account(accounts[0].broker_account_id)
                else:
                    r['code'] = '500'
                    r['detail'] = 'account not registered'

            except UnexpectedError:
                r['code'] = 401
                r['detail'] = 'invalid sandbox_token'

        else:
            r['code'] = 400
            r['detail'] = 'sandbox token not provided'

        return Response(r)


class SandboxSetStocks(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        data = request.data
        r = response_sample.copy()

        if ('sandbox_token' in data) and ('figi' in data) and ('balance' in data):
            try:
                client = ti.SyncClient(data['sandbox_token'], use_sandbox=True)
                accounts = client.get_accounts().payload.accounts

                if accounts[0].broker_account_type == 'Tinkoff':
                    broker_account_id = accounts[0].broker_account_id
                    body = ti.SandboxSetPositionBalanceRequest(
                        balance=data['balance'],
                        figi=data['figi'],
                    )
                    client.set_sandbox_positions_balance(body, broker_account_id)

                else:
                    r['code'] = '500'
                    r['detail'] = 'account not registered'

            except UnexpectedError:
                r['code'] = 401
                r['detail'] = 'invalid sandbox_token'

        else:
            r['code'] = 400
            r['detail'] = 'lack of data. post sandbox_token, figi, balance'

        return Response(r)


class SandboxSetCurrencies(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        data = request.data
        r = response_sample.copy()

        if ('sandbox_token' in data) and ('currency' in data) and ('balance' in data):
            try:
                client = ti.SyncClient(data['sandbox_token'], use_sandbox=True)
                accounts = client.get_accounts().payload.accounts

                if accounts[0].broker_account_type == 'Tinkoff':
                    broker_account_id = accounts[0].broker_account_id
                    body = ti.SandboxSetCurrencyBalanceRequest(
                        balance=data['balance'],
                        currency=data['currency'],
                    )
                    client.set_sandbox_currencies_balance(body, broker_account_id)

                else:
                    r['code'] = '500'
                    r['detail'] = 'account not registered'

            except UnexpectedError:
                r['code'] = 401
                r['detail'] = 'invalid sandbox_token'

        else:
            r['code'] = 400
            r['detail'] = 'lack of data. post sandbox_token, currency, balance'

        return Response(r)
