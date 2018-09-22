from django.db import models
from sportbook.models import MlbOdds
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save, m2m_changed
from decimal import Decimal
from shop.models import Product


# Create your models here.
class BetSlipManager(models.Manager):
    def new_or_get(self, request):
        slip_id = request.session.get('slip_id', None)
        qs = self.get_queryset().filter(id=slip_id)
        if qs.count() == 1:
            new_obj = False
            slip_obj = qs.first()
            if request.user.is_authenticated and slip_obj.user is None:
                slip_obj.user = request.user
                slip_obj.save()
        else:
            slip_obj = Slip.objects.new(user=request.user)
            new_obj = True
            request.session['slip_id'] = slip_obj.id
        return slip_obj, new_obj

    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)


class Slip(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    odds = models.ManyToManyField(MlbOdds, blank=True)
    products = models.ManyToManyField(Product, blank=True)
    divider = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    due = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = BetSlipManager()

    def __str__(self):
        return str(self.pk)

    def add_or_remove_odd(self, odds_obj):
        if odds_obj in self.odds.all():
            self.odds.remove(odds_obj)
            added = False
        else:
            self.odds.add(odds_obj)
            added = True
        return added

    def add_or_remove_prod(self, prod_obj):
        if prod_obj in self.products.all():
            self.products.remove(prod_obj)
            added = False
        else:
            self.products.add(prod_obj)
            added = True
        return added

    def calc_min_price(self):
        if self.odds.count == 0:
            min_price = -10000
        elif self.odds.count() == 5:
            min_price = 10000
        else:
            cnt = Decimal(1 / int(5 - self.odds.count()))
            max_divider = (20 / self.divider) ** (cnt)
            if max_divider < 2:
                min_price = -100 / (max_divider - 1)
            else:
                min_price = (max_divider - 1) * 100
        return int(min_price)


def m2m_changed_slip_receiver(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        odds = instance.odds.all()
        divide = 1
        for x in odds:
            mult = x.get_multiplier()
            divide = divide * mult
        if instance.divider != divide:
            instance.divider = divide
            instance.save()


def m2m_changed_slip_receiver_prod(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        products = instance.products.all()
        total = 0
        for x in products:
            total += x.price
        if instance.total != total:
            instance.total = total
            instance.save()


m2m_changed.connect(m2m_changed_slip_receiver, sender=Slip.odds.through)
m2m_changed.connect(m2m_changed_slip_receiver_prod, sender=Slip.products.through)


def pre_save_cart_receiver(sender, instance, *args, **kwargs):
    if instance.divider > 0 and instance.total > 0:
        instance.due = Decimal(instance.total) / Decimal(instance.divider)
    else:
        instance.due = 0


pre_save.connect(pre_save_cart_receiver, sender=Slip)


class PlaceBetManager(models.Manager):
    def calc_all_bets_value(self):
        pass


class PlacedBet(models.Model):
    STATUS_OPTIONS = (
        (0, 'active'),
        (1, 'lose'),
        (2, 'win')
    )

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    odds = models.ManyToManyField(MlbOdds, through="BetValue")
    products = models.ManyToManyField(Product)
    divider = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    sum_odds = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    placed = models.DateTimeField(auto_now=True)
    value = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    status = models.IntegerField(choices=STATUS_OPTIONS, default=0)

    objects = models.Manager()

    def __str__(self):
        return "{}: Value: {}".format(self.user, self.value)

    @classmethod
    def convert_slip(cls, slip_obj):
        price_sum = 0
        for odd in slip_obj.odds.all():
            if not odd.get_event_status() == 0:
                print(odd.get_event_status())
                return False
            price_sum += odd.get_multiplier()

        new_placed = cls.objects.create(user=slip_obj.user,
                                        value=slip_obj.total,
                                        divider=slip_obj.divider)
        for odd in slip_obj.odds.all():
            value = Decimal(slip_obj.total / (price_sum / odd.get_multiplier()))
            BetValue.objects.create(placed_bet=new_placed, odd=odd, value=value)
            slip_obj.odds.remove(odd)
        for prod in slip_obj.products.all():
            new_placed.products.add(prod)
            slip_obj.products.remove(prod)


class BetValue(models.Model):
    placed_bet = models.ForeignKey(PlacedBet, on_delete=models.CASCADE)
    odd = models.ForeignKey(MlbOdds, on_delete=models.CASCADE)
    value = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)

    objects = models.Manager()

    def __str__(self):
        return "{}, Value: {}".format(self.odd, self.value)
