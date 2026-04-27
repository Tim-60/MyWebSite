from django.contrib import admin
from django.utils.html import format_html
from django_summernote.admin import SummernoteModelAdmin
from .models import Blog, Category, EducationalMaterial

@admin.register(Blog)
class BlogAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)  
    list_display = ('title', 'posted', 'author')
    search_fields = ('title', 'description', 'content')
    list_filter = ('posted', 'author')
    date_hierarchy = 'posted'  

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'materials_count', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    def materials_count(self, obj):
        return obj.get_materials_count()
    materials_count.short_description = 'Материалов'


@admin.register(EducationalMaterial)
class EducationalMaterialAdmin(SummernoteModelAdmin):
    summernote_fields = ('full_description',) 
    list_display = ('title', 'category', 'material_type', 'price_display')
    list_filter = ('category', 'material_type', 'is_free')
    search_fields = ('title', 'short_description', 'author')
    readonly_fields = ('posted_at',)
    
    def price_display(self, obj):
        if obj.is_free:
            return format_html('<span style="color:green">Бесплатно</span>')
        return f'{obj.price} ₽'
    price_display.short_description = 'Цена'