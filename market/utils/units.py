import math


def reduce_dozens(quantity):
    if quantity < 12:
        return str(quantity)
    if (quantity / 12) == math.trunc(quantity / 12):
        return f"{round(quantity / 12)}dz"
    whole_dz = math.trunc(quantity / 12)
    partial_dz = quantity - (whole_dz * 12)
    if partial_dz == 6:
        return f"{whole_dz}.5dz"
    return f"{whole_dz}dz + {partial_dz}"


def reduce_quantity_by_pack(quantity, pack_quantity):
    if quantity < pack_quantity:
        # less than 1 pack
        return str(quantity)
    pack_suffix = humanize_pack_quantity(pack_quantity)
    if (quantity / pack_quantity) == math.trunc(quantity / pack_quantity):
        # evenly divisible by pack_quantity
        return f"{round(quantity / pack_quantity)} {pack_suffix}"
    whole_pack = math.trunc(quantity / pack_quantity)
    partial_pack = quantity - (whole_pack * pack_quantity)
    # if partial_pack == 6:
    #     return f"{whole_pack}.5dz"
    return f"{whole_pack} {pack_suffix} + {partial_pack}"


def humanize_pack_quantity(pack_quantity):
    match pack_quantity:
        case 1:
            return ""
        # case 6:
        #     return "½dz"
        case 12:
            return "dz"
        case _:
            return f"{pack_quantity}pk"
