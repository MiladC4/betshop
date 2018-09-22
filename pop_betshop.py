import os
import requests
import json
from decimal import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'betshop.settings')

import django

django.setup()

from sportbook.models import MlbGame, MlbOdds


def populate():
    try:
        print("PULLING FROM API")
        r = requests.get("https://jsonodds.com/api/test/odds")
        data = r.content
        json_data = json.loads(data.decode("utf-8"))
        filtered = [x for x in json_data if x['Sport'] == 2]
        print("POPULATION HAPPENING")
        for g in filtered:
            odds_list = []
            odds_dict = {"h_sprd": "PointSpreadHomeLine", "a_sprd": "PointSpreadAwayLine",
                         "h_line": "MoneyLineHome", "a_line": "MoneyLineAway",
                         "over": "OverLine", "under": "UnderLine"}
            if len(g["Odds"]) > 1:
                odds = g["Odds"][1]

                for key, value in odds_dict.items():
                    id_odd = odds["ID"] + "-" + key
                    odd, new = MlbOdds.objects.update_or_create(odd_id=id_odd, home=g["HomeTeam"], type=key,
                                                                price=int(odds[value]))
                    odds_list.append(odd)

                try:
                    total = Decimal(odds["TotalNumber"])
                    spread = Decimal(odds["PointSpreadHome"])
                    game, is_new = MlbGame.objects.update_or_create(game_id=g["ID"],
                                                                    home=g["HomeTeam"],
                                                                    away=g["AwayTeam"],
                                                                    h_sprd=odds_list[0],
                                                                    a_sprd=odds_list[1],
                                                                    handicap=spread,
                                                                    h_line=odds_list[2],
                                                                    a_line=odds_list[3],
                                                                    total=total,
                                                                    over=odds_list[4],
                                                                    under=odds_list[5],
                                                                    h_score=0,
                                                                    a_score=0,
                                                                    live_status=0)
                    print("{} => {}".format(game, is_new))
                except django.db.utils.IntegrityError:
                    print("Probably a UNIQUE KEY ERROR")
        print("FINISHED")
    except requests.exceptions.RequestException:
        print('HTTP Request failed')


if __name__ == '__main__':
    populate()
