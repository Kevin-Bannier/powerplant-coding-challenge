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
        return float(self.pmin) * self.wind_capacity


class ProductionPlan:
    @staticmethod
    def proccess(data: dict[str, Any]) -> list[dict[str, Any]]:
        # 1. For all sources, create data objects
        price_gas = data["fuels"]["gas(euro/MWh)"]
        price_ker = data["fuels"]["kerosine(euro/MWh)"]
        wind_capacity = data["fuels"]["wind(%)"]

        power_sources: list[PowerSource] = []
        for pp in data["powerplants"]:
            price: float = 0.0
            if pp["type"] == "gasfired":
                price = price_gas
            elif pp["type"] == "turbojet":
                price = price_ker

            wind: Optional[float] = (
                wind_capacity if pp["type"] == "windturbine" else None
            )

            power_source = PowerSource(
                pp["name"],
                pp["type"],
                pp["efficiency"],
                pp["pmin"],
                pp["pmax"],
                price=price,
                wind_capacity=wind,
            )
            power_sources.append(power_source)

        # 2. Sort by price
        power_sources = sorted(power_sources, key=lambda o: o.price)

        # 3. Create output by powerplant name and load
        output = [
            {"name": o.name, "price": o.price, "p": o.found_load} for o in power_sources
        ]
        # output = [{"name": o.name, "p": o.found_load} for o in power_sources]
        return output
