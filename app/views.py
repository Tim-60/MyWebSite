"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import redirect, render
from django.http import HttpRequest
from .forms import MainForm 
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from .models import Blog

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Главная',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Контакты',
            'message':'Страница с нашими контактами',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'О нас',
            'message':'Сведения о нас',
            'year':datetime.now().year,
        }
    )
def links(request):
    return render(
        request, 'app/links.html', 
        {
            'title':'Полезные ссылки',
        }
    )

def pool(request):
    assert isinstance(request, HttpRequest)
    data = None
    internet = {'1': 'Один раз в день', '2': 'Несколько раз в день',
                '3': 'Один раз в неделю','4': 'Несколько раз в неделю',
                '5': 'Раз в месяц и реже'}
    education = {'1': 'Школа','2': 'Колледж (техникум)',
                    '3': 'Высшее учебное заведение',
                    '4': 'Занимаюсь саомобучением'}
    if request.method == 'POST':
        form = MainForm(request.POST)
        if form.is_valid():
            data = dict()
            data['name'] = form.cleaned_data['name']
            data['country'] = form.cleaned_data['country']
            data['internet'] = internet [ form.cleaned_data['internet']]
            if(form.cleaned_data['payment'] == True):
                data['payment'] = 'Да'
            else:
                data['payment'] = 'Нет'
            data['education'] =  education [form.cleaned_data ['education']]
            data['message'] = form.cleaned_data['message']
            form = None
    else:
        form = MainForm()
    return render(
        request, 'app/pool.html', 
        {
            'form': form,
            'data': data,
            'title':'Обратная связь',
        }
    )

def registration(request):

    if request.method == "POST":
        regform = UserCreationForm(request.POST)
        if regform.is_valid():
            reg_f = regform.save(commit=False)
            reg_f.is_staff = False
            reg_f.is_active = True
            reg_f.is_superuser = False
            reg_f.date_joined = datetime.now()
            reg_f.last_login = datetime.now()
            regform.save()
            return redirect('home')
    else:
        regform = UserCreationForm()
    assert isinstance(request, HttpRequest)
    return render(
        request, 
        'app/registration.html',
        {
            'regform': regform,
            'year': datetime.now().year,
        }
    )

def blog(request): 
    posts = Blog.objects.all()

    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/blog.html',
    {
        'title':'Материалы',
        'posts': posts,
        'year': datetime.now().year,
    }
    )

def blogpost (request, parametr):

    assert isinstance(request, HttpRequest)
    post_1 = Blog.objects.get(id=parametr)
    return render(
        request,
        'app/blogpost.html',
        {
            'post_1': post_1,
            'year': datetime.now().year,
        }
    )