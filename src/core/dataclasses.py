from typing import Any, Optional


class PowerSource:
    name: str
    type: str
    efficiency: float
    pmin: int
    pmax: int
    wind_capacity: float
    price: float

    found_load: Optional[float]

    def __init__(
        self,
        name: str,
        type: str,
        efficiency: float,
        pmin: int,
        pmax: int,
        price: float,
        wind_capacity: Optional[int] = None,
    ) -> None:
        # Input variables
        self.name = name
        self.type = type
        self.efficiency = efficiency
        self.pmin = pmin
        self.pmax = pmax
        self.price = price

        # Processed variables
        self.wind_capacity = (wind_capacity / 100) if wind_capacity is not None else 1.0
        self.found_load = None

    def min_load(self) -> float:
        return float(self.pmin)

    def max_load(self) -> float:
        return float(self.pmax) * self.wind_capacity

    def cost_price(self) -> float:
        """cost price = fuel_price / efficiency"""
        return self.price / self.efficiency


class Solution:
    charges: list[dict[str, Any]]
    reached_load: float

    def __init__(self) -> None:
        self.charges = []
        self.reached_load = 0.0

    def put(self, power_source: PowerSource, power: float) -> None:
        self.charges.append({"name": power_source.name, "p": power})
