import csv
import datetime
import json
from time import sleep
import chardet
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.templatetags import static
import jsonpickle
import numpy as np
import pandas as pd
from django.views.decorators.csrf import csrf_exempt


from .models import Flow, LittleFlow, UploadedFile, Activity

from .forms import FileUploadForm, FilterFlow
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your views here.
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == "XMLHttpRequest"

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
            if len(check_flow < 2):
                period_flow = check_flow[0]
                period_flow = period_flow.__dict__
                period_flow.pop('_state')
                # json_str = jsonpickle.encode(period_flow)
            #    json_strr = json.dumps(check_flow)
            else:
                incoming = 0
                offered = 0
                dealed = 0
                ivr = 0
                gived_up = 0
                ignored = 0

                for flow in check_flow:
                    offered+= flow.offered_calls
                    incoming+= flow.incoming_calls
                    dealed+=flow.dealed_calls
                    ivr+= flow.ivr
                    gived_up+= flow.gived_up
                    ignored+=flow.ignored
                
                period_flow["offered"] = offered
                period_flow["incoming"] = incoming
                period_flow["ivr"] = ivr
                period_flow["gived_up"] = gived_up
                period_flow["offered"] = offered
                period_flow['qs'] = round((period_flow['dealed']/(period_flow['incoming'] - period_flow['ignored'] - period_flow['ivr']))*100, 1)
                # period_flow['sl'] = round()
            activity = data.get("activity")
            # cf_dict = unique_flow.__dict__
            print(period_flow)
            # cf_dict.pop('_state')
            cf_json = json.dumps(period_flow, default=str, indent=4)
            print(type(period_flow))
            print(cf_json)
            print(type(cf_json))
            return JsonResponse({"message":cf_json, "activity": activity})
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

def process_data(form):
    start_date = form.cleaned_data["start_date"]
    end_date = form.cleaned_data["end_date"]
    activity = form.cleaned_data["activity"]
    data = LittleFlow.objects.filter(start_date=start_date, end_date=end_date, activity=activity)
    if data:
        return data[0]
    return data


def fill_db(request):
    load_inbound("media/uploads/2024-01.csv")
    return render(request, 'dashboard/fill.html')

def upload_file(request):
    # For uploading the CSV file
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('process_file')
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})

def upload_success(request):
    return render(request, 'success.html')

def lazy_display(request):
    return render(request, 'lazy_display.html')

