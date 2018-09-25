from django.shortcuts import render, redirect
from django.http import JsonResponse
from sportbook.models import MlbOdds
from shop.models import Product
from .models import *
from decimal import Decimal
from sportbook.models import MlbOdds
from django.core.serializers import serialize


# Create your views here.
def slip_home(request):
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    if slip_obj.divider == 0 or slip_obj.odds.count() == 5:
        min_price = -10000
    else:
        cnt = Decimal(1 / int(5 - slip_obj.odds.count()))
        max_divider = (20 / slip_obj.divider) ** (cnt)
        if max_divider < 2:
            min_price = -100 / (max_divider - 1)
        else:
            min_price = (max_divider - 1) * 100
    odds_list = MlbOdds.objects.filter(price__gte=min_price)
    cont_dict = {
        'slip': slip_obj,
        'odds': odds_list,
    }
    return render(request, 'betslip/home.html', context=cont_dict)


def slip_update(request):
    odds_id = request.POST.get('bet_id')
    prod_id = request.POST.get('prod_id')
    added = False
    if odds_id:
        try:
            odds_obj = MlbOdds.objects.get(odd_id=odds_id)
        except MlbOdds.DoesNotExist:
            print(odds_id)
            print('Odds does not exist')
            return redirect('betslip:home')
        slip_obj, new_obj = Slip.objects.new_or_get(request)
        added = slip_obj.add_or_remove_odd(odds_obj)
        request.session['slip_odds'] = str(round(slip_obj.divider, 2))
        request.session['slip_due'] = str(round(slip_obj.due, 2))
    elif prod_id:
        try:
            prod_obj = Product.objects.get(id=prod_id)
        except Product.DoesNotExist:
            print('Odds does not exist')
            return redirect('betslip:home')
        slip_obj, new_obj = Slip.objects.new_or_get(request)
        added = slip_obj.add_or_remove_prod(prod_obj)
        request.session['slip_odds'] = str(round(slip_obj.divider, 2))
        request.session['slip_due'] = str(round(slip_obj.due, 2))
    if request.is_ajax:
        bets = serialize('json', slip_obj.odds.all())
        json_data = {
            "added": added,
            "removed": not added,
            "slipOdds": str(round(slip_obj.divider, 2)),
            "slipDue": str(round(slip_obj.due, 2)),
            "slipBets": bets,
        }
        return JsonResponse(json_data)
    return redirect('betslip:home')


def parley_update(request):
    odds_id = request.POST.get('bet_id')
    if odds_id is not None:
        try:
            odds_obj = MlbOdds.objects.get(odd_id=odds_id)
        except MlbOdds.DoesNotExist:
            print('Odds does not exist')
            return redirect('betslip:home')
        slip_obj, new_obj = Slip.objects.new_or_get(request)
        added = slip_obj.add_or_remove_odd(odds_obj)
        request.session['slip_odds'] = str(round(slip_obj.divider, 2))
        request.session['slip_due'] = str(round(slip_obj.due, 2))
        if request.is_ajax:
            min_price = slip_obj.calc_min_price()
            odds_list = serialize('json', MlbOdds.objects.filter(price__gte=min_price, live_status=0))
            bets = serialize('json', slip_obj.odds.all())
            json_data = {
                "added": added,
                "removed": not added,
                "slipOdds": str(round(slip_obj.divider, 2)),
                "slipDue": str(round(slip_obj.due, 2)),
                "minPrice": min_price,
                "slipBets": bets,
                "oddsRemain": odds_list,
            }
            return JsonResponse(json_data)
    return redirect('betslip:home')


####### Submitting Bet View #######
def submit_bet(request):
    try:
        slip_obj, new_obj = Slip.objects.new_or_get(request)
    except Slip.DoesNotExist:
        print('Slip does not exist')
        return redirect('betslip:home')
    PlacedBet.convert_slip(slip_obj)
    return redirect('betslip:home')


def submit_straight_bets(request):
    if not request.user.is_authenticated:
        return redirect('sportbook:mlb')
    slip_obj, new_obj = Slip.objects.new_or_get(request)
    if not new_obj:
        odds = slip_obj.odds.all()
        total_due = 0
        # Check account Balance and Max Bet #
        for odd in odds:
            total_due += Decimal(request.POST.get(odd.pk))
        if total_due > slip_obj.user.account.balance:
            return redirect('sportbook:mlb')
        # Create Bets,
        for odd in odds:
            due = Decimal(request.POST.get(odd.pk))
            StraightBet.submit_straight_bet(odd, due, slip_obj.user)
            account = slip_obj.user.account
            account.balance = Decimal(account.balance - due)
            account.save()
            slip_obj.odds.remove(odd)
    return redirect('account:active_bets')
