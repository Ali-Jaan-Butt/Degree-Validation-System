from django.shortcuts import render
from django.contrib import messages
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
import pandas as pd

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
    obj = None
    client = pymongo.MongoClient()
    db = client.get_database('validate')
    collection = db.get_collection('admin_login')
    cursor = collection.find()
    for document in cursor:
        obj = document['_id']
    if obj==None:
        client = pymongo.MongoClient()
        db = client.get_database('validate')
        collection = db.get_collection('admin_login')
        info = {'user':'123', 'passw':'123'}
        collection.insert_one(info)
    else:
        pass
    return render(request, 'myapp/comp/admin_login.html')

def dashboard(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        password = request.POST.get('password')
        client = pymongo.MongoClient()
        db = client.get_database('validate')
        collection = db.get_collection('admin_login')
        cursor = collection.find()
        for document in cursor:
            obj = document
        db_name = obj['user']
        db_pass = obj['passw']
        if name==db_name and password==db_pass:
            messages.info(request, None)
            return render(request, 'myapp/comp/dashboard.html')
        else:
            messages.info(request, 'Invalid Login')
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

def settings(request):
    return render(request, 'myapp/comp/setting.html')

def update_username(request):
    if request.method == 'POST':
        ch_user = request.POST.get('newUsername')
        client = pymongo.MongoClient()
        db = client.get_database('validate')
        collection = db.get_collection('admin_login')
        cursor = collection.find()
        for document in cursor:
            obj = document
        ud_obj = { '$set': {'user':ch_user}}
        collection.update_one(obj, ud_obj)
    else:
        pass
    return render(request, 'myapp/comp/setting.html')

def change_password(request):
    if request.method == 'POST':
        c_pass = request.POST.get('currentPassword')
        client = pymongo.MongoClient()
        db = client.get_database('validate')
        collection = db.get_collection('admin_login')
        cursor = collection.find()
        for document in cursor:
            obj = document
        if obj['passw']==c_pass:
            c_pass = request.POST.get('newPassword')
            ver_c_pass = request.POST.get('confirmPassword')
            if c_pass==ver_c_pass:
                client = pymongo.MongoClient()
                db = client.get_database('validate')
                collection = db.get_collection('admin_login')
                cursor = collection.find()
                for document in cursor:
                    obj = document
                ud_obj = { '$set': {'passw':ver_c_pass}}
                collection.update_one(obj, ud_obj)
                messages.info(request, None)
            else:
                pass
        else:
            messages.info(request, 'Try again')
    else:
        pass
    return render(request, 'myapp/comp/setting.html')
            
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
    global uploaded_file
    uploaded_file = None
    condition = False
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        if uploaded_file is not None:
            with open('myapp/degrees/' + uploaded_file.name, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            print(uploaded_file)
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
                condition = True
                if condition==True:
                    messages.info(request, 'Verified Succesfully.')
            else:
                messages.info(request, 'Verified Succesfully.')
            return render(request, 'myapp/comp/home.html')
    else:
        messages.info(request, 'Upload PDF file to proceed.')
    return render(request, 'myapp/comp/home.html')
    
def checkbox_data(request):
    cb_1 = None
    cb_2 = None
    cb_3 = None
    col_data = []
    if request.method == 'POST':
        if request.POST.get('cb1'):
            cb_1 = request.POST.get('cb1')
            col_data.append('name')
        if request.POST.get('cb2'):
            cb_2 = request.POST.get('cb2')
            col_data.append('roll')
        if request.POST.get('cb3'):
            cb_3 = request.POST.get('cb3')
            col_data.append('result')
        client = pymongo.MongoClient()
        db = client.get_database('validate')
        collection = db.get_collection('validation_data')
        cursor = collection.find()
        final_data = {'_id':[], 'name':[], 'roll':[], 'result':[]}
        for data in cursor:
            final_data['_id'].append(data['_id'])
            final_data['name'].append(data['name'])
            final_data['roll'].append(data['roll'])
            final_data['result'].append(data['result'])
        df = pd.DataFrame(final_data, columns=col_data)
        df_html = df.to_html(classes='dataframe', border=0, index=False)
        print(final_data)
        print(cb_1)
        print(cb_2)
        print(cb_3)
    return render(request, 'myapp/comp/data.html', {'data':df_html})