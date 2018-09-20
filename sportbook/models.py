from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.dispatch import receiver


class OddsManager(models.Manager):
    def get_all_active(self):
        self.get_queryset().filter(status=0)

class MlbOdds(models.Model):
    BET_TYPES = (
        ('hS', 'Home Spread'),
        ('aS', 'Away Spread'),
        ('hL', 'Home Line'),
        ('aL', 'Away Line'),
        ('O', 'Over'),
        ('U', 'Under'),
    )

    STATUS_OPTIONS = (
        (0, 'pregame'),
        (1, 'lose'),
        (2, 'win'),
        (3, 'push')
    )
    odd_id = models.CharField(max_length=100, primary_key=True)
    home = models.CharField(max_length=10, null=True)
    type = models.CharField(max_length=2, choices=BET_TYPES)
    price = models.IntegerField()
    status = models.IntegerField(choices=STATUS_OPTIONS, default=0)

    objects = models.Manager()
    active_objects = OddsManager()

    def __str__(self):
        return "{} Type: {}".format(self.home, self.type)


class MlbGame(models.Model):
    LIVE_STATUS_OPTIONS = (
        (0, 'pregame'),
        (1, 'live'),
        (2, 'complete')
    )
    game_id = models.CharField(primary_key=True, max_length=100)
    home = models.CharField(max_length=100)
    away = models.CharField(max_length=100)
    h_sprd = models.OneToOneField(MlbOdds, on_delete=models.CASCADE, related_name='h_sprd', null=True)
    a_sprd = models.OneToOneField(MlbOdds, on_delete=models.CASCADE, related_name='a_sprd', null=True)
    handicap = models.DecimalField(max_digits=7, decimal_places=1)
    h_line = models.OneToOneField(MlbOdds, on_delete=models.CASCADE, related_name='h_line', null=True)
    a_line = models.OneToOneField(MlbOdds, on_delete=models.CASCADE, related_name='a_line', null=True)
    total = models.DecimalField(max_digits=7, decimal_places=1, null=True)
    over = models.OneToOneField(MlbOdds, on_delete=models.CASCADE, related_name='over', null=True)
    under = models.OneToOneField(MlbOdds, on_delete=models.CASCADE, related_name='under', null=True)
    h_score = models.IntegerField(default=0)
    a_score = models.IntegerField(default=0)
    live_status = models.IntegerField(choices=LIVE_STATUS_OPTIONS, default=0)

    def __str__(self):
        return "{} at {}".format(self.away, self.home)

    def final_spread(self):
        home = self.h_score
        away = self.a_score
        handi = self.handicap
        dif = home - away
        h_sprd = self.h_sprd
        a_sprd = self.a_sprd
        if dif == handi:
            h_sprd.status = 3
            a_sprd.status = 3
        elif dif > handi:
            h_sprd.status = 2
            a_sprd.status = 1
        elif dif < handi:
            h_sprd.status = 1
            a_sprd.status = 2
        h_sprd.save()
        a_sprd.save()

    def final_line(self):
        home = self.h_score
        away = self.a_score
        h_line = self.h_line
        a_line = self.a_line
        if home == away:
            h_line.status = 3
            a_line.status = 3
        elif home > away:
            h_line.status = 2
            a_line.status = 1
        elif home < away:
            h_line.status = 1
            a_line.status = 2
        h_line.save()
        a_line.save()

    def final_total(self):
        pts = self.h_score + self.a_score
        total = self.total
        over = self.over
        under = self.under
        if total == pts:
            over.status = 3
            under.status = 3
        elif total > pts:
            over.status = 1
            under.status = 2
        elif total < pts:
            over.status = 2
            under.status = 1
        over.save()
        under.save()

    def update_game_bets(self):
        if self.live_status == 2:
            self.final_line()
            self.final_spread()
            self.final_total()


def update_odds(sender, instance, *args, **kwargs):
    instance.update_game_bets()


pre_save.connect(update_odds, sender=MlbGame)
