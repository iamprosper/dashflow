import csv
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.templatetags import static

from .forms import FileUploadform

# Create your views here.
def index(request):
    return HttpResponse("Dashboard view")


def upload_file(request):
    if request.method == 'POST':
        form = FileUploadform(request.POST, request.FILES)
        if form.is_valid():
            upload_file = request.FILES['file']
            print(upload_file)
            return redirect('success')
    else:
        form = FileUploadform()
    return render(request, 'upload.html', {'form': form})

def upload_success(request):
    return render(request, 'success.html')

def process_csv(request):
    try:
        if request.method == 'POST' and request.FILES['csv_file']:
            csv_file = request.FILES['csv_file']
            csv_content = csv_file.read()
            # static_url = static('csv_file.csv')
            
            return render(request, 'results.html')
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
            """for name, uploaded_file in request.FILES.items():
                decoded_content = uploaded_file.read().decode('utf-8', errors='ignore').splitlines()
                reader = csv.reader(uploaded_file)
                data = list(reader)
                print("Name: {}".format(name))
                print(" {}".format(data))
                for row in data:
                    for cell in row:
                        print("{}".format(cell))
                # data_list.append({'file_name': name, 'data': data})
                return render(request, 'results.html', {'data': data, 'name': name})"""

            """if decoded_content is not None:
                reader = csv.reader(decoded_content.splitlines(), delimiter=',')
                data = list(reader)


            decoded_file = csv_file.read().decode('utf-32').splitlines()
            reader = csv.reader(decoded_file)

            data = []
            for row in reader:
                data.append(row)"""
        with open("csv_file.csv", 'r', newline='') as file:
            reader = csv.reader(file)
        for row in reader:
            print(row)
        return render(request, 'upload_form.html')
            
    except Exception as e:
        print("An error occured : {}".format(e))
        return render(request, 'upload_form.html')