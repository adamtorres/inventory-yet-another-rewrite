from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.db.models import functions, expressions
from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

from ... import models as u_models


class Command(BaseCommand):
    def handle(self, *args, **options):
        #     def avg_report(self):
        #         qs = self.annotate(item_name=functions.Lower(models.Case(
        #             models.When(~models.Q(common_name=''), models.F('common_name')),
        #             models.When(~models.Q(verbose_name=''), models.F('verbose_name')),
        #             default=models.F('cryptic_name')
        #         ))).values('item_name', 'measuring_unit', 'converted_unit').annotate(
        #             min=models.Min('avg_converted_per_measuring'),
        #             max=models.Max('avg_converted_per_measuring'),
        #             avg=models.Avg('avg_converted_per_measuring'),
        #             count=models.Count('id'),
        #             first_date=models.Min('measure_date'),
        #             last_date=models.Max('measure_date'),
        #         )
        #         qs = qs.order_by('item_name', 'measuring_unit', 'converted_unit')
        with monkey_patch_cursordebugwrapper(print_sql=False, confprefix="SHELL_PLUS", print_sql_location=False):
            self.do_thing()

    def do_thing(self):
        qs = u_models.UsageGroup.objects.all().annotate(
            name_order=models.Case(
                models.When(models.Q(name_on_form__iexact='nona'), models.Value(1)),
                models.When(models.Q(name_on_form__iexact='steven'), models.Value(2)),
                models.When(models.Q(name_on_form__iexact='marianna'), models.Value(3)),
                models.When(models.Q(name_on_form__iexact='bakery-congregate'), models.Value(4)),
                models.When(models.Q(name_on_form__iexact='bakery'), models.Value(5)),
                default=models.Value(20)
            )
        ).order_by("-start_date", "name_order")

        batch_to_update = []
        update_count = 50
        updated_count = 0
        for i, ug in enumerate(qs):
            ug.form_order = i
            batch_to_update.append(ug)
            if len(batch_to_update) >= update_count:
                self.stdout.write(f"Updating {len(batch_to_update)} UsageGroups...")
                updated_count += u_models.UsageGroup.objects.bulk_update(batch_to_update, ["form_order"])
                batch_to_update.clear()
        if batch_to_update:
            self.stdout.write(f"Updating {len(batch_to_update)} UsageGroups...")
            updated_count += u_models.UsageGroup.objects.bulk_update(batch_to_update, ["form_order"])
            batch_to_update.clear()
        self.stdout.write(f"Done.  Updated {updated_count}")

        # start_date
        # name_on_form
        # CASE
        #   WHEN LOWER(name_on_form) = 'nona' THEN 1
        #   WHEN LOWER(name_on_form) = 'steven' THEN 2
        #   WHEN LOWER(name_on_form) = 'marianna' THEN 3
        #   WHEN LOWER(name_on_form) = 'bakery-congregate' THEN 4
        #   WHEN LOWER(name_on_form) = 'bakery' THEN 5
        #   ELSE 6
        # END
        # CASE
        #   WHEN "usage_usagegroup"."name_on_form" LIKE 'nona' ESCAPE '\' THEN 1
        #   WHEN "usage_usagegroup"."name_on_form" LIKE 'steven' ESCAPE '\' THEN 1
        #   WHEN "usage_usagegroup"."name_on_form" LIKE 'marianna' ESCAPE '\' THEN 1
        #   WHEN "usage_usagegroup"."name_on_form" LIKE 'bakery-congregate' ESCAPE '\' THEN 1
        #   WHEN "usage_usagegroup"."name_on_form" LIKE 'bakery' ESCAPE '\' THEN 1
        #   ELSE 20
        # END AS "name_order"
# ug.form_order
