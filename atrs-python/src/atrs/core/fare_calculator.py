"""Fare calculation utilities"""

import math
from datetime import date

from ..models import BoardingClass, FareType, PeakTime


class FareCalculator:
    """Utility class for fare calculations"""

    # Default peak time ratio (100% = no adjustment)
    NORMAL_MULTIPLICATION_RATIO = 100

    @staticmethod
    def ceil_fare(fare: int) -> int:
        """Round fare up to nearest 100 yen"""
        return int(math.ceil(fare / 100) * 100)

    @staticmethod
    def calculate_basic_fare(
        basic_fare_of_route: int,
        boarding_class: BoardingClass,
        peak_times: list[PeakTime],
        departure_date: date,
    ) -> int:
        """
        Calculate basic fare with boarding class surcharge and peak time adjustment.

        Formula: (route_fare + class_surcharge) * peak_ratio / 100
        """
        # Get boarding class extra charge
        boarding_class_fare = boarding_class.extra_charge

        # Get peak time multiplication ratio
        multiplication_ratio = FareCalculator._get_multiplication_ratio(
            peak_times, departure_date
        )

        # Calculate basic fare
        basic_fare = int(
            (basic_fare_of_route + boarding_class_fare) * (multiplication_ratio / 100)
        )

        return basic_fare

    @staticmethod
    def calculate_fare(basic_fare: int, discount_rate: int) -> int:
        """
        Calculate final fare with discount applied.

        Formula: basic_fare * (1 - discount_rate/100), rounded up to 100 yen
        """
        fare = int(basic_fare * (1 - discount_rate / 100))
        return FareCalculator.ceil_fare(fare)

    @staticmethod
    def calculate_total_fare(
        flights: list,  # List of Flight with route info
        passengers: list,  # List of Passenger
        boarding_classes: dict[str, BoardingClass],
        peak_times: list[PeakTime],
        adult_min_age: int = 12,
        child_fare_rate: int = 50,
    ) -> int:
        """
        Calculate total fare for all flights and passengers.

        Child fare = basic_fare * child_rate/100 - discount
        Adult fare = fare with discount applied
        """
        # Count adults and children
        child_count = sum(1 for p in passengers if p.age < adult_min_age)
        adult_count = len(passengers) - child_count

        total_fare = 0

        for flight in flights:
            # Get route basic fare
            route = flight.flight_master.route
            basic_fare_of_route = route.basic_fare

            # Get boarding class
            boarding_class = boarding_classes.get(flight.boarding_class_cd.value)

            # Calculate basic fare with peak time
            basic_fare = FareCalculator.calculate_basic_fare(
                basic_fare_of_route,
                boarding_class,
                peak_times,
                flight.departure_date,
            )

            # Get discount rate
            discount_rate = flight.fare_type.discount_rate

            # Adult fare (with discount)
            adult_fare = FareCalculator.calculate_fare(basic_fare, discount_rate)

            # Child fare calculation
            # child_fare = basic_fare * child_rate/100 - basic_fare * discount_rate/100
            child_fare = int(basic_fare * (child_fare_rate - discount_rate) / 100)

            # Flight total
            flight_total = (adult_fare * adult_count) + (child_fare * child_count)
            total_fare += flight_total

        # Round total to nearest 100 yen
        return FareCalculator.ceil_fare(total_fare)

    @staticmethod
    def _get_multiplication_ratio(peak_times: list[PeakTime], departure_date: date) -> int:
        """Get peak time multiplication ratio for a given date"""
        for peak_time in peak_times:
            if peak_time.peak_start_date <= departure_date <= peak_time.peak_end_date:
                return peak_time.multiplication_ratio

        return FareCalculator.NORMAL_MULTIPLICATION_RATIO
