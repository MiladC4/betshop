from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.
class AccountInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
    address = models.CharField(max_length=128)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=5)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __unicode__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('account:detail', kwargs={'pk': self.pk})
