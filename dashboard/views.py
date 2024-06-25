import csv
import datetime
import glob
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


from .models import DetailedFlow, DetailedFlowR, DetailedHour, DetailedMin, Flow, LittleFlow, UploadedFile, Activity

from .forms import FileUploadForm, FilterFlow
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import plotly.graph_objs as go

# global check_flow
global diff_date

#Initializing bars for graph visualization
def reset_bars():
    global dl_dict
    dl_dict = {
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        11: 0,
        12: 0,
        13: 0,
        14: 0,
        15: 0,
        16: 0,
        17: 0,
        18: 0,
        19: 0,
        20: 0
    }
    
    global sl_dict
    sl_dict = {
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        11: 0,
        12: 0,
        13: 0,
        14: 0,
        15: 0,
        16: 0,
        17: 0,
        18: 0,
        19: 0,
        20: 0
    }
    
    global ic_dict
    ic_dict = {
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        11: 0,
        12: 0,
        13: 0,
        14: 0,
        15: 0,
        16: 0,
        17: 0,
        18: 0,
        19: 0,
        20: 0
    }
    
    global ivr_dict
    ivr_dict = {
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        11: 0,
        12: 0,
        13: 0,
        14: 0,
        15: 0,
        16: 0,
        17: 0,
        18: 0,
        19: 0,
        20: 0
    }
    
    global dma_dict
    dma_dict = {
        7: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        8: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        9: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        10: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        11: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        12: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        13: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        14: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        15: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        16: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        17: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        18: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        19: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        },
        20: {
            "waitDuration":0,
            "dealed": 0,
            "dma": 0
        }
    }
    
    global dmc_dict
    dmc_dict = {
        7: {
            "convDuration":0,
            "dmc": 0
        },
        8: {
            "convDuration":0,
            "dmc": 0
        },
        9: {
            "convDuration":0,
            "dmc": 0
        },
        10: {
            "convDuration":0,
            "dmc": 0
        },
        11: {
            "convDuration":0,
            "dmc": 0
        },
        12: {
            "convDuration":0,
            "dmc": 0
        },
        13: {
            "convDuration":0,
            "dmc": 0
        },
        14: {
            "convDuration":0,
            "dmc": 0
        },
        15: {
            "convDuration":0,
            "dmc": 0
        },
        16: {
            "convDuration":0,
            "dmc": 0
        },
        17: {
            "convDuration":0,
            "dmc": 0
        },
        18: {
            "convDuration":0,
            "dmc": 0
        },
        19: {
            "convDuration":0,
            "dmc": 0
        },
        20: {
            "convDuration":0,
            "dmc": 0
        }
    }
    
    global dpt_dict
    dpt_dict = {
        7: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        8: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        9: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        10: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        11: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        12: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        13: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        14: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        15: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        16: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        17: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        18: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        19: {
            "wrapUpDuration":0,
            "dpt": 0
        },
        20: {
            "wrapUpDuration":0,
            "dpt": 0
        }
    }
    
    global day_bar
    day_bar = {
        "Monday": {
            "incoming": 0,
            "dealed": 0,
            "sl_dealed_calls": 0,
            "ivr": 0,
            "waitDuration": 0,
            "convDuration": 0,
            "wrapUpDuration": 0,
            # "dma": 0
        },
        "Tuesday": {
            "incoming": 0,
            "dealed": 0,
            "sl_dealed_calls": 0,
            "ivr": 0,
            "waitDuration": 0,
            "convDuration": 0,
            "wrapUpDuration": 0,
            # "dma": 0
        },
        "Wednesday": {
            "incoming": 0,
            "dealed": 0,
            "sl_dealed_calls": 0,
            "ivr": 0,
            "waitDuration": 0,
            "convDuration": 0,
            "wrapUpDuration": 0,
            # "dma": 0
        },
        "Thursday": {
            "incoming": 0,
            "dealed": 0,
            "sl_dealed_calls": 0,
            "ivr": 0,
            "waitDuration": 0,
            "convDuration": 0,
            "wrapUpDuration": 0,
            # "dma": 0
        },
        "Friday": {
            "incoming": 0,
            "dealed": 0,
            "sl_dealed_calls": 0,
            "ivr": 0,
            "waitDuration": 0,
            "convDuration": 0,
            "wrapUpDuration": 0,
            # "dma": 0
        },
        "Saturday": {
            "incoming": 0,
            "dealed": 0,
            "sl_dealed_calls": 0,
            "ivr": 0,
            "waitDuration": 0,
            "convDuration": 0,
            "wrapUpDuration": 0,
            # "dma": 0
        },
        "Sunday": {
            "incoming": 0,
            "dealed": 0,
            "sl_dealed_calls": 0,
            "ivr": 0,
            "waitDuration": 0,
            "convDuration": 0,
            "wrapUpDuration": 0,
            # "dma": 0
        },
    }

    global ic_bar
    ic_bar = []

    global dl_bar
    dl_bar = []

    global ivr_bar
    ivr_bar = []

    global sl_line
    sl_line = []

    global dma_bar
    dma_bar = []
    
    global dmc_bar
    dmc_bar = []

    global dpt_bar
    dpt_bar = []

    reset_vars()

