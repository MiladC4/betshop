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


def m2m_changed_slip_receiver(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        odds = instance.odds.all()
        divide = 1
        for x in odds:
            if x.price > 0:
                mult = Decimal(x.price / 100 + 1)
            else:
                mult = Decimal(100 / (x.price * -1) + 1)
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
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    odds = models.ManyToManyField(MlbOdds)
    products = models.ManyToManyField(Product)
    divider = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    placed = models.DateTimeField(auto_now=True)
    value = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)

    def __str__(self):
        return "{}: Value: {}".format(self.user, self.value)

    @classmethod
    def convert_slip(cls, slip_obj):
        for odd in slip_obj.odds.all():
            if not odd.status == 0:
                return False
        new_placed = cls.objects.create(user=slip_obj.user,
                                        value=slip_obj.total,
                                        divider=slip_obj.divider)
        for odd in slip_obj.odds.all():
            new_placed.odds.add(odd)
            slip_obj.odds.remove(odd)
        for prod in slip_obj.products.all():
            new_placed.products.add(prod)
            slip_obj.products.remove(prod)
        return

