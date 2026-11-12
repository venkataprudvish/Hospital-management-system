from django.contrib import admin

from .models import Bill


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "appointment",
        "amount",
        "status",
        "created_by",
        "created_at",
        "paid_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "patient__first_name",
        "patient__last_name",
        "patient__user__username",
        "patient__user__email",
        "description",
    )

    readonly_fields = (
        "patient",
        "appointment",
        "amount",
        "created_by",
        "created_at",
        "paid_at",
    )

    ordering = (
        "-created_at",
    )

    list_select_related = (
        "patient",
        "appointment",
        "created_by",
    )