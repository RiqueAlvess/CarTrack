from django.contrib import admin
from .models import EmailRecipient

@admin.register(EmailRecipient)
class EmailRecipientAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'name', 
        'user',
        'is_active',
        'created_at'
    )
    
    list_filter = (
        'is_active',
        'created_at',
        'user'
    )
    
    search_fields = (
        'email',
        'name',
        'user__username',
        'user__email'
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações do Destinatário', {
            'fields': ('user', 'email', 'name', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    ordering = ['user', 'email']