def stream_csv_data(file_path):

    # Getting the csv file encoding
    with open(file_path, 'rb') as f:
        encoding = chardet.detect(f.read())['encoding']
    
    print("Encoding {}".format(encoding))
    
    # Reading the file with pandas library
    df = pd.read_csv(file_path, encoding=encoding)

    print("Path: {}".format(file_path))

    # Adding more column for analysis
    handled_values =  df["ConvDuration"].apply(lambda x: 1 if x >=10 else 0)
    lost_ivr_values = df.apply(lambda row: 1 if row['ConvDuration'] == 0
                              and row["WaitDuration"] == 0
                              and row["OverflowDuration"] == 0 else 0, axis=1)
    #dates_values = df["CallLocalTime"].apply(lambda x: x.split(' ')[0])
    #hours_values = df["CallLocalTime"].apply(lambda x: x.split(' ')[1].split('.')[0])
    datetime_values_str = df["CallLocalTime"].apply(lambda x: x.split('.')[0])
    datetime_py = datetime_values_str.apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
    date_py = datetime_py.apply(lambda x: x.date())
    dates_values = date_py.apply(lambda x: x.strftime("%Y-%m-%d"))
    hours_values = datetime_py.apply(lambda x: "{:02d}:{:02d}:{:02d}".format(x.hour, x.minute, x.second))
    #date_py = datetime.datetime.strptime(datetime_values_str, "%Y-%m-%d %H:%M:%S").date()
    """datetime_values_date_str = datetime_values_str.apply(lambda x: x.split(' ')).apply(lambda x: x[0])
    datetime_values_hour_str = datetime_values_str.apply(lambda x: x.split(' ')).apply(lambda x: x[1])"""

    #datetime_values_py = datetime.datetime.strptime(datetime_values_str, "%Y-%m-%d %H:%M:%S")
    """date_str = date_py.strftime("%Y-%m-%d")
    hour_str = date_py"""

    # Adding new column to the csv file (optional)
    df.insert(5, 'handled', handled_values)
    df.insert(6, 'lost_ivr', lost_ivr_values)
    df.insert(9, 'dates', dates_values)
    df.insert(10, 'hours', hours_values)
    df['hour'] = pd.to_datetime(df['hours'], format='%H:%M:%S').dt.hour


    # Filtering rows to obtain precise call values
    filtered_rows = df[(df['hour'] >=7 ) &(df['hour'] <= 21)
                       & (df['handled'] == 1)
                       & (df['LastAgent'] > 0)
                       & (df['LastCampaign'] >= 1845)
                       & (df['LastCampaign'] <= 1847)
                       ]
    
    days_filter = filtered_rows['dates'].apply(lambda x: x[8:])
    filtered_rows['days'] = days_filter.apply(lambda x: int(x))

    min_day = filtered_rows['days'].min()
    max_day = filtered_rows['days'].max()

    for day in range(min_day, max_day +1):
        day_filter = filtered_rows[filtered_rows['days'] == day]
        dma = round(day_filter["WaitDuration"].mean())
        dmc = round(day_filter["ConvDuration"].mean())
        dpt = round(day_filter["WrapupDuration"].mean())
        dmt = dmc + dpt
        dealed = day_filter["CallType"].sum()

        print("""Donées du {}
              Traités: {}
              DMA: {}
              DMC: {}
              DPT: {}
              DMT: {}
              """.format(day, dealed, dma, dmc, dpt, dmt))
        return
    """for day in range(min_day, max_day + 1):
        filte"""
    # Doing operations (sum, average...)
    typologies_rows = filtered_rows.dropna(subset=["StatusText"])['StatusText']
    typologies_dict = {}
    for typologie in typologies_rows:
        if typologies_dict.get(typologie):
            typologies_dict[typologie] += 1
        else:
            typologies_dict[typologie] = 1
    
    sorted_typologies_dict = dict(sorted(typologies_dict.items(), key= lambda x:x[1], reverse=True))
    dmc = round(filtered_rows['ConvDuration'].mean())
    dma = round(filtered_rows['WaitDuration'].mean())
    dpt = round(filtered_rows['WrapupDuration'].mean())
    dmt = dmc + dpt
    dealed = filtered_rows['CallType'].sum()
    max_date = filtered_rows['dates'].max()
    min_date = filtered_rows['dates'].min()
    max_hour = filtered_rows['hour'].max()
    min_hour = filtered_rows['hour'].min()
    """for date in df['dates']:
        print(date)"""

    lFlow = LittleFlow()
    lFlow.start_date = min_date
    lFlow.end_date = max_date
    lFlow.dealed_calls = dealed
    lFlow.dma = dma
    lFlow.dmc = dmc
    lFlow.dpt = dpt
    lFlow.dmt = dmt
    lFlow.activity = Activity.objects.filter(code_file__code=filtered_rows['LastCampaign'].iloc[0])[0]
    print(lFlow.activity)
    lf = LittleFlow.objects.filter(start_date=min_date, end_date=max_date, activity=lFlow.activity).first()
    if not lf:
        lFlow.save()

    # lFlow.activity

    print("Max date: {} \nMin date: {} \nMax hour: {} \nMin hour: {}".format(max_date, min_date, max_hour, min_hour))
    #filtered_rows.to_excel('data.xlsx',index=False)
    return ([dmt, dmc, dma, dpt, dealed, sorted_typologies_dict.items()])
    """with open(file_path, 'r', newline='', encoding=encoding) as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            yield ','.join(row) + '\n'"""


def process_file(request):
    uploaded_file = UploadedFile.objects.last()
    if uploaded_file:
        file_path = uploaded_file.file.path
        dmt, dmc, dma, dpt, dealed, typologies = stream_csv_data(file_path)
        """with open(file_path, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)
            # yield header
            data = [row for row in reader]"""
            # for row in reader:
            #     yield ','.join(row) + '\n'
        
        response = render(request, 'success.html', {'dmt': round(dmt),
                                                    'dmc': round(dmc),
                                                    'dma': round(dma),
                                                    'dpt': round(dpt),
                                                    'dealed': dealed,
                                                    'typologies': typologies
                                                    })
        # response = StreamingHttpResponse(stream_csv_data(file_path), content_type='text/csv')
        # response['Content-Disposition'] = 'attachment; filename="data.csv"'
        return response
        
        """df = pandas.read_csv(file_path, encoding='utf-32-be')
        writer = pandas.ExcelWriter()
        excel_data = df.to_excel('ext_29_04.xlsx', sheet_name="Data", index=False)
        response = HttpResponse(excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="ext_29_04.xlsx"'
        return response"""
        # return render(request, 'process.html', {'header': header, 'data': data})
    else:
        return HttpResponse("No CSV File uploaded")
        # return render(request, 'process.html', {'data': []})

