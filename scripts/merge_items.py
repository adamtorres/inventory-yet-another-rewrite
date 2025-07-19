# ? "au jus mix", "au jus paste"
# Different "brownies", "brownie mix"
##### Left off at dairy


# "vegetarian refried bean" -> "refried bean"
# "montreal steak seasoning" -> "steak seasoning"
# "resse's pieces" -> "peanut butter candies"?
# "mrs dash" varieties?
# "cocoa mix" varieties?
# "yellow chips?"

# ./manage.py merge_items -k "egg" -d "eggs" "large eggs"
# ./manage.py merge_items -k "semisweet chocolate chip" -d "chocolate chips"
# ./manage.py merge_items -k "corn" -d "whole kernel sweet corn"
#   Found multiple Items when looking for 'corn'.
#   Item: 2368 / corn /  / canned & dry
#   Item: 2727 / corn /  / frozen
#    ↳ SourceItem(174): sysco sys cls corn whl kernel golden fcy 1x lb
#    ↳ SourceItem(175): sysco sysco classic corn whole kernel golden fancy 1x lb
#    ↳ SourceItem(537): sysco sysco classic corn whole kernel gr a p 1x lb
#    ↳ SourceItem(538): sysco sys rel corn whl kernel p 1x lb
#    ↳ SourceItem(1300): us foods corn, whole kernel golden fancy cnd 1x lb

# ./manage.py merge_items --safe -d "cranberry cocktail juice cup" "cranberry juice cocktail cup" "cranberry grape juice cup" "cranberry juice cup|frozen" -k "cranberry juice cup|canned & dry"
# ./manage.py merge_items --safe -d "grape juice cans" "grape juice cup" "grape juice cups"
# call_command('merge_items', '--safe', '-d', 'grape juice cans', 'grape juice cup', 'grape juice cups')
from django.core.management import call_command

def run():
    dupes = [
        ["candy corn", "candy corn autumn mix", "-k", "candy corn"],
        ["chocolate chips", "semisweet chocolate chip"],
        ["condensed tomato soup", "tomato soup", "-k", "tomato soup|canned & dry"],
        [
            "cranberry cocktail juice cup", "cranberry juice cocktail cup", "cranberry grape juice cup",
            "cranberry juice cup", "-k", "cranberry juice cup|canned & dry"],
        ["creamy peanut butter", "peanut butter", "-k", "peanut butter"],
        ["diced pears", "diced pear", "-k", "diced pear"],
        ["dried craisin packet", "craisins", "-k", "craisins"],
        ["egg", "eggs", "large eggs", "-k", "egg"],
        ["egg noodle", "egg noodle|frozen", "frozen egg noodle", "-k", "egg noodle|canned & dry"],
        ["elbow macaroni", "elbow noodle"],
        ["grape juice cans", "grape juice cup", "grape juice cups"],
        ["hershey kiss", "hershey kisses"],
        ["idahoan instant mashed potato", "dehydrated mashed potatoes", "-k", "dehydrated mashed potatoes"],
        ["idahoan instant scalloped potato", "instant scalloped potatoes", "-k", "instant scalloped potatoes"],
        ["jumbo maraschino cherry", "maraschino cherry", "large maraschino"],
        ["m&m's", "m&m’s", "m&m’s mini", "-k", "m&m's"],
        ["mayonnaise packet", "mayonnaise packets"],
        ["mild chunky salsa", "mild salsa"],
        ["milk chocolate chip", "milk chocolate chips"],
        ["mushroom stem & pieces", "mushroom stems and pieces"],
        ["mustard packets", "mustard packet"],
        ["orange juice", "orange juice cup"],
        ["oreo crumb", "medium oreo crumb"],
        ["parsley", "dried parsley flake"],
        ["sliced peach", "peach slice"],
        ["potato chip", "potato chips"],
        ["ranch dressing packet", "ranch dressing packets"],
        ["raspberry jello", "raspberry gelatin", "-k", "raspberry gelatin"],
        ["regular rolled oats", "rolled oats"],
        ["rice pilaf parboiled", "rice pilaf"],
        ["round tortilla chip", "tortilla chip"],
        ["scalloped potato casserole", "scalloped potato"],
        ["sliced apples", "sliced apple"],
        ["sliced pears in lite something", "sliced pear"],
        ["sliced pickled beets", "pickled beet"],
        ["spaghetti noodle", "spaghetti", "-k", "spaghetti"],
        ["sweet and sour sauce", "sweet & sour sauce"],
        ["sweetened applesauce", "applesauce", "unsweetened applesauce", "-k", "applesauce"],
        ["sweetened flake coconut", "flake coconut", "-k", "flake coconut"],
        ["white distilled vinegar", "distilled vinegar", "white vinegar"],
        ["whole kernel sweet corn", "corn", "-k", "corn|canned & dry"],
        ["whole wheat flour", "wheat flour", "-k", "wheat flour"],
    ]
    for dupe in dupes:
        print("=" * 80)
        call_command('merge_items', '--safe', '-d', *dupe)
    print("=" * 80)
