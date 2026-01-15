"""SQL queries for reservation repository"""

GET_NEXT_RESERVE_NO = """
    SELECT TO_CHAR(NEXTVAL('sq_reservation_1'), 'FM0999999999')
"""

GET_NEXT_RESERVE_FLIGHT_NO = """
    SELECT NEXTVAL('sq_reserve_flight_1')
"""

GET_NEXT_PASSENGER_NO = """
    SELECT NEXTVAL('sq_passenger_1')
"""

INSERT_RESERVATION = """
    INSERT INTO reservation (
        reserve_no, reserve_date, total_fare,
        rep_family_name, rep_given_name, rep_age, rep_gender,
        rep_tel, rep_mail, rep_customer_no
    ) VALUES (
        :reserve_no, :reserve_date, :total_fare,
        :rep_family_name, :rep_given_name, :rep_age, :rep_gender,
        :rep_tel, :rep_mail, NULLIF(:rep_customer_no, '')
    )
"""

INSERT_RESERVE_FLIGHT = """
    INSERT INTO reserve_flight (
        reserve_flight_no, reserve_no, departure_date,
        flight_name, boarding_class_cd, fare_type_cd
    ) VALUES (
        :reserve_flight_no, :reserve_no, :departure_date,
        :flight_name, :boarding_class_cd, :fare_type_cd
    )
"""

INSERT_PASSENGER = """
    INSERT INTO passenger (
        passenger_no, reserve_flight_no, family_name, given_name,
        age, gender, customer_no
    ) VALUES (
        :passenger_no, :reserve_flight_no, :family_name, :given_name,
        :age, :gender, NULLIF(:customer_no, '')
    )
"""

FIND_ALL_BY_MEMBERSHIP_NUMBER_FOR_REPORT = """
    SELECT
        r.reserve_no,
        r.reserve_date,
        r.total_fare,
        r.rep_family_name,
        r.rep_given_name,
        rf.reserve_flight_no,
        rf.departure_date,
        rf.flight_name,
        a_dep.airport_name AS dep_airport_name,
        a_arr.airport_name AS arr_airport_name
    FROM reservation r
    JOIN reserve_flight rf ON rf.reserve_no = r.reserve_no
    JOIN flight_master fm ON rf.flight_name = fm.flight_name
    JOIN route rt ON fm.route_no = rt.route_no
    JOIN airport a_dep ON rt.dep_airport_cd = a_dep.airport_cd
    JOIN airport a_arr ON rt.arr_airport_cd = a_arr.airport_cd
    WHERE r.rep_customer_no = :membership_number
    ORDER BY r.reserve_no, rf.reserve_flight_no
"""
