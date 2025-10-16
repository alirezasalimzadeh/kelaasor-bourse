from django.contrib import admin
from .models import Company, InstrumentStats, Holding, Order


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "symbol", "name", "total_shares")
    search_fields = ("symbol", "name")


@admin.register(InstrumentStats)
class InstrumentStatsAdmin(admin.ModelAdmin):
    list_display = ("company", "ref_price", "band_low", "band_high", "last_price")
    list_filter = ("company",)


@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "quantity")
    list_filter = ("company", "user")
    search_fields = ("user__username", "company__symbol")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "company",
        "type",
        "quantity",
        "quantity_filled",
        "price",
        "status",
        "created_at",
    )
    list_filter = ("company", "type", "status")
    search_fields = ("user__username", "company__symbol")
    ordering = ("-created_at",)
