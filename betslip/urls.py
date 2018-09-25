from django.conf.urls import url
from .views import slip_home, slip_update, parley_update, submit_bet, submit_straight_bets

app_name = 'betslip'

urlpatterns = [
    url(r'^$', slip_home, name='home'),
    url(r'^update/$', slip_update, name='update'),
    url(r'^parley_update/$', parley_update, name='parley_update'),
    url(r'^submit_bet/$', submit_bet, name='submit_bet'),
    url(r'^submit_straight_bets/$', submit_straight_bets, name='submit_straight_bets'),
]