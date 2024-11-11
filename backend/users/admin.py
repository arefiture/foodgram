from django.contrib import admin
from django.contrib.auth.models import Group
from django.forms import PasswordInput, ModelForm
from django.urls import reverse
from django.utils.html import format_html
from rest_framework.authtoken.models import TokenProxy

from users.models import (
    Subscription,
    User
)


class SubscriptionAdmin(admin.ModelAdmin):

    list_display = ('id', 'get_author_recipe', 'get_user', 'created_at')
    search_fields = ('author_recipe__username', 'user__username')
    ordering = ('id', )
    readonly_fields = ('created_at', )

    required_block = (
        'Обязательные данные', {
            'fields': ('author_recipe', 'user')
        }
    )

    def add_view(self, request, extra_content=None):
        self.fieldsets = [self.required_block]
        return super(SubscriptionAdmin, self).add_view(request)

    def change_view(self, request, object_id, extra_content=None):
        self.fieldsets = [
            self.required_block,
            (None, {'fields': ('created_at', )})
        ]
        return super(SubscriptionAdmin, self).change_view(request, object_id)

    def get_author_recipe(self, obj: Subscription):
        # Создаем ссылку на редактирование автора рецепта
        url = reverse('admin:users_user_change', args=[obj.author_recipe.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.author_recipe.username
        )

    def get_user(self, obj: Subscription):
        # Создаем ссылку на редактирование подписчика
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    get_author_recipe.short_description = 'Автор рецепта'
    get_user.short_description = 'Подписчик'


class UserAdminForm(ModelForm):
    class Meta:
        model = User
        fields = '__all__'

    # Переопределяем метод, чтобы скрыть пароль
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Только для создания
            self.fields['password'].widget = PasswordInput(
                attrs={'class': 'vTextField'}  # Длина поля для админки
            )


class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = (
        'username', 'email', 'get_full_name', 'last_login',
        'is_active', 'is_staff'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff')
    ordering = ('id', )

    readonly_fields = ('date_joined', 'last_login')
    exclude = ('groups', 'user_permissions')

    def set_fieldsets(
        self, enabled_password: bool = True, fields: list = []
    ) -> None:
        """
        Функция устанавливает форму в зависимости от переданных данных.

        Параметры:
        * enabled_password - Требуется ли в форме пароль. По умолчанию True
        * fields - Отображаемые необязательные поля. По умолчанию пустой
        список. В отображаемых полях всегда есть date_joined.
        """
        self.fieldsets = [
            (
                'Персональные данные', {
                    'fields': (
                        'username', 'email', 'first_name', 'last_name',
                        *(['password'] if enabled_password else [])
                    )
                }
            ),
            (
                'Признаки', {
                    'fields': ('is_active', 'is_staff', 'is_superuser')
                }
            ),
            (
                None, {
                    'fields': ('date_joined', *fields)
                }
            )
        ]

    def add_view(self, request, extra_content=None):
        self.set_fieldsets()
        return super(UserAdmin, self).add_view(request)

    def change_view(self, request, object_id, extra_content=None):
        self.set_fieldsets(enabled_password=False, fields=['last_login'])
        return super(UserAdmin, self).change_view(request, object_id)


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