"""def process_csv(request):
    try:
        if request.method == 'POST' and request.FILES['csv_file']:
            csv_file = request.FILES['csv_file']
            csv_content = csv_file.read()
            # static_url = static('csv_file.csv')
            
            return render(request, 'results.html')
            # data_list = []

            # encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii', 'utf-32']
            # decoded_content = None

            for encoding in encodings:
                try:
                    deconded_content = csv_content.decode(encoding, errors='ignore')
                    break
                except UnicodeDecodeError as ue:
                    print("UnicodeDecodeError found {}".format(ue))
                    continue
            for name, uploaded_file in request.FILES.items():
                decoded_content = uploaded_file.read().decode('utf-8', errors='ignore').splitlines()
                reader = csv.reader(uploaded_file)
                data = list(reader)
                print("Name: {}".format(name))
                print(" {}".format(data))
                for row in data:
                    for cell in row:
                        print("{}".format(cell))
                # data_list.append({'file_name': name, 'data': data})
                return render(request, 'results.html', {'data': data, 'name': name})

            if decoded_content is not None:
                reader = csv.reader(decoded_content.splitlines(), delimiter=',')
                data = list(reader)


            decoded_file = csv_file.read().decode('utf-32').splitlines()
            reader = csv.reader(decoded_file)

            data = []
            for row in reader:
                data.append(row)
        with open("csv_file.csv", 'r', newline='') as file:
            reader = csv.reader(file)
        for row in reader:
            print(row)
        return render(request, 'upload_form.html')
            
    except Exception as e:
        print("An error occured : {}".format(e))
        return render(request, 'upload_form.html')"""


"""def real_process_data(request):
    channel_layer = get_channel_layer()

    for i in range(5):
        sleep(2)
        data = {
            "message": f'Processed data {i+1}'
        }
        async_to_sync(channel_layer.group_send)(
            'data_group',
            {
                'type': 'send_data',
                'data': data
            }
        )
    return HttpResponse('Data processing completed')"""

def load_inbound(file_path):
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

    for day in range(df['CallLocalTime'].min().day, df['CallLocalTime'].max().day + 1):
    # day = 3
        day_frame = df[
                (df['CallLocalTime'].apply(lambda x: x.day == day))
                & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
                & (df['CallLocalTime'].apply(lambda x: x.hour <= 20))
            ]
        day_time_stamps = day_frame['CallLocalTime'].iloc[0]
        day_date = day_time_stamps.date()
        day_name = day_time_stamps.strftime('%A')

        print('**********************Day {}****************'.format(day))

        activities = list(Activity.objects.all())

        for activity in activities:
            if activity.name == 'FRAN' and day_name == 'Sunday':
                continue
            else:
                activity_codes_file = list(activity.code_file.values_list('code', flat=True))
                activity_rows = day_frame[
                    day_frame['LastCampaign'].isin(activity_codes_file)
                ]
                activity_incoming = activity_rows['CallType'].sum()
                activity_handled_rows = activity_rows[activity_rows['handled'] == 1]
                if not activity_handled_rows.empty:
                    activity_handled = activity_handled_rows['handled'].sum()
                    activity_ignored = activity_rows[activity_rows['ignored'] == 1]['ignored'].sum()
                    activity_rerouted = activity_rows[activity_rows['rerouted'] == 1]['rerouted'].sum()
                    activity_ivr = activity_rows['lost_ivr'].sum()
                    activity_offered = activity_incoming - activity_ivr
                    activity_gived_up = activity_rows[
                        (activity_rows['WaitDuration'] > 0)
                        &(activity_rows['Overflow'] == 0)
                        &(activity_rows['LastAgent'] == 0)
                    ]['CallType'].sum()
                    activity_dma = round((activity_handled_rows['WaitDuration'].mean()))
                    activity_dmc = round((activity_handled_rows['ConvDuration'].mean()))
                    activity_dpt = round((activity_handled_rows['WrapupDuration'].mean()))
                    activity_dmt = activity_dmc + activity_dpt
                    # activity_qs = round(((activity_handled + activity_rerouted /(activity_incoming - activity_ignored - activity_ivr)) * 100) , 1)
                    activity_qs = round(((activity_handled + activity_rerouted)/(activity_incoming - activity_ignored - activity_ivr)) * 100, 1)
                    activity_sl = round(((activity_handled_rows['ns_ok'].sum()/activity_handled) * 100), 1)
                    activity_sl_dealed = activity_handled_rows['ns_ok'].sum()
                    # Filling KPIs in DB
                    # sleep(5)
                    print('Before saving in DB')
                    LittleFlow(
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
                        sl_dealed_calls = activity_sl_dealed
                    ).save()
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
                else:
                    print('**************************************No working day for activity {}'.format(activity.name))
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
    


