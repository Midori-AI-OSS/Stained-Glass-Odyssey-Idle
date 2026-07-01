"""Warp engine constants — banner IDs, pity formula, promotion rates, and rarity labels."""

BANNER_IDS: tuple[str, ...] = (
    "fire",
    "ice",
    "wind",
    "lightning",
    "light",
    "dark",
    "yolo",
)

PITY_BASE_RATE: float = 0.00001          # 0.001% base for a 5★
PITY_SLOPE: float = 0.04999 / 159.0      # increment per pity count
PITY_HARD_GUARANTEE: int = 179           # 5★ guaranteed at pity >= 179

SIX_STAR_PROMO_RATE: float = 0.001       # 0.1% of 5★ hits promote to 6★
SEVEN_STAR_PROMO_RATE: float = 0.000001  # 0.0001% of 6★ hits promote to 7★

YOLO_RATE_MULTIPLIER: int = 50

RARITY_NONE: int | None = None   # fallback / non-character result
RARITY_5 = 5
RARITY_6 = 6
RARITY_7 = 7

PRISMATIC_FALLBACK_ID: str = "prismatic_shard"
