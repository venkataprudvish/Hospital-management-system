from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from authentication.models import Profile
from core.utils import has_role
from records.models import Patient
from .forms import BillForm
from .models import Bill


STAFF = (
    Profile.ROLE_OWNER,
    Profile.ROLE_ADMIN,
    Profile.ROLE_RECEPTIONIST,
    Profile.ROLE_ACCOUNTANT,
    Profile.ROLE_NURSE,
)


@login_required
def billing_list(request):
    queryset = Bill.objects.select_related(
        "patient",
        "appointment",
        "created_by",
    )

    if request.user.is_superuser or has_role(
        request.user,
        *STAFF,
    ):
        bills = queryset.all()

    elif hasattr(request.user, "patient_record"):
        bills = queryset.filter(
            patient=request.user.patient_record,
        )

    else:
        bills = queryset.none()

    return render(
        request,
        "billing/list.html",
        {
            "bills": bills,
        },
    )


@login_required
def create_bill(request):
    if not (
        request.user.is_superuser
        or has_role(request.user, *STAFF)
    ):
        raise PermissionDenied

    form = BillForm(
        request.POST or None,
        patient_queryset=Patient.objects.all(),
    )

    if request.method == "POST" and form.is_valid():
        bill = form.save(
            commit=False
        )

        bill.created_by = request.user

        bill.save()

        messages.success(
            request,
            "Invoice created.",
        )

        return redirect(
            "billing-list"
        )

    return render(
        request,
        "billing/form.html",
        {
            "form": form,
        },
    )


@login_required
def pay_bill(request, pk):
    if request.method != "POST":
        raise PermissionDenied

    if not (
        request.user.is_superuser
        or has_role(request.user, *STAFF)
    ):
        raise PermissionDenied

    with transaction.atomic():

        bill = get_object_or_404(
            Bill.objects.select_for_update(),
            pk=pk,
        )

        if bill.status == Bill.STATUS_CANCELLED:
            messages.error(
                request,
                "A cancelled invoice cannot be paid.",
            )

            return redirect(
                "billing-list"
            )

        if bill.status != Bill.STATUS_PAID:
            bill.status = Bill.STATUS_PAID
            bill.paid_at = timezone.now()

            bill.save(
                update_fields=[
                    "status",
                    "paid_at",
                ]
            )

            messages.success(
                request,
                "Invoice marked as paid.",
            )

    return redirect(
        "billing-list"
    )