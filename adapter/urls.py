from django.urls import path
from adapter.views import MarketDetail
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    path('market/<str:ticker>', MarketDetail.as_view(), name='first')
]
