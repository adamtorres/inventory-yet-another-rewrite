from django.core.management.base import BaseCommand
from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper


class MyBaseCommand(BaseCommand):
    def actual_handle(self, *args, **options):
        pass

    def handle(self, *args, **options):
        print_sql = False
        print_sql_location = False
        if options.get("verbosity", 1) >= 2:
            print_sql = True
        if options.get("verbosity", 1) >= 3:
            print_sql_location = True
        with monkey_patch_cursordebugwrapper(
                print_sql=print_sql, confprefix="SHELL_PLUS", print_sql_location=print_sql_location):
            self.actual_handle(*args, **options)
