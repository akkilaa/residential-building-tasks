class Stock:
    def __init__(self, salt_bags: int, low_stock_threshold: int = 2):
        self.salt_bags = salt_bags
        self.low_stock_threshold = low_stock_threshold

    def decrement(self, amount: int) -> bool:
        """Reduce stock by amount. Returns True if stock is now at or below threshold."""
        self.salt_bags = max(0, self.salt_bags - amount)
        return self.salt_bags <= self.low_stock_threshold

    def add(self, amount: int) -> None:
        self.salt_bags += amount

    def is_low(self) -> bool:
        return self.salt_bags <= self.low_stock_threshold

    def to_dict(self) -> dict:
        return {
            "salt_bags": self.salt_bags,
            "low_stock_threshold": self.low_stock_threshold,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Stock":
        return cls(
            salt_bags=data.get("salt_bags", 0),
            low_stock_threshold=data.get("low_stock_threshold", 2),
        )
