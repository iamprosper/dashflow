import csv
import chardet
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.templatetags import static
import pandas

from .models import UploadedFile

from .forms import FileUploadForm

# Create your views here.
def index(request):
    return HttpResponse("Dashboard view")


def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('process')
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})

def upload_success(request):
    return render(request, 'success.html')

def lazy_display(request):
    return render(request, 'lazy_display.html')

def stream_csv_data(file_path):
    with open(file_path, 'rb') as f:
        encoding = chardet.detect(f.read())['encoding']
    
    df = pandas.read_csv(file_path, encoding=encoding)
    handled_values =  df["ConvDuration"].apply(lambda x: 1 if x >=10 else 0)
    lost_ivr_values = df.apply(lambda row: 1 if row['ConvDuration'] == 0
                              and row["WaitDuration"] == 0
                              and row["OverflowDuration"] == 0 else 0, axis=1)
    dates_values = df["CallLocalTime"].apply(lambda x: x.split(' ')[0])
    hours_values = df["CallLocalTime"].apply(lambda x: x.split(' ')[1].split('.')[0])
    df.insert(5, 'handled', handled_values)
    df.insert(6, 'lost_ivr', lost_ivr_values)
    df.insert(9, 'dates', dates_values)
    df.insert(10, 'hours', hours_values)
    df['hour'] = pandas.to_datetime(df['hours'], format='%H:%M:%S').dt.hour
    filtered_rows = df[(df['hour'] >=7 ) &(df['hour'] <= 21)
                       & (df['handled'] == 1)
                       & (df['LastAgent'] > 0)
                       & (df['LastCampaign'] >= 1845)
                       & (df['LastCampaign'] <= 1847)
                       ]

    dmc = filtered_rows['ConvDuration'].mean()
    dma = filtered_rows['WaitDuration'].mean()
    dpt = filtered_rows['WrapupDuration'].mean()
    dealed = filtered_rows['CallType'].sum()
    # filtered_rows.to_excel('data.xlsx',index=False)
    return ([dmc, dma, dpt, dealed])
    """with open(file_path, 'r', newline='', encoding=encoding) as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            yield ','.join(row) + '\n'"""

def process_file(request):
    uploaded_file = UploadedFile.objects.last()
    if uploaded_file:
        file_path = uploaded_file.file.path
        dmc, dma, dpt, dealed = stream_csv_data(file_path)
        """with open(file_path, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)
            # yield header
            data = [row for row in reader]"""
            # for row in reader:
            #     yield ','.join(row) + '\n'
        response = render(request, 'success.html', {'dmc': round(dmc), 'dma': round(dma), 'dpt': round(dpt), 'dealed': dealed})
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