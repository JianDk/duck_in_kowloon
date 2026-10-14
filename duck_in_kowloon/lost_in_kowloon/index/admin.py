from django.contrib import admin
from .models import Dish


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
	list_display = ("display_order", "name", "price", "is_active", "updated_at")
	list_display_links = ("name",)
	list_editable = ("display_order", "price", "is_active")
	list_filter = ("is_active",)
	search_fields = ("name", "short_description")
	ordering = ("display_order", "name")

	fieldsets = (
		("Dish Content", {"fields": ("name", "short_description", "price", "image")}),
		("Display", {"fields": ("display_order", "is_active")}),
		("Timestamps", {"fields": ("created_at", "updated_at")}),
	)
	readonly_fields = ("created_at", "updated_at")
