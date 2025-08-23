import functools
import itertools
import operator

from django.forms import models

# An attempt to add grouped options to a ModelChoiceField as seen in the Django ticket
# https://code.djangoproject.com/ticket/27331.  The ticket is closed as "wontfix" because of a terminology reason.
# A comment at the end of the thread claims the fix doesn't work anymore because of a change in 2016
# https://github.com/django/django/commit/5ec64f96b2d83ec3c0ef574f52e4767a440017b8.

# This site shows this possible fix and is dated 2019.
# https://simpleisbetterthancomplex.com/tutorial/2019/01/02/how-to-implement-grouped-model-choice-field.html
# Seems to work fine.

class GroupedModelChoiceIterator(models.ModelChoiceIterator):
    def __init__(self, field, groupby):
        self.groupby = groupby
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset
        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, objs in itertools.groupby(queryset, self.groupby):
            yield (group, [self.choice(obj) for obj in objs])


class GroupedModelChoiceField(models.ModelChoiceField):
    def __init__(self, *args, choices_groupby, **kwargs):
        if isinstance(choices_groupby, str):
            choices_groupby = operator.attrgetter(choices_groupby)
        elif not callable(choices_groupby):
            raise TypeError('choices_groupby must either be a str or a callable accepting a single argument')
        self.iterator = functools.partial(GroupedModelChoiceIterator, groupby=choices_groupby)
        super().__init__(*args, **kwargs)
