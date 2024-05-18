from django.shortcuts import render
import tabula
import re
import pandas as pd
import numpy as np
import math
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from PyPDF2 import PdfFileReader
from django.http import HttpResponse
import os
import pymongo

def myapp(request):
    if os.path.exists('myapp/gazet/gazet.csv')==False:
        gazet_processing()
    else:
        pass
    return render(request, 'myapp/comp/home.html')

def home(request):
    return render(request, 'myapp/comp/home.html')

def about(request):
    return render(request, 'myapp/comp/about.html')

def login(request):
    return render(request, 'myapp/comp/admin_login.html')

def dashboard(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        password = request.POST.get('password')
        if name=='123' and password=='123':
            return render(request, 'myapp/comp/dashboard.html')
        else:
            return render(request, 'myapp/comp/admin_login.html')
    else:
        pass
    return HttpResponse('Passed')

def admin_dashboard(request):
    return render(request, 'myapp/comp/dashboard.html')

def saved_template(request):
    return render(request, 'myapp/comp/saved_templates.html')

def report(request):
    return render(request, 'myapp/comp/reports.html')



# a = 0

# def upload_file(request):
#     # a+=1
#     print('Ali')
#     uploaded_file = None
#     if request.method == 'POST' and request.FILES['file']:
#         uploaded_file = request.FILES['file']
#     if uploaded_file is not None:
#             # my_file = uploaded_file.name
#             # print(my_file)
#             with open('myapp/degrees/' + uploaded_file.name, 'wb+') as destination:
#                 for chunk in uploaded_file.chunks():
#                     destination.write(chunk)
#             # global uploaded_file
#     else:
#         pass
#     return uploaded_file
            
def gazet_processing():
    pdf_path = 'myapp/gazet/Gz_Ia1p21.pdf'
    tables = tabula.read_pdf(pdf_path, pages='103-1218', multiple_tables=True)
    var = {}
    tbl = 0
    for t in tables:
        c = 3
        s = 0
        for i in range(3):
            var_df = f"t{tbl}"
            var[var_df] = t[t.columns[s:c]]
            c+=3
            s+=3
            tbl+=1
    for name in list(var.keys()):
        try:
            col = [i for i in var[name].columns if i.startswith('Unnamed')]
            var[name].drop(col, axis=1, inplace=True)
            var[name].columns=['Roll-No Name', 'Result']
        except:
            print(name)
    con_df = pd.DataFrame()
    for con in list(var.keys()):
        con_df = pd.concat([con_df, var[con]], ignore_index=True)
    df = con_df.dropna(subset='Roll-No Name')
    df = df.drop('Result.2', axis= 1)
    df['Roll'] = df['Roll-No Name'].str.split(expand=True)[0]
    df['Name'] = df['Roll-No Name'].str[7:]
    df.drop('Roll-No Name', axis=1, inplace=True)
    df = df[['Roll', 'Name', 'Result']]
    df = df.dropna(subset='Result')
    df.to_csv('myapp/gazet/gazet.csv', index=False)
    pass

# def get_request(request):
#     return render(request, 'myapp/dashboard.html')

def varified_db(name, roll, result):
    client = pymongo.MongoClient()
    db = client.get_database('validate')
    collection = db.get_collection('validation_data')
    data = {'name': name, 'roll': roll, 'result': result}
    collection.insert_one(data)
    
def unvarified_db(name, roll, result):
    client = pymongo.MongoClient()
    db = client.get_database('validate')
    collection = db.get_collection('unvalidated_data')
    unver_data = {'name': name, 'roll': roll, 'result': result}
    collection.insert_one(unver_data)

def verify(request):
    # if request.method == 'POST' and request.FILES['file']:
    #     uploaded_file = request.FILES['file']
    # logger.info("Verify function called")
    global uploaded_file
    uploaded_file = None
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        if uploaded_file is not None:
            # my_file = uploaded_file.name
            # print(my_file)
            with open('myapp/degrees/' + uploaded_file.name, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            # global uploaded_file
        # else:
        #     pass
        # uploaded_file = None
        # uploaded_file = upload_file(request)
        # if uploaded_file is not None:
            # uploaded_file = upload_file(request)
            print(uploaded_file)
            # get_request(request)
            pdf_file = 'myapp/degrees/' + uploaded_file.name
            file_name = uploaded_file.name
            images = convert_from_path(pdf_file, dpi=300)
            for i, image in enumerate(images):
                image.save('myapp/image/' + file_name + '.jpg', 'JPEG')
            image_file = 'myapp/image/' + file_name + '.jpg'
            image = Image.open(image_file)
            extracted_text = pytesseract.image_to_string(image)
            name = re.search('Name: (.*?) F', extracted_text).group(1)
            roll = re.search('Roll No.: (.*?) ', extracted_text).group(1)
            result = re.search('Notification: (.*?)\n', extracted_text).group(1)
            df = pd.read_csv('myapp/gazet/gazet.csv')
            if any(df['Roll']==roll)==True:
                comp = df[df['Roll']==roll]
                ver = (comp['Result']==result).iloc[0]
                if ver==True:
                    with open('myapp/verified/' + uploaded_file.name, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)
                    varified_db(name, roll, result)
                else:
                    with open('myapp/unverified/' + uploaded_file.name, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)
                    unvarified_db(name, roll, result)
                # return HttpResponse('Data Uploaded')
                # return render(request, 'myapp/dashboard.html')
            else:
                return render(request, 'myapp/comp/home.html',{'text' : 'Roll no not found'})
            # return render(request, 'myapp/dashboard.html')
    else:
        return HttpResponse('File not found')
    
def your_view_name(request):
    if request.method == 'POST':
        checkbox_value = request.POST.get('my_checkbox')
        if checkbox_value == '1':
            print('Checked')
        else:
            print('Unchecked')

    # return render(request, 'myapp/dashboard.html')