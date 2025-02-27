"""
Django admin module for core app(Customization).
"""
from django.contrib import admin  # noqa # type: ignore
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin  # noqa # type: ignore
from django.utils.translation import gettext as _  # noqa # type: ignore

from core import models  # noqa # type: ignore


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for  users"""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    readonly_fields = [
        'last_login',  # 'is_active', 'is_staff', 'is_superuser'
     ]
    # add_fieldsets is used to add new fields to the user creation page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # adding style the add user page
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            ),
        }),
    )


admin.site.register(models.User, UserAdmin)
