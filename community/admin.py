from django.contrib import admin
from .models import Column

@admin.register(Column)
class ColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date')
    list_filter = ('published_date', 'categories')
    search_fields = ('title', 'content')
    date_hierarchy = 'published_date'