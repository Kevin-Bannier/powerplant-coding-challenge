from typing import Any, Optional

from .dataclasses import PowerSource, Solution


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

        # 2. Find the best solution
        solution = ProductionPlan.find_best_solution(power_sources, wanted_load)

        # 3. Create output by powerplant name and load
        output = solution.charges
        return output

    @staticmethod
    def find_best_solution(
        power_sources: list[PowerSource], wanted_load: float
    ) -> Solution:
        # Define the first criteria: price
        # 1. Sort power plants by cost price (cost price = fuel_price / efficiency)
        power_sources = sorted(power_sources, key=lambda o: o.cost_price())

        s = Solution()
        remaining_load = wanted_load
        reached_load = 0.0

        # WARNING. List of constraints:
        # - Wind tubine can be used at 0% or 100% capacity
        # - Others powerplants can have a mininum load to be working (variable pmin)

        # 2. Loop on all power plants to distribute the load
        for pp in power_sources:
            # Find the adequate load for this powerplant
            choosen_load = min(pp.max_load(), remaining_load)

            # If the wind turbine is not used at 100% capacity, we decide to not using it
            if pp.type == "windturbine" and choosen_load != pp.max_load():
                # raise Exception(
                #     f"Wind max power not reached: {pp.name} {choosen_load}, {pp.max_load()}"
                # )
                s.put(pp, 0.0)
                continue

            if choosen_load < pp.min_load():
                # If the defined load for this powerplant is lower than the min power (pmin)
                # We need to find a compromise with the minimal cost. There is 2 solutions:
                # - 1. Reduce the load of previous powerplants
                # - 2. Power on a next powerplant

                print("error", choosen_load, pp.min_load())
                raise Exception(
                    f"Minimal power not reached: {pp.name} {choosen_load} < {pp.min_load()}"
                )

            # Affect load
            reached_load += choosen_load
            remaining_load -= choosen_load

            s.put(pp, round(choosen_load, 1))

            # TODO(kba): do not test equality between 2 floats
            if remaining_load == 0.0:
                break

        s.reached_load = reached_load

        return s