#Reseting vars for kpi computing
def reset_vars():
    global ic_var
    ic_var = 0

    global ivr_var
    ivr_var = 0

    global dl_var
    dl_var = 0

    global sl_var
    sl_var = 0

    global wait_var
    wait_var = 0

    global conv_var
    conv_var = 0

    global wrap_var
    wrap_var = 0

#Graph visualisation for Calls and Sl
def graph(activity, ic_bar, dl_bar, ivr_bar, sl_line, distrib):
    #Default time for 5 min review
    hr = 7

    categories_min_5 = [f"{hr}h - 00 min",
                  f"{hr}h - 05 min",
                  f"{hr}h - 10 min",
                  f"{hr}h - 15 min",
                  f"{hr}h - 20 min",
                  f"{hr}h - 25 min",
                  f"{hr}h - 30 min",
                  f"{hr}h - 35 min",
                  f"{hr}h - 40 min",
                  f"{hr}h - 45 min",
                  f"{hr}h - 50 min",
                  f"{hr}h - 55 min"]
    
    categories_hour = ["7h",
                  "8h",
                  "9h",
                  "10h",
                  "11h",
                  "12h",
                  "13h",
                  "14h",
                  "15h",
                  "16h",
                  "17h",
                  "18h",
                  "19h",
                  "20h"]
    
    categories_day = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]
    
    if distrib == 60:
        category = categories_hour
    elif distrib == 5:
        category = categories_min_5
    else:
        # Clear unnecessaries days for day visualization
        for day in day_bar.keys():
            if (day_bar[day]["dealed"] == 0):
                categories_day.remove(day)
        category = categories_day
    
    print(ic_bar)
    
    #Defining calls charts
    ic_trace_bar = go.Bar(
        x=category,
        y=ic_bar,
        name="Ic Calls Chart"
    )

    dealed_trace_bar = go.Bar(
        x=category,
        y=dl_bar,
        name="Dealed Calls Chart"
    )

    ivr_trace_bar = go.Bar(
        x=category,
        y=ivr_bar,
        name="Ivr Calls Chart"
    )

    sl_trace_line = go.Scatter(
        x=category,
        y=sl_line,
        mode='lines+markers',
        name='Sl Line'
    )

    data = [ic_trace_bar, dealed_trace_bar, ivr_trace_bar, sl_trace_line]

    layout = go.Layout(
        title='Graph incoming calls + SL',
        xaxis=dict(title="Heures"),
        yaxis=dict(title="Effectif")
    )

    fig = go.Figure(data=data, layout=layout)

    graph_json = fig.to_json()

    # context = {
    #     'graph_json': graph_json
    # }

    # return render(request, 'dashboard/graphs.html', context)
    # print(graph_json)
    return graph_json

