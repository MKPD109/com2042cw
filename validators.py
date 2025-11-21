from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_release_date_within_6_months(value: date):
    """
    unreleased albums may have a release date up to six months in the future, inclusive
    """
    if value is None:
        return
    six_months = timedelta(days=180)
    if value > (date.today() + six_months):
        raise ValidationError(_("Release date cannot be more than 6 months in the future."))

def validate_stars_half_step(value: Decimal):
    """
    have a 1 digit and 1 decimal-place value between 0 and 5, in increments of 0.5
    """
    if value < Decimal("0.0") or value > Decimal("5.0"):
        raise ValidationError(_("Stars must be between 0.0 and 5.0."))
    # check increments of 0.5
    doubled = value * 2
    if doubled != int(doubled):
        raise ValidationError(_("Stars must be in increments of 0.5 (e.g., 2.5, 3.0, 4.5)."))
