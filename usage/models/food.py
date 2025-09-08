from django.db import models


class Item(models.Model):
    ENTREE = "entree"
    SIDE = "side"
    DESSERT = "dessert"
    BREAD = "bread"
    TYPE_CHOICES = {
        ENTREE: "Entree",
        SIDE: "Side",
        DESSERT: "Dessert",
        BREAD: "Bread",
    }
    name = models.CharField(max_length=1024)
    description = models.CharField(max_length=1024, help_text="short description of this item.  Likely sides and such.")
    type = models.CharField(max_length=64, choices=TYPE_CHOICES)


class Meal(models.Model):
    date = models.DateField()
    comment = models.TextField(
        help_text="Generally about the meal or day.  Was it a fair week, a funeral, an oddly enjoyed meal?")


class MealItem(models.Model):
    meal = models.ForeignKey(
        "usage.Meal", on_delete=models.CASCADE, related_name="meal_items", related_query_name="meal_items")
    item = models.ForeignKey(
        "usage.Item", on_delete=models.CASCADE, related_name="meal_items", related_query_name="meal_items")
    ran_out = models.BooleanField(help_text="Ran out of this item during service")
    substitute = models.BooleanField(help_text="Used this to replace something that ran out")
    # TODO: Should substitute point to the MealItem which ran out?
    recent_leftover = models.BooleanField(help_text="left over from previous day or so.  Not frozen.")
    frozen_leftover = models.BooleanField(help_text="left over from some other week.  Was frozen.")
    comment = models.TextField(help_text="Anything special about this item on this specific meal?")