# df = load_inbound("media/uploads/05-2024.csv")
"""def filter_days():
    days = {}
    for day in range(df['CallLocalTime'].min().day, df['CallLocalTime'].max().day + 1):
        tmoney_rows = df[
            (df['CallLocalTime'].apply(lambda x: x.day == day))
            & (df['LastCampaign'].isin([1845, 1846, 1847]))
            & (df['CallLocalTime'].apply(lambda x: x.hour >= 7))
            & (df['CallLocalTime'].apply(lambda x: x.hour <= 21))
        ]

        tmoney_rows_incoming = tmoney_rows['CallType'].sum()
        tmoney_rows_lost_ivr= tmoney_rows['lost_ivr'].sum()
        tmoney_rows_handled = tmoney_rows[tmoney_rows['handled'] == 1]
        tmoney_rows_dma = round(tmoney_rows_handled['WaitDuration'].mean())
        tmoney_rows_dmc = round(tmoney_rows_handled['ConvDuration'].mean())
        tmoney_rows_dpt = round(tmoney_rows_handled['WrapupDuration'].mean())
        tmoney_rows_dmt = tmoney_rows_dmc + tmoney_rows_dpt

        tmoney_stats = {
            'incoming': tmoney_rows_incoming,
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
        fixe_rows_incoming = fixe_rows['CallType'].sum()
        fixe_rows_lost_ivr= fixe_rows['lost_ivr'].sum()
        fixe_rows_handled = fixe_rows[fixe_rows['handled'] == 1]
        fixe_rows_dma = round(fixe_rows_handled['WaitDuration'].mean())
        fixe_rows_dmc = round(fixe_rows_handled['ConvDuration'].mean())
        fixe_rows_dpt = round(fixe_rows_handled['WrapupDuration'].mean())
        fixe_rows_dmt = fixe_rows_dmc + fixe_rows_dpt

        fixe_stats = {
            'incoming': fixe_rows_incoming,
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
        mobile_rows_incoming = mobile_rows['CallType'].sum()
        mobile_rows_lost_ivr= mobile_rows['lost_ivr'].sum()
        mobile_rows_handled = mobile_rows[mobile_rows['handled'] == 1]
        mobile_rows_dma = round(mobile_rows_handled['WaitDuration'].mean())
        mobile_rows_dmc = round(mobile_rows_handled['ConvDuration'].mean())
        mobile_rows_dpt = round(mobile_rows_handled['WrapupDuration'].mean())
        mobile_rows_dmt = mobile_rows_dmc + mobile_rows_dpt

        mobile_stats = {
            'incoming': mobile_rows_incoming,
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
        pdv_rows_incoming = pdv_rows['CallType'].sum()
        pdv_rows_lost_ivr= pdv_rows['lost_ivr'].sum()
        pdv_rows_handled = pdv_rows[pdv_rows['handled'] == 1]
        pdv_rows_dma = round(pdv_rows_handled['WaitDuration'].mean())
        pdv_rows_dmc = round(pdv_rows_handled['ConvDuration'].mean())
        pdv_rows_dpt = round(pdv_rows_handled['WrapupDuration'].mean())
        pdv_rows_dmt = pdv_rows_dmc + pdv_rows_dpt

        pdv_stats = {
            'incoming': pdv_rows_incoming,
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
            fran_rows_incoming = fran_rows['CallType'].sum()
            fran_rows_lost_ivr= fran_rows['lost_ivr'].sum()
            fran_rows_handled = fran_rows[fran_rows['handled'] == 1]
            if not fran_rows_handled.empty:
                fran_rows_dma = round(fran_rows_handled['WaitDuration'].mean())
                fran_rows_dmc = round(fran_rows_handled['ConvDuration'].mean())
                fran_rows_dpt = round(fran_rows_handled['WrapupDuration'].mean())
            # fran_rows_dmt = fran_rows_dmc + fran_rows_dpt

                fran_stats = {
                    'incoming': fran_rows_incoming,
                    'lost_ivr': fran_rows_lost_ivr,
                    'dma': fran_rows_dma,
                    'dmc': fran_rows_dmc,
                    'dpt': fran_rows_dpt,
                    # 'dmt': fran_rows_dmt
                }
            else:
                fran_stats = {}
    
            days[day] = {
                'tmoney':tmoney_stats,
                'fixe':fixe_stats,
                'mobile':mobile_stats,
                'fran':fran_stats,
                'pdv':pdv_stats,
            }
        else:
            days[day] = {
                'tmoney':tmoney_stats,
                'fixe':fixe_stats,
                'mobile':mobile_stats,
                'pdv':pdv_stats,
            }
        print("Loaded")
        print("Day {} - {}".format(df[df['CallLocalTime'].apply(lambda x: x.day == day)]
                                   ['CallLocalTime'].iloc[0].day,
                                   day
                                   ))
        print(days[day])
        print("==================")

    return days        
"""