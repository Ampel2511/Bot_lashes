class Lashes:
    price = ""

    async def __call__(self, new_price):
        self.price = new_price


price_lashes = Lashes()