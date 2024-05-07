from django.shortcuts import render

def myapp(request):

    # Pass variables to the HTML template
    return render(request, 'myapp/myapp.html')

def upload_file(request):
    if request.method == 'POST' or request.FILES['file']:
        uploaded_file = request.FILES['file']
        content = uploaded_file.read().decode('utf-8')
        # print('Hello World')
        handle_uploaded_file(uploaded_file)
        return HttpResponse(f'File uploaded successfully. Content: {content}')
    return render(request, 'myapp/myapp.html')

def handle_uploaded_file(file):
    with open('degrees/' + file.name, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)