from django.shortcuts import render


def home(request):
    return render(request, 'catalog/home.html')


def contacts(request):
    if request.method == 'POST':
        # Обработка формы (для дополнительного задания)
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # Здесь можно добавить логику сохранения или отправки email
        return render(request, 'catalog/contacts.html', {'success': True})

    return render(request, 'catalog/contacts.html')