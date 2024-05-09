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

def myapp(request):
    if os.path.exists('myapp/gazet/gazet.csv')==False:
        gazet_processing()
    else:
        pass
    return render(request, 'myapp/myapp.html')

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        handle_uploaded_file(uploaded_file)
    return render(request, 'myapp/myapp.html')

def handle_uploaded_file(uploaded_file):
    with open('myapp/degrees/' + uploaded_file.name, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
            
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

def verify(request):
    upload_file(request)
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
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
    print(name)
    print(roll)
    print(result)
    data = name + '\n' + roll + '\n' + result
    return HttpResponse(data, content_type='text/plain')
    
# def handle_click(request):
#     if request.method == 'POST':
#         varify()
#     else:
#         print('Method not allowed.')