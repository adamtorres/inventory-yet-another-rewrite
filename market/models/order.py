import decimal
import logging

from django.db import models
from django.utils import timezone


logger = logging.getLogger(__name__)


def today():
    return timezone.localdate(timezone.now())


def now():
    return timezone.localtime(timezone.now())


class OrderManager(models.Manager):
    def incomplete(self):
        return self.exclude(pickup_date__isnull=False, date_paid__isnull=False)


class Order(models.Model):
    date_ordered = models.DateField(default=today)
    time_ordered = models.TimeField(default=now)
    date_made = models.DateField(null=True, blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    date_paid = models.DateField(null=True, blank=True)
    who = models.CharField(max_length=100, blank=True, default="")
    sale_price = models.DecimalField(
        max_digits=9, decimal_places=4, default=0, help_text="sale price for all items in the order",)
    material_cost = models.DecimalField(
        max_digits=9, decimal_places=4, default=0, help_text="cost of materials for all items in the order.",)
    expected_date = models.DateField(null=True, blank=True)
    expected_time = models.TimeField(null=True, blank=True)  # TODO: Or should this be 'morning', 'afternoon'?
    who_is_picking_up = models.CharField(max_length=100, blank=True, default="", help_text="If different than 'who'")
    reason_for_order = models.CharField(
        max_length=100, blank=True, default="", help_text="Because people keep asking me.",)
    how_paid = models.CharField(
        max_length=100, blank=True, default="", help_text="card/cash/gift certificate.  Is this even needed?",)
    contact_number = models.CharField(
        max_length=100, blank=True, default="", help_text="In case there is an issue and/or pickup is delayed",)
    discount = models.DecimalField(
        max_digits=9, decimal_places=4, default=0, help_text="discount applied to the order.",)
    discount_text = models.CharField(
        max_length=100, blank=True, default="", help_text="Brief explanation of the discount.",)
    discounted_price = models.DecimalField(
        max_digits=9, decimal_places=4, default=0, help_text="sale price minus discount.",)
    objects = OrderManager()

    class Meta:
        ordering = ['expected_date', 'who', 'id']

    def __str__(self):
        return f"{self.date_ordered} : {self.who} : {self.state()}"

    def calculate_totals(self):
        material_cost = 0
        sale_price = 0
        for line_item in self.line_items.all():
            line_item.calculate_totals()
            material_cost += decimal.Decimal(line_item.material_cost)
            sale_price += decimal.Decimal(line_item.sale_price)
        if ((self.material_cost != material_cost) or (self.sale_price != sale_price)
                or (self.discounted_price != (sale_price - self.discount))):
            self.material_cost = material_cost
            self.sale_price = sale_price
            self.discounted_price = self.sale_price - self.discount
            self.save()

    def can_be_made(self):
        return not self.date_made

    def can_be_picked_up(self):
        return self.date_made and not self.pickup_date

    def clear_order_made(self):
        if self.date_made:
            self.date_made = None
            self.save()

    def clear_order_paid(self):
        if self.date_paid:
            self.date_paid = None
            self.save()

    def clear_order_picked_up(self):
        if self.pickup_date:
            self.pickup_date = None
            self.save()

    def is_completed(self):
        return self.date_made and self.pickup_date and self.date_paid

    def is_paid(self):
        return bool(self.date_paid)

    def is_picked_up(self):
        return bool(self.pickup_date)

    def set_order_made(self):
        if not self.date_made:
            self.date_made = timezone.now()
            self.save()

    def set_order_paid(self):
        if not self.date_paid:
            self.date_paid = timezone.now()
            self.save()

    def set_order_picked_up(self):
        if not self.pickup_date:
            self.pickup_date = timezone.now()
            self.save()

    def state(self):
        _state = ""
        if not self.date_made:
            _state = "Ordered"
        if not _state and not self.pickup_date:
            _state = "Made"
        if self.pickup_date and not self.date_paid:
            _state = "Picked Up"
        if self.pickup_date and self.date_paid:
            _state = "Completed"
        return f"{_state}:{'' if self.date_paid else 'NOT'} Paid"
