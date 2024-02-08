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


class Solution:
    charges: list[dict[str, Any]]
    reached_load: float

    def __init__(self) -> None:
        self.charges = []
        self.reached_load = 0.0

    def put(self, power_source: PowerSource, power: float) -> None:
        self.charges.append({"name": power_source.name, "p": power})


class ProductionPlan:
    @staticmethod
    def proccess(data: dict[str, Any]) -> list[dict[str, Any]]:
        # 1. For all sources, create data objects
        wanted_load = data["load"]

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
        solution = ProductionPlan.find_best_solution(power_sources, wanted_load)

        # 3. Create output by powerplant name and load
        output = solution.charges
        return output

    @staticmethod
    def find_best_solution(
        power_sources: list[PowerSource], wanted_load: float
    ) -> Solution:
        power_sources = sorted(power_sources, key=lambda o: o.price)

        s = Solution()
        remaining_load = wanted_load
        reached_load = 0.0

        for pp in power_sources:
            # Find the adequate load
            max_load = pp.max_load()
            choosen_load = min(max_load, remaining_load)

            if choosen_load < pp.min_load():
                # If the defined load for this powerplant is lower than the min power (pmin)
                # We need to find a compromise
                print("error", choosen_load, pp.min_load())
                # raise x

            # Affect load
            reached_load += choosen_load
            remaining_load -= choosen_load

            s.put(pp, round(choosen_load, 1))

            if remaining_load == 0.0:
                break
        s.reached_load = reached_load

        return s
