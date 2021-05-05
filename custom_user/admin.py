from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe

from .models import CustomUser

class MyUserAdmin(UserAdmin):
    list_display = ('email', 'profile_photo_img', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', )
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('password', )}),
        (_('Personal info'), {'fields': ('email', 'profile_photo')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    @admin.display(description=_('Фото профиля'))
    def profile_photo_img(self, obj):
        if obj.profile_photo:
            return mark_safe(f"<img src='{obj.profile_photo.url}' style='height: 80px;'>")

admin.site.register(CustomUser, MyUserAdmin)