#Graph visualisation for dms
def dm_graph(activity, dma_bar, dmc_bar, dpt_bar):
    hr = 7
    categories_min_5 = [f"{hr}h - 00 min",
                  f"{hr}h - 05 min",
                  f"{hr}h - 10 min",
                  f"{hr}h - 15 min",
                  f"{hr}h - 20 min",
                  f"{hr}h - 25 min",
                  f"{hr}h - 30 min",
                  f"{hr}h - 35 min",
                  f"{hr}h - 40 min",
                  f"{hr}h - 45 min",
                  f"{hr}h - 50 min",
                  f"{hr}h - 55 min"]
    
    categories_hours = ["7h",
                  "8h",
                  "9h",
                  "10h",
                  "11h",
                  "12h",
                  "13h",
                  "14h",
                  "15h",
                  "16h",
                  "17h",
                  "18h",
                  "19h",
                  "20h"]
    
    categories_day = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    if distrib == 60:
        category = categories_hours
    elif distrib == 5:
        category = categories_min_5
    else:
        #Clear unnecessaries days for day visualization
        for day in day_bar.keys():
            if(day_bar[day]["dealed"] == 0):
                categories_day.remove(day)
    
    #Defining dms charts
    dma_line = go.Scatter(
        x=categories_hours,
        y=dma_bar,
        name="DMA Chart"
    )

    dmc_line = go.Scatter(
        x=categories_hours,
        y=dmc_bar,
        name="DMC Chart"
    )

    dpt_line = go.Scatter(
        x=categories_hours,
        y=dpt_bar,
        name="DPT Chart"
    )


    data = [dma_line, dmc_line, dpt_line]

    layout = go.Layout(
        title='Graph DMs',
        xaxis=dict(title="Heures"),
        yaxis=dict(title="Durées")
    )

    fig = go.Figure(data=data, layout=layout)

    dm_graph_json = fig.to_json()

    # context = {
    #     'graph_json': graph_json
    # }

    # print("Ic_calls {}".format(DMA) )
    # return render(request, 'dashboard/graphs.html', context)
    # print(graph_json)
    return dm_graph_json


def compute_graph_data(day_interval, time_interval, hour_value):
    # global check_flow
    # global ic_bar
    # global ic_var
    # global ivr_var
    # global sl_var
    # global dl_var
    # global wait_var
    # global conv_var
    # global wrap_var
    # global ic_bar
    # global dl_bar
    # global sl_line
    # global dma_bar
    # global dmc_bar
    # global dpt_bar
    # global dma_dict
    # global dmc_dict
    # global dpt_dict
    # global sl_dict
    # global dl_dict
    # global ic_dict
    if day_interval == 0 and time_interval == 5:
        ic_bar.append(ic_var)
        dl_bar.append(dl_var)
        ivr_bar.append(ivr_var)
        sl_line.append(sl_var)
        if (dl_var != 0):
            dma_bar.append(round(wait_var/dl_var))
            dmc_bar.append(round(conv_var/dl_var))
            dpt_bar.append(round(wrap_var/dl_var))
        else:
            dma_bar.append(0)
            dmc_bar.append(0)
            dpt_bar.append(0)
    else:
        if time_interval == 60:
            ic_dict[hour_value] += ic_var
            dl_dict[hour_value] += dl_var
            ivr_dict[hour_value] += ivr_var
            sl_dict[hour_value] += sl_var
            
            dma_dict[hour_value]["waitDuration"]+=wait_var
            dmc_dict[hour_value]["convDuration"]+=conv_var
            dpt_dict[hour_value]["wrapUpDuration"]+=wrap_var
            
            dma_dict[hour_value]["dealed"] += dl_var
    ic_var = 0
    dl_var = 0
    ivr_var = 0
    sl_var = 0
    wait_var = 0
    conv_var = 0
    wrap_var = 0

    responseData = {}
    return JsonResponse(responseData)

def update_graphs_visual(request):
    if request.method == 'POST':
        print("------Visualising-------")
        data_str = request.body.decode('utf-8')
        data = json.loads(data_str)
        time_view = (int) (data.get("code"))
        compute_graph_data(distrib, time_view)
    
# Create your views here.
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == "XMLHttpRequest"

@csrf_exempt
def index(request):
    if request.method == 'POST':
        global check_flow
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

