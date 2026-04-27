"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpRequest
from .forms import MainForm, CommentForm, BlogForm, CategoryForm, EducationalMaterialForm
from django.contrib.auth.forms import UserCreationForm
from django.db import models
from .models import Blog, Comment, Category, EducationalMaterial
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count


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
    comments = Comment.objects.filter(post=parametr)
    form = CommentForm(request.POST)
    
    if request.method == 'POST':
        if form.is_valid():
            comment_f = form.save(commit=False)
            comment_f.author = request.user
            comment_f.date = datetime.now()
            comment_f.post = Blog.objects.get(id=parametr)
            comment_f.save()

            return redirect('blogpost', parametr=post_1.id)
        
        else:
            form = CommentForm()

    return render(
        request,
        'app/blogpost.html',
        {
            'post_1': post_1,
            'comments': comments,
            'form': form,
            'year': datetime.now().year,
        }
    )

def newpost(request):
    assert isinstance(request, HttpRequest)

    if request.method == "POST":
        blogform = BlogForm(request.POST, request.FILES)
        if blogform.is_valid():
            blog_f = blogform.save(commit=False)
            blog_f.posted = datetime.now()
            blog_f.author = request.user
            blog_f.save()

            return redirect('blog')
    else:
        blogform = BlogForm()

    return render(
        request,
        'app/newpost.html',
        {
            'blogform': blogform,
            'title': 'Добавить материал',
            'year': datetime.now().year,
        }
    )

def video(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/video.html',
        {
            'title':'Видеоматериалы',
            'message':'Сведения о нас',
            'year':datetime.now().year,
        }
    )

def catalog_view(request):
    
    categories = Category.objects.annotate(
        materials_count=Count('materials')).filter(materials_count__gt=0)
    
    return render(
        request, 
        'app/catalog.html',
        {
            'categories': categories
        }
        
    )

def category_detail(request, slug):
    
    category = get_object_or_404(Category, slug=slug)
    materials = EducationalMaterial.objects.filter(category=category)
    if request.GET.get('type'):
        materials = materials.filter(material_type=request.GET['type'])

    is_free_filter = request.GET.get('is_free') == 'true'
    if is_free_filter:
        materials = materials.filter(is_free=True)

    return render(
        request, 
        'app/category_detail.html', 
        {
            'category': category,
            'materials': materials
        }
    )

def material_detail(request, pk):
    
    material = get_object_or_404(EducationalMaterial, pk=pk)

    return render(
        request, 
        'app/material_detail.html', 
        {
            'material': material
        }
    )


def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def admin_catalog_dashboard(request):
   
    categories = Category.objects.annotate(materials_count=Count('materials'))
    materials = EducationalMaterial.objects.select_related('category').all()

    return render(
        request, 
        'app/admin/catalog_dashboard.html', 
        {
            'categories': categories,
            'materials': materials
        }
    )

@login_required
@user_passes_test(is_staff)
def admin_add_category(request):
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория создана!')
            return redirect('admin_catalog_dashboard')
    else:
        form = CategoryForm()
    return render(
        request, 
        'app/admin/form.html', 
        {
            'form': form, 
            'title': 'Добавить категорию'
        }
    )

@login_required
@user_passes_test(is_staff)
def admin_add_material(request):
    
    if request.method == 'POST':
        form = EducationalMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Материал создан!')
            return redirect('admin_catalog_dashboard')
    else:
        form = EducationalMaterialForm()
    return render(
        request, 
        'app/admin/form.html', 
        {
            'form': form, 
            'title': 'Добавить материал'
        }
    )