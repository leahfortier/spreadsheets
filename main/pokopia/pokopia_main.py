from pokopia.items import Items, Traders


def main():
    items = Items()
    traders = Traders()

    traders.update(items)

    items.write_trade_value()
    items.write_traders()


main()
