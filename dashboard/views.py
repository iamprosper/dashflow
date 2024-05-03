import csv
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    return HttpResponse("Dashboard view")

def process_csv(request):
    try:
        if request.method == 'POST' and request.FILES['csv_file']:
            csv_file = request.FILES['csv_file']
            csv_content = csv_file.read()
            # data_list = []

            # encodings = ['utf-8', 'utf-16', 'latin-1', 'ascii', 'utf-32']
            # decoded_content = None

            """for encoding in encodings:
                try:
                    deconded_content = csv_content.decode(encoding, errors='ignore')
                    break
                except UnicodeDecodeError as ue:
                    print("UnicodeDecodeError found {}".format(ue))
                    continue"""
            for name, uploaded_file in request.FILES.items():
                decoded_content = uploaded_file.read().decode('utf-8', errors='ignore').splitlines()
                reader = csv.reader(decoded_content)
                data = list(reader)
                # data_list.append({'file_name': name, 'data': data})
                return render(request, 'results.html', {'data': data})

            """if decoded_content is not None:
                reader = csv.reader(decoded_content.splitlines(), delimiter=',')
                data = list(reader)


            decoded_file = csv_file.read().decode('utf-32').splitlines()
            reader = csv.reader(decoded_file)

            data = []
            for row in reader:
                data.append(row)"""
            
        return render(request, 'upload_form.html')
    except Exception as e:
        print("An error occured : {}".format(e))