from django.urls import path
import adapter.views as ad
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    path('market/currencies', ad.MarketCurrencies.as_view(), name='currencies'),
    path('market/stocks/earn/<str:ticker_name>', ad.QuartEarnings.as_view(), name='earnings'),
    path('market/stocks/nextearns/<str:ticker_name>', ad.NextEarns.as_view(), name='next earnings'),
    path('market/stocks/info/<str:ticker_name>', ad.Info.as_view(), name='info'),
    path('market/stocks/dividends/<str:ticker_name>', ad.Dividends.as_view(), name='dividends'),
    path('market/stocks/nextdivs/<str:ticker_name>', ad.NextDivs.as_view(), name='next dividends'),
    path('market/<str:ticker>', ad.MarketDetail.as_view(), name='first')
]
