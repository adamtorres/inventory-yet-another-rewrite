How are different items represented in the system?
This is a brainstorming file for how to handle quantity and pricing for the variety of items at the senior center.

# Scenarios

1. 4 bags of 50# all purpose flour
   * Open a bag and write off the whole bag even if only a cup is used.
   * Want price per lb
2. 3 cases each with 6 #10 cans of pickled beets
   * Want price per can
   * Weight per can varies depending on the item.  Do we want to include the weight?
   * Including weight would allow conversions in recipes
3. 2 boxes each with 6 boxes of 5# brownie mix
   * Want price per inner box
   * Do we care about price/lb?  1 box of Sysco is 5lb while 1 box of BakersSource is 6lb
4. 1 box containing 200 single-serving packets of craisins
   * Want price per packet
   * Do we want or care about price per lb?  To compare with buying a giant bag of craisin for in-house?
5. 2 boxes each containing 15dz eggs
   * Want price per egg, dz, flat
6. 2 boxes each containing 8 packs each containing 4 single-serving pudding cups
   * Want price per single-serving pudding cup
   * Do we care about the 4pack price?
   * Means $box price \over 8 packs * 4 cups$ 
7. 2 boxes each containing 5 9-12#avg briskets
   * Take the average of the 9-12?  Or just ignore that in the calculation?
   * $total weight / briskets = actual Average Brisket Weight$ then $per Pack Cost / actual Average Brisket Weight = per
     Brisket Cost$
   * Calculate and store an average per brisket weight?  Should the unit amount decimal value be changed to this value?
8. 2 boxes each containing 4 10# chubs of ground beef
   * Actual weight is not always exactly 10lbs.  Probably should treat this the same as the brisket.

## Properties and functions important to quantities and amounts

Item
 * latest_order
 * price_in_unit
 * total_ordered

SourceItem
 * unit_size
 * unit_amount
 * unit_amount_text
 * subunit_size
 * subunit_amount
 * subunit_amount_text
 * Q: Should this have some price functions which just use the most recently ordered item?

OrderLineItem
 * source_item - links to SourceItem
 * quantity_ordered
 * quantity_delivered
 * per_pack_price
 * extended_price
 * tax
 * per_weight_price
 * per_pack_weights
 * total_weight
 * fn per_unit_price
 * fn per_subunit_price
 * fn per_unitsize_price

## Ideas

* Have a list in Item define what kinds of prices we want.
  * For each of those, have a formula that describes how to get it
    * Ex: Egg would have "flat price", "dozen", and "count"
    * Flat = $\$40 per box \over (180 eggs / 30 eggs per flat)$ = $\$40 per box \over 6 flats$ = \$6.67 per flat
    * Dozen = $\$40 per box \over (180 eggs / 12 eggs per dozen)$ = $\$40 per box \over 15 dozens$ = \$2.67 per dozen
    * Count = $\$40 per box \over 180 eggs$ = \$0.2222 per egg
  * When a SourceItem is made, it copies the Item's pricing formula?
    * Meh: means changes aren't automagically copied.
  * SourceItem just uses its linked Item's formula?
    * Better but what if an 18 pack of eggs is used?  the per flat price would be meaningless.
    * Add a criteria to the pricing formula for minimum quantity?
    * Price per unit that is larger isn't necessarily bad
      * Would need a common unit when comparing a 12oz bag of X to a 50lb bag.  The per lb would likely be a nicer
        number to use.
  * Have SourceItem activate/deactivate Item pricing formula?
    * SourceItem for an 18 pack would not activate the flat pricing?
    * Or have it opt-out instead of opt-in.  SourceItem would have to list pricing it doesn't want so any new formulas
      added to Item will automatically apply to existing SourceItems.
* Have all styles of price calculation happen regardless of product
  * Customization on SourceItem tells which to use
  * by "happen", I mean have functions to do the calculations but the customization on SourceItem tells which to call.
  * 
* Should price formulas be a discrete object?
  * Allows multiple Items to use the same tested formula instead of having to copy/paste.
  * Changes to a formula would propagate to all Items instead of lots of copy/paste or filter/update.
    * Hastily done filter/update could affect others or exclude some
  * Named/described formulas might help guard against incorrect usage
* Need a cheat sheet with a variety of products and how to fill in the entry form.
  * Examples like this would help with data consistency
  * Have this available as a pop-up link on the entry form for easy access
* Base unit
  * Smallest unit that makes sense for inventory
  * Can be smaller units but only for things like \$/lb on bags of flour
  * Means no "subunit" as there shouldn't be such for inventory
  * Packs would be some multiple of base unit
  * Examples:
    * #10 cans would have base unit = #10 can, pack would be 6 of those
    * 50# bag of flour, base unit would be the bag? and base unit amount would be 50? or 1? leaving weight to be 50?
      * Weight has nothing to do with the pricing of a bag of flour so weight should not be part of the base unit.
      * Still want to track the weight as part of SourceItem since places sell 25lb and 50lb bags
    * 15dz pack of eggs would have a single egg as the base unit.  Or, more generically, "count"
      * "count" would allow the same unit to be used for mayo packets, craisins, pudding cups, etc.
    * a 48 pack of pudding cups came as 8 packs of 6 cups.
      * base unit is a pudding cup
* Really need a definition page
  * unit - single item that is the smallest that can be entered on the usage form
    * For some items, this is what is sold to us
      * bag of flour, rice, oats, potatoes, etc
    * Might be using the term "base unit" to make it clear this is the smallest unit for inventory purposes.
  * pack - a grouping of unit that might be what is sold to us
    * 200 pack of craisins, 6 pack of #10 cans
  * case - a grouping of packs
    * Likely means the pack is a retail package?
    * case of 8 packs of 6 pudding cups.  Each pack appeared to be retail packaging.
    * 10 boxes("pack" but that sounds weird to say here) of 200 gloves each.