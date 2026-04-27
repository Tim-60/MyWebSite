"""
Definition of models.
"""

from django.db import models
from django.contrib import admin
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Blog(models.Model):
    title = models.CharField(max_length = 100, unique_for_date = "posted", verbose_name = "Заголовок")
    description = models.TextField(verbose_name= "Краткое содержание" )
    content = models.TextField(verbose_name= "Полное содержание")
    posted = models.DateTimeField(default=datetime.now(), db_index= True, verbose_name = "Опубликована")
    author = models.ForeignKey(User, null=True, blank=True, on_delete = models.SET_NULL, verbose_name = "Автор")
    image = models.FileField(default='temp.jpg', verbose_name= "Путь к картинке")
    
    def get_absolute_url(self):
        return reverse('blogpost', args=[str(self.id)])
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = "Posts"
        ordering = ["-posted"]
        verbose_name = "статья блога"
        verbose_name_plural = "статьи блога"

class Comment(models.Model):
    text = models.TextField(verbose_name="Текст комментария")
    date = models.DateTimeField(default=datetime.now(), db_index= True, verbose_name = "Дата комментария")
    author = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name= "Автор комментария")
    post = models.ForeignKey(Blog, on_delete = models.CASCADE, verbose_name = "Статья комментария")

    def __str__(self):
        return 'Комментарий %d %s к %s' % (self.id, self.author, self.post)

class Meta:
    db_table = "Comment"
    ordering = ["-date"]
    verbose_name = "Комментарии к статье блога"
    verbose_name_plural = "Комментарии к статьям блога"


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Название категории")
    description = models.TextField(verbose_name="Описание", blank=True)
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL-метка")
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='materials/%Y/%m/%d/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})
    
    def get_materials_count(self):
        return self.materials.count()


class EducationalMaterial(models.Model):
    
    MATERIAL_TYPES = [
        ('video', 'Видеолекция'),
        ('book', 'Учебник/Книга'),
        ('article', 'Статья'),
        ('presentation', 'Презентация'),
        ('test', 'Тест'),
        ('other', 'Другое'),
    ]
    
    
    title = models.CharField(max_length=100, verbose_name="Название")
    short_description = models.CharField(max_length=200, verbose_name="Краткое описание")
    full_description = models.TextField(verbose_name="Полное описание")
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, default='other', verbose_name="Тип")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)], verbose_name="Цена")
    is_free = models.BooleanField(default=False, verbose_name="Бесплатный")
    image = models.ImageField(upload_to='materials/%Y/%m/%d/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='materials', verbose_name="Категория")

    author = models.CharField(max_length=200, blank=True, verbose_name="Автор")
    duration = models.CharField(max_length=50, blank=True, verbose_name="Продолжительность")


    posted_at = models.DateTimeField(default=datetime.now(), verbose_name="Опубликовано")
    
    class Meta:
        verbose_name = "Образовательный материал"
        verbose_name_plural = "Образовательные материалы"
        ordering = ['-posted_at', 'title']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('material_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        if self.price == 0:
            self.is_free = True
        super().save(*args, **kwargs)


admin.site.register(Comment)