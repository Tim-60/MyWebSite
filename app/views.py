"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpRequest
from .forms import MainForm, CommentForm, BlogForm, CategoryForm, EducationalMaterialForm
from django.contrib.auth.forms import UserCreationForm
from django.db import models, transaction
from .models import Blog, Comment, Category, EducationalMaterial, Order, OrderItem
from django.contrib import messages
from django.db.models import Count, Sum
from django.views.decorators.http import require_POST
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import Group
from .roles import (CLIENT_GROUP, is_admin, is_manager, is_client, role_required)


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title': 'Главная',
            'latest_news': Blog.objects.all()[:3],
            'year': datetime.now().year,
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
            user = regform.save()
            client_group, _ = Group.objects.get_or_create(name=CLIENT_GROUP)
            user.groups.add(client_group)
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

def blogpost(request, parametr):
    assert isinstance(request, HttpRequest)
    post_1 = get_object_or_404(Blog, id=parametr)
    comments = Comment.objects.filter(post=post_1)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_f = form.save(commit=False)
            comment_f.author = request.user
            comment_f.post = post_1
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

@role_required(is_admin)  
def newpost(request):
    assert isinstance(request, HttpRequest)

    if request.method == "POST":
        blogform = BlogForm(request.POST, request.FILES)
        if blogform.is_valid():
            blog_f = blogform.save(commit=False)
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
            'title': 'Добавить новость',
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

    selected_type = request.GET.get('type', '')
    if selected_type in dict(EducationalMaterial.MATERIAL_TYPES):
        materials = materials.filter(material_type=selected_type)
    else:
        selected_type = ''

    is_free_filter = request.GET.get('is_free') == 'true'
    if is_free_filter:
        materials = materials.filter(is_free=True)

    return render(
        request,
        'app/category_detail.html',
        {
            'category': category,
            'materials': materials,
            'material_types': EducationalMaterial.MATERIAL_TYPES,
            'selected_type': selected_type,
            'is_free_filter': is_free_filter,
        }
    )

def material_detail(request, pk):

    material = get_object_or_404(EducationalMaterial, pk=pk)
    has_access, pending = material_access(request.user, material)
    in_cart = material.pk in request.session.get('cart', [])

    return render(
        request,
        'app/material_detail.html',
        {
            'material': material,
            'has_access': has_access,
            'pending': pending,
            'in_cart': in_cart,
        }
    )
    

@role_required(is_admin)  
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

@role_required(is_admin)  
def admin_add_category(request):
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
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

@role_required(is_admin)  
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

def material_access(user, material):
    if not material.is_paid:
        return True, False
    if not user.is_authenticated:
        return False, False
    if user.is_superuser or is_manager(user):
        return True, False
    statuses = set(
        OrderItem.objects
        .filter(order__customer=user, material=material)
        .values_list('order__status', flat=True)
    )
    return bool(statuses & set(Order.ACCESS_STATUSES)), 'processing' in statuses


@role_required(is_manager)
def manager_orders(request):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=request.POST.get('order_id'))
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save(update_fields=['status'])
            messages.success(request, 'Статус заказа №%d изменён.' % order.id)
        return redirect('manager_orders')

    orders = (Order.objects
              .select_related('customer')
              .prefetch_related('items')
              .annotate(total_price=Sum('items__price')))

    return render(
        request,
        'app/manager/orders.html',
        {
            'title': 'Заказы',
            'orders': orders,
            'statuses': Order.STATUS_CHOICES,
        }
    )


@role_required(is_client)
@require_POST
def add_to_cart(request, pk):
    material = get_object_or_404(EducationalMaterial, pk=pk)
    if not material.is_paid:
        messages.info(request, 'Этот материал бесплатный, покупка не нужна.')
        return redirect('cart')

    has_access, pending = material_access(request.user, material)
    if has_access or pending:
        messages.info(request, 'Вы уже приобрели этот материал, либо заказ ожидает подтверждения.')
        return redirect('cart')
    
    cart = request.session.get('cart', [])
    if material.pk in cart:
        messages.info(request, 'Этот материал уже в корзине.')
    else:
        cart.append(material.pk)
        request.session['cart'] = cart
        messages.success(request, 'Материал «%s» добавлен в корзину.' % material.title)
    return redirect('cart')


@role_required(is_client)
@require_POST
def remove_from_cart(request, pk):
    cart = request.session.get('cart', [])
    if pk in cart:
        cart.remove(pk)
        request.session['cart'] = cart
        messages.success(request, 'Материал удалён из корзины.')
    return redirect('cart')


@role_required(is_client)
def cart_view(request):
    ids = request.session.get('cart', [])
    materials = list(EducationalMaterial.objects.filter(pk__in=ids).select_related('category'))

    found = {m.pk for m in materials}
    clean = [i for i in ids if i in found]
    if clean != ids:
        request.session['cart'] = clean

    total = sum(m.price for m in materials)

    return render(
        request,
        'app/cart.html',
        {
            'title': 'Корзина',
            'materials': materials,
            'total': total,
        }
    )


@role_required(is_client)
@require_POST
def checkout(request):
    ids = request.session.get('cart', [])
    materials = list(EducationalMaterial.objects.filter(pk__in=ids))
    if not materials:
        messages.warning(request, 'Корзина пуста.')
        return redirect('cart')

    with transaction.atomic():
        order = Order.objects.create(customer=request.user)
        OrderItem.objects.bulk_create([
            OrderItem(order=order, material=m, title=m.title, price=m.price)
            for m in materials
        ])

    request.session['cart'] = []
    messages.success(request, 'Заказ №%d оформлен.' % order.id)
    return redirect('my_orders')


@role_required(is_client)
def my_orders(request):
    orders = (Order.objects
              .filter(customer=request.user)
              .prefetch_related('items')
              .annotate(total_price=Sum('items__price')))

    return render(
        request,
        'app/my_orders.html',
        {
            'title': 'Мои покупки',
            'orders': orders,
        }
    )