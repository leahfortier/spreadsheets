from pokopia.faves import Faves
from pokopia.items import Items, Traders
from pokopia.ref import Ref


def sheet_update(ref: Ref, items: Items):
    traders = Traders()

    traders.update(items)
    items.update(ref)

    items.validate()

    items.write_paint_trade_values()
    items.write_traders()
    items.write_faves()


def serebii_compare(ref: Ref, items: Items):
    faves = Faves(items, ref)
    faves.validate()


def main():
    ref = Ref()
    items = Items(ref)

    sheet_update(ref, items)
    serebii_compare(ref, items)


main()
