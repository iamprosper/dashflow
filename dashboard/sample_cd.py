"""for day in range(df['CallLocalTime'].min().day, df['CallLocalTime'].max().day + 1):
    # waitDuration = 0
    # wrapUpDuration = 0
    # convDuration = 0
    # day = 3
    day_frame = df[(df['CallLocalTime'].apply(lambda x: x.day == day))]
    day_time_stamps = day_frame['CallLocalTime'].iloc[0]
    day_date = day_time_stamps.date()
    day_name = day_time_stamps.strftime('%A')
    print('**********************Day {}****************'.format(day))
    #day_frame = df[
    #        (df['CallLocalTime'].apply(lambda x: x.day == day))
    #       & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
    #        & (df['CallLocalTime'].apply(lambda x: x.hour <= 20))
    #   ]
    for hour in range(7, 21):
        for mn in range(0, 60, 5):
            hour_day_frame = day_frame[
                (df['CallLocalTime'].apply(lambda x: x.hour == hour))
                & (df['CallLocalTime'].apply(lambda x: x.minute >= mn))
                & (df['CallLocalTime'].apply(lambda x: x.minute < (mn + 5)))
            ]
            for activity in activities:
                if (activity.name == 'FRAN' and day_name == 'Sunday') or activity.name == 'FRAN_ALL':
                    continue
                else:
                    activity_codes_file = list(activity.code_file.values_list('code', flat=True))
                    activity_rows = hour_day_frame[
                        hour_day_frame['LastCampaign'].isin(activity_codes_file)
                    ]
                    activity_incoming = activity_rows['CallType'].sum()
                    activity_handled_rows = activity_rows[activity_rows['handled'] == 1]
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
                    activity_ignored = activity_rows[activity_rows['ignored'] == 1]['ignored'].sum()
                    activity_rerouted = activity_rows[activity_rows['rerouted'] == 1]['rerouted'].sum()
                    activity_ivr = activity_rows['lost_ivr'].sum()
                    activity_offered = activity_incoming - activity_ivr
                    activity_gived_up = activity_rows[
                        (activity_rows['WaitDuration'] > 0)
                        &(activity_rows['Overflow'] == 0)
                        &(activity_rows['LastAgent'] == 0)
                    ]['CallType'].sum()
                    # Filling KPIs in DB
                    # sleep(5)
                    print('Before saving in DB')
                    DetailedFlow(
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
                    ).save()"""