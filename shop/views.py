from django.shortcuts import render
from .models import Product
from betslip.models import Slip


# Create your views here.
def index(request):
    prod_list = Product.objects.all()
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    prod_dict = {'products': prod_list,
                 'slip': slip_obj}

    return render(request, 'shop/index.html', context=prod_dict)
