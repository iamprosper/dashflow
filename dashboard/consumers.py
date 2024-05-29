import asyncio
import json
from time import sleep
import numpy as np
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer


def load_inbound(file_path):
    def status_text_converter(value):
        if pd.isna(value):
            return ""
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

    """def int_converter(value):
        if pd.isna(value):
            return 0
        else:
            return int(value)"""
    global df

    df = pd.read_csv(
        file_path,
        usecols=[
            'CallType',
            'CallLocalTime',
            'LastCampaign',
            'LastAgent',
            'WaitDuration',
            'ConvDuration',
            'WrapupDuration',
            'Overflow',
            'StatusText'
        ],
        dtype=column_types,
        parse_dates= ['CallLocalTime'],
        encoding='utf-32be',
        converters={
            'StatusText': status_text_converter
            }
    )

    df = df.dropna(subset=["WaitDuration"])
    df = df.dropna(subset=["ConvDuration"])

    numeric_columns = df.select_dtypes(include=np.number).columns
    non_numeric_columns = df.columns.difference(numeric_columns)

    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)
    # df['handled'] = df[
    #     (df['ConvDuration'].apply(lambda cell: 1 if cell >= 10 else 0))
    #     & (df['LastAgent'] > 0)
    #     ]
    df['handled'] = df.apply(
        lambda row: 1 if row['ConvDuration'] >= 10
        and row['LastAgent'] > 0 else 0, axis=1
    )
    df['lost_ivr'] = df.apply(lambda row: 1 if row['ConvDuration'] == 0
                              and row['WaitDuration'] == 0
                              and row['Overflow'] == 0 else 0, axis=1)
    
    #days = filter_days()
    """print(days)
    for day_details in days.items():
        print(day_details)"""

    """filtered_rows_camp = df[(df['CallLocalTime'].apply(lambda x: x.day == 6))
                       & (df['LastCampaign'] >= 1845)
                       & (df['LastCampaign'] <= 1847)
                       & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
                       & (df['CallLocalTime'].apply(lambda x: x.hour <= 21))]"""

    #for day in range(df['CallLocalTime'].min().day, df['CallLocalTime'].max().day + 1):

load_inbound('media/uploads/05-2024.csv')

class DataConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        print('Connected successfully')
        await self.process_and_send_data()

    async def disconnect(self, close_code):
        print('Disconnected')
        pass

    async def receive(self, text_data):
        pass
    
    async def send_data(self, data):
        # print('Processing data')
        await self.send(text_data=json.dumps(data, default=str, indent=4))
        print('Data sent')
        """for day in range(df['CallLocalTime'].min().day, df['CallLocalTime'].max().day):
            await self.filter_days(day)"""
            # await self.send(text_data=json.dumps(days, default=str, indent=4))
    
    async def process_and_send_data(self):
        """async for item in self.filter_days():
            await self.send_data(item)"""
        await self.filter_days()
    
    async def filter_days(self):
        days = {}
        day_stat = {}
        days_list = [nb for nb in range(df['CallLocalTime'].min().day, df['CallLocalTime'].max().day)]
        for day in days_list:
 
            tmoney_rows = df[
                (df['CallLocalTime'].apply(lambda x: x.day == day))
                & (df['LastCampaign'].isin([1845, 1846, 1847]))
                & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
                & (df['CallLocalTime'].apply(lambda x: x.hour <= 21))
            ]

            tmoney_rows_offered = tmoney_rows['CallType'].sum()
            tmoney_rows_lost_ivr= tmoney_rows['lost_ivr'].sum()
            tmoney_rows_handled = tmoney_rows[tmoney_rows['handled'] == 1]
            tmoney_rows_dma = round(tmoney_rows_handled['WaitDuration'].mean())
            tmoney_rows_dmc = round(tmoney_rows_handled['ConvDuration'].mean())
            tmoney_rows_dpt = round(tmoney_rows_handled['WrapupDuration'].mean())
            tmoney_rows_dmt = tmoney_rows_dmc + tmoney_rows_dpt

            tmoney_stats = {
                'offered': tmoney_rows_offered,
                'lost_ivr': tmoney_rows_lost_ivr,
                'dma': tmoney_rows_dma,
                'dmc': tmoney_rows_dmc,
                'dpt': tmoney_rows_dpt,
                'dmt': tmoney_rows_dmt
            }
            
            fixe_rows = df[
                (df['CallLocalTime'].apply(lambda x: x.day == day))
                & (df['LastCampaign'].isin([1117, 1118, 1119]))
                & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
                & (df['CallLocalTime'].apply(lambda x: x.hour <= 21))
            ]
            fixe_rows_offered = fixe_rows['CallType'].sum()
            fixe_rows_lost_ivr= fixe_rows['lost_ivr'].sum()
            fixe_rows_handled = fixe_rows[fixe_rows['handled'] == 1]
            fixe_rows_dma = round(fixe_rows_handled['WaitDuration'].mean())
            fixe_rows_dmc = round(fixe_rows_handled['ConvDuration'].mean())
            fixe_rows_dpt = round(fixe_rows_handled['WrapupDuration'].mean())
            fixe_rows_dmt = fixe_rows_dmc + fixe_rows_dpt

            fixe_stats = {
                'offered': fixe_rows_offered,
                'lost_ivr': fixe_rows_lost_ivr,
                'dma': fixe_rows_dma,
                'dmc': fixe_rows_dmc,
                'dpt': fixe_rows_dpt,
                'dmt': fixe_rows_dmt
            }
            
            mobile_rows = df[
                (df['CallLocalTime'].apply(lambda x: x.day == day))
                & (df['LastCampaign'].isin([1880, 1890, 1891]))
                & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
                & (df['CallLocalTime'].apply(lambda x: x.hour <= 21))
            ]
            mobile_rows_offered = mobile_rows['CallType'].sum()
            mobile_rows_lost_ivr= mobile_rows['lost_ivr'].sum()
            mobile_rows_handled = mobile_rows[mobile_rows['handled'] == 1]
            mobile_rows_dma = round(mobile_rows_handled['WaitDuration'].mean())
            mobile_rows_dmc = round(mobile_rows_handled['ConvDuration'].mean())
            mobile_rows_dpt = round(mobile_rows_handled['WrapupDuration'].mean())
            mobile_rows_dmt = mobile_rows_dmc + mobile_rows_dpt

            mobile_stats = {
                'offered': mobile_rows_offered,
                'lost_ivr': mobile_rows_lost_ivr,
                'dma': mobile_rows_dma,
                'dmc': mobile_rows_dmc,
                'dpt': mobile_rows_dpt,
                'dmt': mobile_rows_dmt
            }
            
            pdv_rows = df[
                (df['CallLocalTime'].apply(lambda x: x.day == day))
                & (df['LastCampaign'].isin([1109, 1110]))
                & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
                & (df['CallLocalTime'].apply(lambda x: x.hour <= 21))
            ]
            pdv_rows_offered = pdv_rows['CallType'].sum()
            pdv_rows_lost_ivr= pdv_rows['lost_ivr'].sum()
            pdv_rows_handled = pdv_rows[pdv_rows['handled'] == 1]
            pdv_rows_dma = round(pdv_rows_handled['WaitDuration'].mean())
            pdv_rows_dmc = round(pdv_rows_handled['ConvDuration'].mean())
            pdv_rows_dpt = round(pdv_rows_handled['WrapupDuration'].mean())
            pdv_rows_dmt = pdv_rows_dmc + pdv_rows_dpt

            pdv_stats = {
                'offered': pdv_rows_offered,
                'lost_ivr': pdv_rows_lost_ivr,
                'dma': pdv_rows_dma,
                'dmc': pdv_rows_dmc,
                'dpt': pdv_rows_dpt,
                'dmt': pdv_rows_dmt
            }

            # for day in range(fran_rows.min().day(), fran_rows.max().day()):
            fran_rows = df[
                (df['CallLocalTime'].apply(lambda x: x.day == day))
                & (df['LastCampaign'].isin([1111, 1112, 1113]))
                & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
                & (df['CallLocalTime'].apply(lambda x: x.hour <= 21))
            ]
            weekday = fran_rows[
                fran_rows['CallLocalTime'].apply(lambda x: x.day == day)
                ]['CallLocalTime'].iloc[0].weekday()
            
            days_of_week = ['Monday',
                            'Tuesday',
                            'Wednesday',
                            'Thursday',
                            'Friday',
                            'Saturday',
                            'Sunday'
                            ]
            # if (days_of_week[weekday] != 'Sunday'):
            #     print("Fran day number - {}, day name {}".format(weekday, days_of_week[weekday]))
            if (days_of_week[weekday] != 'Sunday'):
                fran_rows_offered = fran_rows['CallType'].sum()
                fran_rows_lost_ivr= fran_rows['lost_ivr'].sum()
                fran_rows_handled = fran_rows[fran_rows['handled'] == 1]
                if not fran_rows_handled.empty:
                    fran_rows_dma = round(fran_rows_handled['WaitDuration'].mean())
                    fran_rows_dmc = round(fran_rows_handled['ConvDuration'].mean())
                    fran_rows_dpt = round(fran_rows_handled['WrapupDuration'].mean())
                # fran_rows_dmt = fran_rows_dmc + fran_rows_dpt

                    fran_stats = {
                        'offered': fran_rows_offered,
                        'lost_ivr': fran_rows_lost_ivr,
                        'dma': fran_rows_dma,
                        'dmc': fran_rows_dmc,
                        'dpt': fran_rows_dpt,
                        # 'dmt': fran_rows_dmt
                    }
                else:
                    fran_stats = {}

                day_stat = {
                    'tmoney':tmoney_stats,
                    'fixe':fixe_stats,
                    'mobile':mobile_stats,
                    'fran':fran_stats,
                    'pdv':pdv_stats,
                }
            else:
                day_stat = {
                    'tmoney':tmoney_stats,
                    'fixe':fixe_stats,
                    'mobile':mobile_stats,
                    'pdv':pdv_stats,
                }
            days[day] = day_stat
            print("Loaded")
            print("Day {} - {}".format(df[df['CallLocalTime'].apply(lambda x: x.day == day)]
                                        ['CallLocalTime'].iloc[0].day,
                                        day
                                        ))
            # print(days[day])
            await self.print_sth(day_stat)
            # await self.send(text_data=json.dumps(days, default=str, indent=4))
            print("==================")

        # return days 
    

    async def print_sth(self, data):
    # sleep(2)
    # consumer = DataConsumer()
        print("Data : {}".format(data))
        await self.send(text_data=json.dumps(data, default=str, indent=4))
