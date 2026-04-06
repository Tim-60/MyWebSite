from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Blog

@admin.register(Blog)
class BlogAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)  
    list_display = ('title', 'posted', 'author')
    search_fields = ('title', 'description', 'content')
    list_filter = ('posted', 'author')
    date_hierarchy = 'posted'  # Добавляет удобную навигацию по годам/месяцам/дням