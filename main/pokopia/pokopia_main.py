from pokopia.items import Items, Traders, BuyFrom


def main():
    items = Items()
    traders = Traders()
    buy_sheet = BuyFrom()

    traders.update(items, buy_sheet)
    buy_sheet.update(items)

    items.validate()

    items.write_paint_trade_values()
    items.write_traders()
    buy_sheet.write()


main()
