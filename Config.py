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
        open_free_gifts=True,
        open_rank_rewards=True,
        max_orange_boosts=True,
        max_banana_boosts=True,
        max_apple_boosts=True,
        max_pineapple_boosts=True,
        max_rainbow_fruits_boosts=True,
        save_logs=False,
    ):
        self.OPEN_LUCKY_BLOCKS = open_lucky_blocks
        self.OPEN_PARTY_BOXES = open_party_boxes
        self.OPEN_LARGE_GIFT_BAGS = open_large_gift_bags
        self.OPEN_SMALL_GIFT_BAGS = open_small_gift_bags
        self.OPEN_PINATAS = open_pinatas
        self.CREATE_SECRET_KEYS = create_secret_keys
        self.CREATE_CRYSTAL_KEYS = create_crystal_keys
        self.OPEN_FREE_GIFTS = open_free_gifts
        self.OPEN_RANK_REWARDS = open_rank_rewards
        self.MAX_ORANGE_BOOSTS = max_orange_boosts
        self.MAX_APPLE_BOOSTS = max_apple_boosts
        self.MAX_BANANA_BOOSTS = max_banana_boosts
        self.MAX_PINEAPPLE_BOOSTS = max_pineapple_boosts
        self.MAX_RAINBOW_FRUITS_BOOSTS = max_rainbow_fruits_boosts
        self.SAVE_LOGS = save_logs
