"""SQL queries for flight repository"""

# Note: fare_type_list is built dynamically as parameterized IN clause
FIND_BY_VACANT_SEAT_SEARCH_CRITERIA = """
    SELECT
        f.departure_date,
        f.flight_name,
        f.fare_type_cd,
        f.vacant_num,
        f.boarding_class_cd
    FROM flight f
    JOIN fare_type ft ON f.fare_type_cd = ft.fare_type_cd
    JOIN flight_master fm ON f.flight_name = fm.flight_name
    JOIN route r ON fm.route_no = r.route_no
    WHERE f.fare_type_cd IN ({fare_types})
      AND r.dep_airport_cd = :dep_airport_cd
      AND r.arr_airport_cd = :arr_airport_cd
      AND f.departure_date = :departure_date
      AND f.boarding_class_cd = :boarding_class_cd
      AND :before_day_num BETWEEN ft.rsrv_available_end_day_num AND ft.rsrv_available_start_day_num
    ORDER BY ft.display_order ASC, fm.departure_time ASC
"""

FIND_ONE_FOR_UPDATE = """
    SELECT
        f.departure_date,
        f.flight_name,
        f.fare_type_cd,
        f.vacant_num,
        f.boarding_class_cd
    FROM flight f
    WHERE f.departure_date = :departure_date
      AND f.flight_name = :flight_name
      AND f.boarding_class_cd = :boarding_class_cd
      AND f.fare_type_cd = :fare_type_cd
    FOR UPDATE
"""

UPDATE_VACANT_NUM = """
    UPDATE flight
    SET vacant_num = :vacant_num
    WHERE departure_date = :departure_date
      AND flight_name = :flight_name
      AND boarding_class_cd = :boarding_class_cd
      AND fare_type_cd = :fare_type_cd
"""

EXISTS = """
    SELECT EXISTS (
        SELECT 1 FROM flight
        WHERE departure_date = :departure_date
          AND flight_name = :flight_name
          AND boarding_class_cd = :boarding_class_cd
          AND fare_type_cd = :fare_type_cd
    )
"""

FIND_ALL_FLIGHT_MASTER = """
    SELECT
        fm.flight_name,
        fm.departure_time,
        fm.arrival_time,
        fm.craft_type,
        r.route_no,
        r.basic_fare,
        r.flight_time,
        a_dep.airport_cd AS dep_airport_cd,
        a_dep.airport_name AS dep_airport_name,
        a_arr.airport_cd AS arr_airport_cd,
        a_arr.airport_name AS arr_airport_name
    FROM flight_master fm
    JOIN route r ON fm.route_no = r.route_no
    JOIN airport a_dep ON r.dep_airport_cd = a_dep.airport_cd
    JOIN airport a_arr ON r.arr_airport_cd = a_arr.airport_cd
"""

FIND_ALL_ROUTES = """
    SELECT
        r.route_no,
        r.dep_airport_cd,
        r.arr_airport_cd,
        r.flight_time,
        r.basic_fare
    FROM route r
"""

FIND_ALL_FARE_TYPES = """
    SELECT
        fare_type_cd, fare_type_name, discount_rate,
        rsrv_available_start_day_num, rsrv_available_end_day_num,
        passenger_min_num, display_order
    FROM fare_type
    ORDER BY display_order
"""

FIND_ALL_BOARDING_CLASSES = """
    SELECT
        boarding_class_cd, boarding_class_name,
        extra_charge, display_order
    FROM boarding_class
    ORDER BY display_order
"""

FIND_ALL_PEAK_TIMES = """
    SELECT
        peak_time_cd, peak_start_date, peak_end_date, multiplication_ratio
    FROM peak_time
"""

FIND_ALL_AIRPORTS = """
    SELECT airport_cd, airport_name, display_order
    FROM airport
    ORDER BY display_order
"""
