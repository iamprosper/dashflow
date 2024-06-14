def load_inbound_per_5_min(file_path):
    def status_text_converter(value):
        if pd.isna(value) or type(value) == str:
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
        'Overflow': int,
        'RerouteDuration': int,
        'Abandon': int
    }

    def int_converter(value):
        try:
            return int(value)
        except:
            return 0
            
    # global df

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
            'StatusText',
            'RerouteDuration',
            'Abandon'
        ],
        # dtype=column_types,
        parse_dates= ['CallLocalTime'],
        encoding='utf-32be',
        converters={
            'StatusText': status_text_converter,
            'CallType': int_converter,
            'LastCampaign': int_converter,
            'LastAgent': int_converter,
            'WaitDuration': int_converter,
            'ConvDuration': int_converter,
            'WrapupDuration': int_converter,
            'Overflow': int_converter,
            'RerouteDuration': int_converter,
            'Abandon': int_converter
            }
    )

    df = df.dropna(subset=["WaitDuration"])
    df = df.dropna(subset=["ConvDuration"])

    # numeric_columns = df.select_dtypes(include=np.number).columns
    # non_numeric_columns = df.columns.difference(numeric_columns)

    # df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)
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
                              and row['Overflow'] == 0 else 0, axis=1
                              )
    df['ignored'] = df.apply(
        lambda row: 1 if row['ConvDuration'] > 0
        and row['ConvDuration'] < 10 else 0, axis=1
    )
    df['rerouted'] = df.apply(
        lambda row: 1 if row['RerouteDuration'] > 0
        and row['LastAgent'] > 0 else 0,axis=1
    )

    df['ns_ok'] = df.apply(
        lambda row: 1 if row['WaitDuration'] <= 20
        and row['handled'] == 1 else 0, axis=1
    )
    """df['gived_up'] = df.apply(
        lambda row: 1 if row['Abandon'] == 1 else 0, axis=1
    )"""

    # days_of_week = ['Monday',
    #                     'Tuesday',
    #                     'Wednesday',
    #                     'Thursday',
    #                     'Friday',
    #                     'Saturday',
    #                     'Sunday'
    #                     ]

    # activities = list(Activity.objects.all())
    activity = Activity.objects.filter(name="Mobile")[0]
    activity_codes_file = list(activity.code_file.values_list('code', flat=True))

    #for day in range(df['CallLocalTime'].min().day, df['CallLocalTime'].max().day + 1):
        # waitDuration = 0
        # wrapUpDuration = 0
        # convDuration = 0
        # day = 3
    day = df['CallLocalTime'].min().day
    day_frame = df[(df['CallLocalTime'].apply(lambda x: x.day == day))]
    day_time_stamps = day_frame['CallLocalTime'].iloc[0]
    day_date = day_time_stamps.date()
    day_name = day_time_stamps.strftime('%A')
    print('**********************Day {}****************'.format(day))
    """day_frame = df[
            (df['CallLocalTime'].apply(lambda x: x.day == day))
            & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
            & (df['CallLocalTime'].apply(lambda x: x.hour <= 20))
        ]"""
    activity_frame = day_frame[
        day_frame['LastCampaign'].isin(activity_codes_file)
    ]
    occurences = 0
    for hour in range(7, 21):
        for mn in range(0, 60, 5):
            activity_hour_day_frame = activity_frame[
                (activity_frame['CallLocalTime'].apply(lambda x: x.hour == hour))
                & (activity_frame['CallLocalTime'].apply(lambda x: x.minute >= mn))
                & (activity_frame['CallLocalTime'].apply(lambda x: x.minute < (mn + 5)))
            ]
            #for activity in activities:
            # activity = Activity.objects.filter(name="Mobile")[0]
            """if (activity.name == 'FRAN' and day_name == 'Sunday') or activity.name == 'FRAN_ALL':
                continue
            else:"""
            # activity_hour_day_frame = hour_day_frame[
            #     hour_day_frame['LastCampaign'].isin(activity_codes_file)
            # ]
            activity_incoming = activity_hour_day_frame['CallType'].sum()
            activity_handled_rows = activity_hour_day_frame[activity_hour_day_frame['handled'] == 1]
            activity_rerouted = activity_hour_day_frame[activity_hour_day_frame['rerouted'] == 1]['rerouted'].sum()
            activity_ignored = activity_hour_day_frame[activity_hour_day_frame['ignored'] == 1]['ignored'].sum()
            activity_ivr = activity_hour_day_frame['lost_ivr'].sum()
            activity_offered = activity_incoming - activity_ivr
            activity_gived_up = activity_hour_day_frame[
                (activity_hour_day_frame['WaitDuration'] > 0)
                &(activity_hour_day_frame['Overflow'] == 0)
                &(activity_hour_day_frame['LastAgent'] == 0)
            ]['CallType'].sum()
            if not activity_handled_rows.empty:
                activity_handled = activity_handled_rows['handled'].sum()
                activity_dma = round((activity_handled_rows['WaitDuration'].mean()))
                activity_dmc = round((activity_handled_rows['ConvDuration'].mean()))
                activity_dpt = round((activity_handled_rows['WrapupDuration'].mean()))
                activity_dmt = activity_dmc + activity_dpt
                # activity_qs = round(((activity_handled + activity_rerouted /(activity_incoming - activity_ignored - activity_ivr)) * 100) , 1)
                activity_qs = round(((activity_handled + activity_rerouted)/(activity_incoming - activity_ignored - activity_ivr)) * 100, 1)
                activity_sl = round(((activity_handled_rows['ns_ok'].sum()/activity_handled) * 100), 1)
                activity_sl_dealed = activity_handled_rows['ns_ok'].sum()
                activity_waitDuration = activity_handled_rows['WaitDuration'].sum()
                activity_convDuration = activity_handled_rows['ConvDuration'].sum()
                activity_wrapUpDuration = activity_handled_rows['WrapupDuration'].sum()
            else:
                activity_handled = 0
                activity_sl = 0
                activity_qs = 0
                activity_dma = 0
                activity_dmc = 0
                activity_dmt = 0
                activity_dpt = 0
                activity_waitDuration = 0
                activity_convDuration = 0
                activity_wrapUpDuration = 0
                activity_sl_dealed = 0
                print("Null handled")
            # Filling KPIs in DB
            # sleep(5)
            print('Before saving in DB')
            DetailedFlowR(
                activity=activity,
                process_date=day_date,
                incoming_calls = activity_incoming,
                offered_calls = activity_offered,
                dealed_calls = activity_handled,
                ivr = activity_ivr,
                ignored = activity_ignored,
                gived_up = activity_gived_up,
                dma = activity_dma,
                dmc = activity_dmc,
                dpt = activity_dpt,
                dmt = activity_dmt,
                sl = activity_sl,
                qs = activity_qs,
                sl_dealed_calls = activity_sl_dealed,
                wait_duration = activity_waitDuration,
                wrapup_duration = activity_wrapUpDuration,
                conv_duration = activity_convDuration,
                hour = DetailedHour.objects.filter(hour_value=hour)[0],
                mn = DetailedMin.objects.filter(mn_value=mn)[0]
            ).save()
            occurences+=1

            print("------------------Hour : {} - Min: {}------------".format(hour, mn))

            """DayKpiDuration(
                process_date = day_date,
                activity = activity,
                waitDuration = waitDuration,
                convDuration = convDuration,
                wrapUpDuration = wrapUpDuration
            ).save()"""
            # lf.activity = activity
            # lf.process_date = day_date
            # lf.incoming_calls = activity_incoming
            # lf.dealed_calls = activity_handled
            # lf.ivr = activity_ivr
            # lf.ignored = activity_ignored
            # lf.gived_up = activity_gived_up
            # lf.dma = activity_dma
            # lf.dmc = activity_dmc
            # lf.dpt = activity_dpt
            # lf.dmt = activity_dmt
            # lf.sl = activity_sl
            # lf.qs = activity_qs
            # sleep(5)
            # print(lf)
            # sleep(5)
            # lf.save()
            print('Saved activity {} of {}  stats in DB'.format(activity.name, day))
            # sleep(5)
            # break

            """print('===============Activity {} ==============='.format(activity.name))
            print('incoming: {}'.format(activity_incoming))
            print('Handled: {}'.format(activity_handled_rows['handled'].sum()))
            print('Ignored : {}'.format(activity_ignored))
            print('Lost Ivr: {}'.format(activity_ivr))
            print('Abandonned: {}'.format(activity_gived_up))
            print('Rerouted: {}'.format(activity_rerouted))
            print('DMA: {}'.format(activity_dma))
            print('DMC: {}'.format(activity_dmc))
            print('DPT: {}'.format(activity_dpt))
            print('DMT: {}'.format(activity_dmt))

            print('Total call 20s {}'.format(activity_rows['ns_ok'].sum()))
            print('SL: {}'.format(activity_sl))
            print('QS: {}'.format(activity_qs))"""
        """else:
            print('**************************************No working day for activity {}'.format(activity.name))"""
                
    print("Occurences - {}".format(occurences))
    """tmoney_incoming = tmoney_rows['CallType'].sum()

    tmoney_rows_handled = tmoney_rows[tmoney_rows['handled'] == 1]
    tmoney_ignored = tmoney_rows[tmoney_rows['ignored'] == 1]['ignored'].sum()
    tmoney_rerouted = tmoney_rows[tmoney_rows['rerouted'] == 1]['rerouted'].sum()
    tmoney_ivr = tmoney_rows['lost_ivr'].sum()
    tmoney_gived_up = tmoney_rows['gived_up'].sum()
    tmoney_dma = round(tmoney_rows_handled['WaitDuration'].mean())
    tmoney_dmc = round(tmoney_rows_handled['ConvDuration'].mean())
    tmoney_dpt = round(tmoney_rows_handled['WrapupDuration'].mean())
    tmoney_dmt = tmoney_dmc + tmoney_dpt
    qs = round((tmoney_rows_handled['handled'].sum() + tmoney_rerouted)/(tmoney_incoming - tmoney_ignored - tmoney_ivr) * 100, 1)
    sl = round((tmoney_rows_handled['ns_ok'].sum()/tmoney_rows_handled['handled'].sum()) * 100, 1)"""
    

    """lf = LittleFlow.objects.all()
    # print(lf)
    for instance in lf:
        print(instance)
        tmoney_start_date = tmoney_rows_handled['CallLocalTime'].min().day
        tmoney_end_date = tmoney_rows_handled['CallLocalTime'].max().day
        print("Tmoney Start date: {} - Tmoney End date: {}".format(tmoney_start_date==instance.start_date, tmoney_end_date==instance.end_date))
        if (instance.start_date.day == tmoney_rows_handled['CallLocalTime'].min().day
            and instance.end_date.day == tmoney_rows_handled['CallLocalTime'].max().day
            # and instance.dma == tmoney_dma
            ):
            print("------Founded-----")
            instance.incoming_calls = tmoney_incoming
            instance.ignored = tmoney_ignored
            instance.ivr = tmoney_ivr
            instance.gived_up = tmoney_gived_up
            instance.qs = qs
            instance.sl = sl
            instance.save()
        else:
            print('=========Not founded=======')"""
    

    # days = filter_days()
    """print(days)
    for day_details in days.items():
        print(day_details)"""

    """filtered_rows_camp = df[(df['CallLocalTime'].apply(lambda x: x.day == 6))
                       & (df['LastCampaign'] >= 1845)
                       & (df['LastCampaign'] <= 1847)
                       & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
                       & (df['CallLocalTime'].apply(lambda x: x.hour <= 21))]"""
    
