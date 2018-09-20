# Generated by Django 2.0.6 on 2018-09-20 01:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MlbGame',
            fields=[
                ('game_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('home', models.CharField(max_length=100)),
                ('away', models.CharField(max_length=100)),
                ('handicap', models.DecimalField(decimal_places=1, max_digits=7)),
                ('total', models.DecimalField(decimal_places=1, max_digits=7, null=True)),
                ('h_score', models.IntegerField(default=0)),
                ('a_score', models.IntegerField(default=0)),
                ('live_status', models.IntegerField(choices=[(0, 'pregame'), (1, 'live'), (2, 'complete')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='MlbOdds',
            fields=[
                ('odd_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('home', models.CharField(max_length=10, null=True)),
                ('type', models.CharField(choices=[('hS', 'Home Spread'), ('aS', 'Away Spread'), ('hL', 'Home Line'), ('aL', 'Away Line'), ('O', 'Over'), ('U', 'Under')], max_length=2)),
                ('price', models.IntegerField()),
                ('status', models.IntegerField(choices=[(0, 'pregame'), (1, 'lose'), (2, 'win'), (3, 'push')], default=0)),
            ],
        ),
        migrations.AddField(
            model_name='mlbgame',
            name='a_line',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='a_line', to='sportbook.MlbOdds'),
        ),
        migrations.AddField(
            model_name='mlbgame',
            name='a_sprd',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='a_sprd', to='sportbook.MlbOdds'),
        ),
        migrations.AddField(
            model_name='mlbgame',
            name='h_line',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='h_line', to='sportbook.MlbOdds'),
        ),
        migrations.AddField(
            model_name='mlbgame',
            name='h_sprd',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='h_sprd', to='sportbook.MlbOdds'),
        ),
        migrations.AddField(
            model_name='mlbgame',
            name='over',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='over', to='sportbook.MlbOdds'),
        ),
        migrations.AddField(
            model_name='mlbgame',
            name='under',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='under', to='sportbook.MlbOdds'),
        ),
    ]