@csrf_exempt
def index_r(request):
    if request.method == 'POST':
        global diff_date
        global distrib
        global categories_day
        categories_day = []
        print("---------Posted--------")
        data_str = request.body.decode('utf-8')
        data = json.loads(data_str)
        start_date = datetime.datetime.strptime(data.get("start_date"), "%d/%m/%Y")
        end_date = datetime.datetime.strptime(data.get("end_date"), "%d/%m/%Y")
        """check_flow = LittleFlow.objects.filter(process_date__range=(start_date, end_date),
                                            #    end_date = datetime.datetime.strptime(data.get("end_date"), "%d/%m/%Y"),
                                            #    activity__code = data.get("code"),
                                               activity__name = data.get("activity"))"""
        distrib = (int)(data.get("time_interval"))
        check_flow = DetailedFlowR.objects.filter(process_date__range=(start_date, end_date),
                                            #    end_date = datetime.datetime.strptime(data.get("end_date"), "%d/%m/%Y"),
                                            #    activity__code = data.get("code"),
                                               activity__name = data.get("activity"))
        
        # graph_json = ""
        # dl_dict = {}
        # sl_dict = {}
        # ivr_dict = {}
        # 
        # global dl_dict
        # global sl_dict
        # global ivr_dict
        # global ic_dict
        diff_date = end_date - start_date
        print("Distrib {} \n Diff date {}".format(distrib, diff_date.days))
        # distrib = 0
        # if diff_date.days > 0:
        #     distrib = 2
        # else:
        #     distrib = diff_date 
        # if diff_date.days > 0:
        
        """# When we have many days, we have to collect calls by bours (for dms calcultations)
        dl_dict = {
            7: 0,
            8: 0,
            9: 0,
            10: 0,
            11: 0,
            12: 0,
            13: 0,
            14: 0,
            15: 0,
            16: 0,
            17: 0,
            18: 0,
            19: 0,
            20: 0
        }
        sl_dict = {
            7: 0,
            8: 0,
            9: 0,
            10: 0,
            11: 0,
            12: 0,
            13: 0,
            14: 0,
            15: 0,
            16: 0,
            17: 0,
            18: 0,
            19: 0,
            20: 0
        }
        ic_dict = {
            7: 0,
            8: 0,
            9: 0,
            10: 0,
            11: 0,
            12: 0,
            13: 0,
            14: 0,
            15: 0,
            16: 0,
            17: 0,
            18: 0,
            19: 0,
            20: 0
        }
        ivr_dict = {
            7: 0,
            8: 0,
            9: 0,
            10: 0,
            11: 0,
            12: 0,
            13: 0,
            14: 0,
            15: 0,
            16: 0,
            17: 0,
            18: 0,
            19: 0,
            20: 0
        }
        dma_dict = {
            7: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            8: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            9: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            10: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            11: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            12: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            13: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            14: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            15: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            16: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            17: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            18: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            19: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            },
            20: {
                "waitDuration":0,
                "dealed": 0,
                "dma": 0
            }
        }
        dmc_dict = {
            7: {
                "convDuration":0,
                "dmc": 0
            },
            8: {
                "convDuration":0,
                "dmc": 0
            },
            9: {
                "convDuration":0,
                "dmc": 0
            },
            10: {
                "convDuration":0,
                "dmc": 0
            },
            11: {
                "convDuration":0,
                "dmc": 0
            },
            12: {
                "convDuration":0,
                "dmc": 0
            },
            13: {
                "convDuration":0,
                "dmc": 0
            },
            14: {
                "convDuration":0,
                "dmc": 0
            },
            15: {
                "convDuration":0,
                "dmc": 0
            },
            16: {
                "convDuration":0,
                "dmc": 0
            },
            17: {
                "convDuration":0,
                "dmc": 0
            },
            18: {
                "convDuration":0,
                "dmc": 0
            },
            19: {
                "convDuration":0,
                "dmc": 0
            },
            20: {
                "convDuration":0,
                "dmc": 0
            }
        }
        dpt_dict = {
            7: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            8: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            9: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            10: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            11: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            12: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            13: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            14: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            15: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            16: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            17: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            18: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            19: {
                "wrapUpDuration":0,
                "dpt": 0
            },
            20: {
                "wrapUpDuration":0,
                "dpt": 0
            }
        }
        """
    
        reset_bars()
        if (check_flow):
            # print(check_flow)

            period_flow = {}
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
            ic_bar = []
            dl_bar = []
            ivr_bar = []
            sl_line = []
            dma_bar = []
            dmc_bar = []
            dpt_bar = []
            ic_var = 0
            dl_var = 0
            ivr_var = 0
            sl_var = 0
            conv_var = 0
            wait_var = 0
            wrap_var = 0

            ic_5_var = 0
            dl_5_var = 0
            ivr_5_var = 0
            sl_5_var = 0
            conv_5_var = 0
            wrap_5_var = 0
            wait_5_var = 0

            """if len(check_flow) <= 168:
                # period_flow = check_flow[0]
                period_flow = period_flow.__dict__
                period_flow.pop('_state')
                period_flow.pop('wait_duration')
                period_flow.pop('conv_duration')
                period_flow.pop('wrapup_duration')"""
            # count_flow = 0
            for flow in check_flow:
                # count_flow
                incoming += flow.incoming_calls
                ic_var += flow.incoming_calls
                ivr += flow.ivr
                ivr_var += flow.ivr
                dealed += flow.dealed_calls
                dl_var += flow.dealed_calls
                sl_dealed_calls += flow.sl_dealed_calls
                sl_var += flow.sl_dealed_calls
                conv_var += flow.conv_duration
                wait_var += flow.wait_duration
                wrap_var += flow.wrapup_duration

                ic_5_var = flow.incoming_calls
                dl_5_var = flow.dealed_calls
                ivr_5_var = flow.ivr
                sl_5_var = flow.sl_dealed_calls
                wait_5_var = flow.wait_duration
                wrap_5_var = flow.wrapup_duration
                conv_5_var = flow.conv_duration
                
                if diff_date.days == 0 and distrib == 5 and flow.hour.hour_value == 7:
                    ic_bar.append(ic_5_var)
                    dl_bar.append(dl_5_var)
                    ivr_bar.append(ivr_5_var)
                    sl_line.append(sl_5_var)
                    if (dl_5_var != 0):
                        dma_bar.append(round(wait_5_var/dl_5_var))
                        dmc_bar.append(round(conv_5_var/dl_5_var))
                        dpt_bar.append(round(wrap_5_var/dl_5_var))
                    else:
                        dma_bar.append(0)
                        dmc_bar.append(0)
                        dpt_bar.append(0)
                    print("------------------5min----------------")

                elif flow.mn.mn_value == 55:
                    # visualize(
                    #     flow,
                    #     distrib,
                    #     ic_var,
                    #     dl_var,
                    #     ivr_var,
                    #     sl_var,
                    #     wait_var,
                    #     conv_var,
                    #     wrap_var,
                        
                    # )
                    # compute_graph_data(diff_date, distrib, flow.hour.hour_value)
                    if diff_date.days == 0 and distrib == 60:
                        ic_bar.append(ic_var)
                        dl_bar.append(dl_var)
                        ivr_bar.append(ivr_var)
                        sl_line.append(sl_var)
                        if (dl_var != 0):
                            dma_bar.append(round(wait_var/dl_var))
                            dmc_bar.append(round(conv_var/dl_var))
                            dpt_bar.append(round(wrap_var/dl_var))
                        else:
                            dma_bar.append(0)
                            dmc_bar.append(0)
                            dpt_bar.append(0)
                    else:
                        if distrib == 60:
                            ic_dict[flow.hour.hour_value] += ic_var
                            dl_dict[flow.hour.hour_value] += dl_var
                            ivr_dict[flow.hour.hour_value] += ivr_var
                            sl_dict[flow.hour.hour_value] += sl_var
                            
                            dma_dict[flow.hour.hour_value]["waitDuration"]+=wait_var
                            dmc_dict[flow.hour.hour_value]["convDuration"]+=conv_var
                            dpt_dict[flow.hour.hour_value]["wrapUpDuration"]+=wrap_var
                            
                            dma_dict[flow.hour.hour_value]["dealed"] += dl_var
                        else:
                            day_str = flow.process_date.strftime("%A")
                            day_bar[day_str]["incoming"] += ic_var
                            day_bar[day_str]["dealed"] += dl_var
                            day_bar[day_str]["ivr"] += ivr_var
                            day_bar[day_str]["sl_dealed_calls"] += sl_var

                            day_bar[day_str]["waitDuration"] += wait_var
                            day_bar[day_str]["convDuration"] += conv_var
                            day_bar[day_str]["wrapUpDuration"] += wrap_var

                            # print()
                    ic_var = 0
                    dl_var = 0
                    ivr_var = 0
                    sl_var = 0
                    wait_var = 0
                    conv_var = 0
                    wrap_var = 0
                # if day_bar[day_str]["dealed"] != 0:
                #     categories_day.append(day_str)
                #     print(categories_day)
                
                ignored += flow.ignored
                waitDuration += flow.wait_duration
                convDuration += flow.conv_duration
                wrapUpDuration += flow.wrapup_duration
            if diff_date.days > 0:
                if distrib == 60:
                    ic_bar = list(ic_dict.values())
                    dl_bar = list(dl_dict.values())
                    ivr_bar = list(ivr_dict.values())
                    sl_line = list(sl_dict.values())
                    for hr in range(7, 21):
                        wait_stat = dma_dict[hr]
                        conv_stat = dmc_dict[hr]
                        wrap_stat = dpt_dict[hr]
                        if wait_stat["dealed"] != 0:
                            dma_bar.append(round(wait_stat["waitDuration"]/wait_stat["dealed"]))
                            dmc_bar.append(round(conv_stat["convDuration"]/wait_stat["dealed"]))
                            dpt_bar.append(round(wrap_stat["wrapUpDuration"]/wait_stat["dealed"]))
                        else:
                            dma_bar.append(0)
                            dmc_bar.append(0)
                            dpt_bar.append(0)
                elif distrib == 1:
                    ic_bar = [dict_val["incoming"] for dict_val in list(day_bar.values())]
                    dl_bar = [dict_val["dealed"] for dict_val in list(day_bar.values())]
                    ivr_bar = [dict_val["ivr"] for dict_val in list(day_bar.values())]
                    sl_line = [dict_val["sl_dealed_calls"] for dict_val in list(day_bar.values())]

                    for day in day_bar.keys():
                        if day_bar[day]["dealed"] != 0:
                            dayWaitDuration = day_bar[day]["waitDuration"]
                            dayConvDuration = day_bar[day]["convDuration"]
                            dayWrapUpDuration = day_bar[day]["wrapUpDuration"]
                            dayDealed = day_bar[day]["dealed"]
                            dma_bar.append(round(dayWaitDuration/dayDealed))
                            dmc_bar.append(round(dayConvDuration/dayDealed))
                            dpt_bar.append(round(dayWrapUpDuration/dayDealed))
                        else:
                            dma_bar.append(0)
                            dmc_bar.append(0)
                            dpt_bar.append(0)
            
            print(day_bar)

            graph_json = graph(check_flow, ic_bar, dl_bar, ivr_bar, sl_line, distrib)
            # dm_graph_json = dm_graph(check_flow, dma_bar, dmc_bar, dpt_bar)
            # period_flow["offered_calls"] = offered
            period_flow["incoming_calls"] = incoming
            period_flow["dealed_calls"] = dealed
            period_flow["ivr"] = ivr
            period_flow["ignored"] = ignored
            # period_flow["gived_up"] = gived_up
            if period_flow["dealed_calls"] != 0:
                period_flow['qs'] = ((period_flow["dealed_calls"]/(period_flow["incoming_calls"] - period_flow['ignored'] - period_flow['ivr']))*100, 1)
                period_flow['sl'] = round(((sl_dealed_calls/dealed) * 100), 1)
                period_flow['dma'] = round(waitDuration/dealed)
                period_flow['dmc'] = round(convDuration/dealed)
                period_flow['dpt'] = round(wrapUpDuration/dealed)
                period_flow['dmt'] = period_flow['dmc'] + period_flow['dpt']
            else:
                period_flow["qs"] = 0
                period_flow['sl'] = 0
                period_flow['dma'] = 0
                period_flow['dmc'] = 0
                period_flow['dpt'] = 0
                period_flow['dmt'] = 0
            # period_flow['sl'] = round()
                    

                # json_str = jsonpickle.encode(period_flow)
            #    json_strr = json.dumps(check_flow)
            """else:
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
                
                days_kpi_duration = DayKpiDuration.objects.filter(
                    process_date__range=(start_date, end_date),
                    activity__name=data.get("activity")
                    )
                
                waitDuration = 0
                convDuration = 0
                wrapUpDuration = 0

                for day_kpi in days_kpi_duration:
                    waitDuration+=day_kpi.waitDuration
                    convDuration+=day_kpi.convDuration
                    wrapUpDuration+=day_kpi.wrapUpDuration

                
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
                # period_flow['sl'] = round()"""
            activity = data.get("activity")
            # cf_dict = unique_flow.__dict__
            #print(period_flow)
            # cf_dict.pop('_state')
            cf_json = json.dumps(period_flow, default=str, indent=4)
            """print(type(period_flow))
            print(cf_json)
            print(type(cf_json))"""
            # print("Graph Json")
            # print(graph_json)
            # print("Dealed: {}".format(dealed))
            # print("Sl dealed: {}".format(sl_dealed_calls))
            return JsonResponse({
                "message":cf_json,
                "activity": activity,
                "graph_json": graph_json,
                # "dm_graph_json": dm_graph_json
                })
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
    # load_inbound_per_5_min("media/uploads/2024-01.csv")
    print("Data loaded")
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
        # waitDuration = 0
        # wrapUpDuration = 0
        # convDuration = 0
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
                    activity_waitDuration = activity_handled_rows['WaitDuration'].sum()
                    activity_convDuration = activity_handled_rows['ConvDuration'].sum()
                    activity_wrapUpDuration = activity_handled_rows['WrapupDuration'].sum()
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
                        sl_dealed_calls = activity_sl_dealed,
                        wait_duration = activity_waitDuration,
                        wrapup_duration = activity_wrapUpDuration,
                        conv_duration = activity_convDuration
                    ).save()

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


    all_occurence = 0
    for day in range(df['CallLocalTime'].min().day, df['CallLocalTime'].max().day + 1):
        # waitDuration = 0
        # wrapUpDuration = 0
        # convDuration = 0
    # day = 3
        day_occurence = 0
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
            activity_occurence = 0
            if activity.name == 'FRAN' and day_name == 'Sunday':
                continue
            else:
                activity_codes_file = list(activity.code_file.values_list('code', flat=True))
                activity_rows = day_frame[
                    day_frame['LastCampaign'].isin(activity_codes_file)
                ]
                for hour in range(7, 21):
                    for mn in range(0, 60, 5):
                        activity_hour_day_frame = activity_rows[
                            (activity_rows['CallLocalTime'].apply(lambda x: x.hour == hour))
                            & (activity_rows['CallLocalTime'].apply(lambda x: x.minute >= mn))
                            & (activity_rows['CallLocalTime'].apply(lambda x: x.minute < (mn + 5)))
                        ]
                        activity_incoming = activity_hour_day_frame['CallType'].sum()
                        activity_handled_rows = activity_hour_day_frame[activity_hour_day_frame['handled'] == 1]
                        activity_ignored = activity_hour_day_frame[activity_hour_day_frame['ignored'] == 1]['ignored'].sum()
                        activity_rerouted = activity_hour_day_frame[activity_hour_day_frame['rerouted'] == 1]['rerouted'].sum()
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
                            activity_wrapUpDuration = 0
                            activity_sl_dealed = 0
                            print('**************************************No working time for activity {} on {}h  {}-{}min range'.format(activity.name, hour, mn, mn + 5))
                            # Filling KPIs in DB
                            # sleep(5)
                        print('Before saving in DB')
                        activity_occurence+=1
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
                    print("Activity - {} - Day {} - Hour {} - Occurences {}".format(activity.name, day, hour, activity_occurence))

                #day_occurence += activity_occurence
        #all_occurence += day_occurence
        #print("Day occurences - {}".format(day_occurence))
    #print("All month ocurrences {}".format(all_occurence))

