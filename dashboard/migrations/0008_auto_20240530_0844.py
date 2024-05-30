# Generated by Django 5.0.4 on 2024-05-30 08:44

from django.db import migrations
import pandas as pd


def populate_new_field(apps, shchema_editor):
    file_path = 'media/uploads/20240507.csv'
    def status_text_converter(value):
        if pd.isna(value):
            return ''
        else:
            return str(value)
    column_types = {
        'CallType': int,
        'LastCampaign': int,
        'LastAgent': int,
        'WaitDuration': int,
        'ConvDuration': int,
        'WrapupDuration': int,
        'Overflow': int
    }
    df = pd.read_csv(
        file_path,
        usecols=[
            'CallType',
            'CallLocalTime',
            'LastCampaign',
            'WaitDuration',
            'ConvDuration',
            'WrapupDuration',
            'Overflow',
            'StatusText'
        ],
        dtype=column_types,
        parse_dates=['CallLocalTime'],
        encoding='utf-32be',
        converters={
            'StatusText': status_text_converter
        }
    
    )

    df['handled'] = df.apply(
        lambda row: 1 if row['ConvDuration'] >= 10
        and row['LastAgent'] > 0 else 0, axis=1
    )

    df['lost_ivr'] = df.apply(
        lambda row: 1 if row['ConvDuration'] == 0
        and row['WaitDuration'] == 0
        and row['Overflow'] == 0 else 0, axis=1
    )

    df['ignored'] = df.apply(
        lambda row: 1 if row['ConvDuration'] > 0
        and row['ConvDurtaion'] < 10 else 0, axis=1
    )
    df['rerouted'] = df.apply(
        lambda row: 1 if row['RerouteDuration'] > 0
        and row['LastAgent'] > 0 else 0, axis=1
    )

    for day in range(df['CallLocalTime'].min().day, df['CallLocalTime'].max().day):
        day_frame = df[
            (df['CallLocalTime'].apply(lambda x: x.day == day))
            & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
            & (df['CallLocalTime'].apply(lambda x: x.hour <= 21))
        ]
        tmoney_rows = day_frame[
            day_frame['LastCampaign'].isin([1845, 1846, 1847])
        ]

        tmoney_offered = tmoney_rows['CallType'].sum()

        tmoney_rows_handled = tmoney_rows[tmoney_rows['handled'] == 1]
        tmoney_rows_ignored = tmoney_rows[tmoney_rows['ignored'] == 1]['Ignored'].sum()
        tmoney_rows_rerouted = tmoney_rows[tmoney_rows['retouted'] == 1]['rerouted'].sum()
        tmoney_rows_ivr = tmoney_rows['lost_ivr']
        qs = round((tmoney_rows_handled + tmoney_rows_rerouted)/(tmoney_offered - tmoney_rows_ignored - tmoney_rows_ivr))
        
        print('Handled: {}'.format(tmoney_rows_handled['CallType'].sum()))
        print('Ignored : {}'.format(tmoney_rows_ignored))
        print('Lost Ivr: {}'.format(tmoney_rows['lost_ivr'].sum()))
        print('Rerouted: {}'.format(tmoney_rows_rerouted))

        print('QS: {}'.format(qs))


    # lf = apps.get_model('dashboard', 'LittleFlow')

    # for instance in lf.objects.all():

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_littleflow_dmt'),
    ]

    operations = [
    ]
