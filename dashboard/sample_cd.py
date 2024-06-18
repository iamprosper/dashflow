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


@csrf_exempt
def index(request):
    if request.method == 'POST':
        print("---------Posted--------")
        data_str = request.body.decode('utf-8')
        data = json.loads(data_str)
        start_date = datetime.datetime.strptime(data.get("start_date"), "%d/%m/%Y")
        end_date = datetime.datetime.strptime(data.get("end_date"), "%d/%m/%Y")
        check_flow = LittleFlow.objects.filter(process_date__range=(start_date, end_date),
                                            #    end_date = datetime.datetime.strptime(data.get("end_date"), "%d/%m/%Y"),
                                            #    activity__code = data.get("code"),
                                               activity__name = data.get("activity"))
        if (check_flow):
            print(check_flow)
            period_flow = {}
            if len(check_flow) < 2:
                period_flow = check_flow[0]
                period_flow = period_flow.__dict__
                period_flow.pop('_state')
                period_flow.pop('wait_duration')
                period_flow.pop('conv_duration')
                period_flow.pop('wrapup_duration')
                # json_str = jsonpickle.encode(period_flow)
            #    json_strr = json.dumps(check_flow)
            else:
                incoming = 0
                offered = 0
                dealed = 0
                ivr = 0
                gived_up = 0
                ignored = 0
                waitDuration = 0
                convDuration = 0
                wrapUpDuration = 0
                sl_dealed_calls = 0

                for flow in check_flow:
                    offered+= flow.offered_calls
                    incoming+= flow.incoming_calls
                    dealed+=flow.dealed_calls
                    ivr+= flow.ivr
                    gived_up+= flow.gived_up
                    ignored+=flow.ignored
                    waitDuration+= flow.wait_duration
                    convDuration+= flow.conv_duration
                    wrapUpDuration+= flow.wrapup_duration
                    sl_dealed_calls+= flow.sl_dealed_calls
                
                """days_kpi_duration = DayKpiDuration.objects.filter(
                    process_date__range=(start_date, end_date),
                    activity__name=data.get("activity")
                    )
                
                waitDuration = 0
                convDuration = 0
                wrapUpDuration = 0

                for day_kpi in days_kpi_duration:
                    waitDuration+=day_kpi.waitDuration
                    convDuration+=day_kpi.convDuration
                    wrapUpDuration+=day_kpi.wrapUpDuration"""

                
                period_flow["offered_calls"] = offered
                period_flow["incoming_calls"] = incoming
                period_flow["dealed_calls"] = dealed
                period_flow["ivr"] = ivr
                period_flow["ignored"] = ignored
                period_flow["gived_up"] = gived_up
                period_flow['qs'] = ((period_flow["dealed_calls"]/(period_flow["incoming_calls"] - period_flow['ignored'] - period_flow['ivr']))*100, 1)
                period_flow['sl'] = round(((sl_dealed_calls/dealed) * 100), 1)
                period_flow['dma'] = round(waitDuration/dealed)
                period_flow['dmc'] = round(convDuration/dealed)
                period_flow['dpt'] = round(wrapUpDuration/dealed)
                period_flow['dmt'] = period_flow['dmc'] + period_flow['dpt']
                # period_flow['sl'] = round()
            activity = data.get("activity")
            # cf_dict = unique_flow.__dict__
            print(period_flow)
            # cf_dict.pop('_state')
            cf_json = json.dumps(period_flow, default=str, indent=4)
            print(type(period_flow))
            print(cf_json)
            print(type(cf_json))
            # print("Dealed: {}".format(dealed))
            # print("Sl dealed: {}".format(sl_dealed_calls))
            return JsonResponse({"message":cf_json, "activity": activity, "graph_json": graph_json})
            # return render(request, 'results.html', {'flow': check_flow})
        
        response_data = {'message': json.dumps({'result':'Données Inexistantes'})}
        
        return JsonResponse(response_data)
        """form = FilterFlow(request.POST)
        if form.is_valid():
            data = process_data(form)
            print("Data: {}".format(data))
        return render(request, 'results.html', {'flow': data})"""
    else:
        form = FilterFlow()
    return render(request, 'dashboard/index.html', {'form': form})
