class Config:

    def __init__(
        self,
        open_lucky_blocks=True,
        open_party_boxes=True,
        open_large_gift_bags=True,
        open_small_gift_bags=True,
        open_pinatas=True,
        create_secret_keys=True,
        create_crystal_keys=True,
    ):
        self.OPEN_LUCKY_BLOCKS = open_lucky_blocks
        self.OPEN_PARTY_BOXES = open_party_boxes
        self.OPEN_LARGE_GIFT_BAGS = open_large_gift_bags
        self.OPEN_SMALL_GIFT_BAGS = open_small_gift_bags
        self.OPEN_PINATAS = open_pinatas
        self.CREATE_SECRET_KEYS = create_secret_keys
        self.CREATE_CRYSTAL_KEYS = create_crystal_keys