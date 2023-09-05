from django.contrib import admin

from .models import Fundacion


@admin.register(Fundacion)
class FundacionAdmin(admin.ModelAdmin):
    pass
