from django.conf.urls import url
from sportbook import views

app_name = 'sportbook'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^mlb', views.mlb, name='mlb'),
    url(r'^cbvtest',views.CBView.as_view()),
    url(r'^base', views.base, name='base'),
]