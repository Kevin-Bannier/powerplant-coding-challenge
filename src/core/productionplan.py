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

        # 2. Group powerplants by cost price
        # power_sources_grouped = []
        pp_by_cost_prices = {}
        for pp in power_sources:
            if pp.cost_price() not in pp_by_cost_prices:
                pp_by_cost_prices[pp.cost_price()] = []
            pp_by_cost_prices[pp.cost_price()].append(pp)

        pp_by_cost_prices = dict(sorted(pp_by_cost_prices.items()))
        # print("Powerplants sorted by cost prices")
        # for price, pps in pp_by_cost_prices.items():
        #     print("- ", price, [pp.name for pp in pps])
        # print()

        s = Solution()
        remaining_load = wanted_load

        # WARNING. List of constraints:
        # - Wind tubine can be used at 0% or 100% capacity
        # - Others powerplants can have a mininum load to be working (variable pmin)

        # 3. Loop on all power plants to distribute the load
        for powerplants in pp_by_cost_prices.values():
            list_of_pps_output, remaining_load = (
                ProductionPlan.find_compromise_pp_at_same_cost_price(
                    powerplants, remaining_load
                )
            )
            for pp in list_of_pps_output:
                s.put(pp[0], pp[1])
                print("- ", pp[0].name, pp[1])

        s.reached_load = wanted_load - remaining_load

        return s

    @staticmethod
    def find_compromise_pp_at_same_cost_price(
        powerplants: list[PowerSource],
        remaining_load: float,
    ) -> list[tuple[PowerSource, float]]:
        list_of_pps_output = []

        for pp in powerplants:
            # Find the adequate load for this powerplant
            if remaining_load != 0.0:

                choosen_load = min(pp.max_load(), remaining_load)
                # If the wind turbine is not used at 100% capacity, we decide to not using it
                if pp.type == "windturbine" and choosen_load != pp.max_load():
                    list_of_pps_output.append((pp, 0.0))
                    continue

                if choosen_load < pp.min_load():
                    # If the defined load for this powerplant is lower than the min power (pmin)
                    # We need to find a compromise with the minimal cost.
                    # We choose to reduce power of previous powerpants

                    delta_too_much_load = pp.min_load() - choosen_load
                    choosen_load = pp.min_load()
                    ProductionPlan.reduce_loads_of_previous_powerplants(
                        list_of_pps_output, delta_too_much_load
                    )
                    remaining_load += delta_too_much_load

                # Affect load
                remaining_load -= choosen_load
            else:
                choosen_load = 0.0

            list_of_pps_output.append((pp, round(choosen_load, 1)))

        return list_of_pps_output, remaining_load

    @staticmethod
    def reduce_loads_of_previous_powerplants(
        powerplants: list[tuple[PowerSource, float]],
        delta_too_much_load: float,
    ) -> None:
        for i, (powerplant, power) in enumerate(powerplants):
            power_reduced = max(power - delta_too_much_load, powerplant.min_load())

            delta_too_much_load -= power - power_reduced
            powerplants[i] = (powerplant, power_reduced)

        if delta_too_much_load != 0:
            pp_str = ",".join(pp[0].name for pp in powerplants)
            raise Exception(
                f"Cannot find a compromise of power loads of power plants:{pp_str}"
            )
