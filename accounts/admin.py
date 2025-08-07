from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = (
        'email', 
        'username', 
        'first_name', 
        'last_name', 
        'is_email_configured',
        'is_staff', 
        'is_active'
    )
    
    list_filter = (
        'is_staff', 
        'is_active', 
        'is_email_configured',
        'date_joined'
    )
    
    search_fields = ('email', 'username', 'first_name', 'last_name')
    
    ordering = ('email',)
    
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Informações Pessoais', {
            'fields': ('first_name', 'last_name')
        }),
        ('Configurações SMTP', {
            'fields': (
                'smtp_email',
                'smtp_password', 
                'smtp_host',
                'smtp_port',
                'smtp_use_tls',
                'is_email_configured'
            ),
            'classes': ('collapse',)
        }),
        ('Permissões', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username', 
                'first_name',
                'last_name',
                'password1',
                'password2',
                'is_staff',
                'is_active'
            ),
        }),
    )
    
    readonly_fields = ('is_email_configured', 'last_login', 'date_joined')