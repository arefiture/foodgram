from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from api.models import (
    Ingredient,
    Recipe,
    RecipeFavorite,
    RecipeIngredients,
    RecipeTags,
    Tag
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    ordering = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredients
    autocomplete_fields = ['ingredient']
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = RecipeTags
    autocomplete_fields = ['tag']
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_author_recipe', 'get_favorite_count')
    search_fields = (
        'name', 'author__username', 'author__first_name', 'author__last_name'
    )
    list_filter = ('tags',)
    inlines = [RecipeIngredientInline, RecipeTagInline]
    autocomplete_fields = ('author', )
    readonly_fields = ('short_link', )
    ordering = ('id',)

    def get_author_recipe(self, obj: Recipe):
        # Создаем ссылку на редактирование автора рецепта
        url = reverse('admin:users_user_change', args=[obj.author.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.author.__str__()
        )

    def get_favorite_count(self, obj):
        return RecipeFavorite.objects.filter(recipe=obj).count()

    get_author_recipe.short_description = 'Автор рецепта'
    get_favorite_count.short_description = 'В избранном у ...'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    ordering = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
