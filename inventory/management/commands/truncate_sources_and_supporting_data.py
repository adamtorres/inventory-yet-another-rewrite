from django.core.management.base import BaseCommand

from ... import models as inv_models


class Command(BaseCommand):
    help = """
    The name of this command is intentionally long to give the user time to consider if this is actually what they want
    to do.  It goes step-by-step in deleting all inventory objects from the database.
    Django admin users are unaffected.
    """
    def handle(self, *args, **options):
        print("Deleting OrderLineItems...")
        inv_models.OrderLineItem.objects.all().delete()
        print("Deleting Orders...")
        inv_models.Order.objects.all().delete()
        print("Deleting SourceItems...")
        inv_models.SourceItem.objects.all().delete()
        print("Deleting Sources...")
        inv_models.Source.objects.all().delete()
        print("Deleting Items...")
        inv_models.Item.objects.all().delete()
        print("Deleting UnitSizes...")
        inv_models.UnitSize.objects.all().delete()
        print("Deleting Categories...")
        inv_models.Category.objects.all().delete()
        print("done.")
