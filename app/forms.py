"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.db import models
from .models import Comment
from .models import Blog

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))
    
class MainForm(forms.Form):
    name = forms.CharField(label='Ваше имя:', min_length=2, max_length=30)
    country = forms.CharField(label='Ваша страна:', min_length=2, max_length=30)
    internet = forms.ChoiceField(label = 'Как часто вы открываете наш ресурс?', 
                               choices = (('1', 'Один раз в день'),
                                ('2', 'Несколько раз в день'),
                                ('3', 'Один раз в неделю'),
                                ('4', 'Несколько раз в неделю'),
                                ('5', 'Раз в месяц и реже')), initial=1) 
    payment = forms.BooleanField(label='Вы используете платный контент?', required=False)
    education = forms.ChoiceField(label = 'На каком этапе обучения вы находитесь?', 
                               choices = (('1', 'Школа'),
                                ('2', 'Колледж (техникум)'),
                                ('3', 'Высшее учебное заведение'),
                                ('4', 'Занимаюсь саомобучением')), widget=forms.RadioSelect, initial=1)
    message = forms.CharField(label= 'Пожелания нашей платформе:', required=False, widget=forms.Textarea(attrs={'rows':5,'cols':50}))

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text':"Комментарий"}

class BlogForm(forms.ModelForm):
    class Meta: 
        model = Blog 
        fields = ('title', 'description', 'content', 'image', )
        labels = {'title': "Заголовок", 'description': "Краткое содержание", 
                  'content': "Полное содержание", 'image': "Картинка"}