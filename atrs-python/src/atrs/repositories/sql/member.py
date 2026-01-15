"""SQL queries for member repository"""

FIND_ONE_FOR_LOGIN = """
    SELECT
        m.customer_no,
        m.kanji_family_name,
        m.kanji_given_name,
        ml.password,
        ml.last_password,
        ml.login_date_time,
        ml.login_flg
    FROM member m
    JOIN member_login ml ON m.customer_no = ml.customer_no
    WHERE m.customer_no = :membership_number
"""

FIND_ONE = """
    SELECT
        m.customer_no,
        m.kanji_family_name,
        m.kanji_given_name,
        m.kana_family_name,
        m.kana_given_name,
        m.birthday,
        m.gender,
        m.tel,
        m.zip_code,
        m.address,
        m.mail,
        m.credit_no,
        m.credit_term,
        m.credit_type_cd,
        ml.password,
        ml.last_password,
        ml.login_date_time,
        ml.login_flg,
        ct.credit_type_cd,
        ct.credit_firm
    FROM member m
    JOIN member_login ml ON m.customer_no = ml.customer_no
    JOIN credit_type ct ON m.credit_type_cd = ct.credit_type_cd
    WHERE m.customer_no = :membership_number
"""

UPDATE_TO_LOGIN_STATUS = """
    UPDATE member_login
    SET login_date_time = :login_date_time, login_flg = :login_flg
    WHERE customer_no = :membership_number
"""

UPDATE_TO_LOGOUT_STATUS = """
    UPDATE member_login
    SET login_flg = :login_flg
    WHERE customer_no = :membership_number
"""

GET_NEXT_MEMBER_NUMBER = """
    SELECT TO_CHAR(NEXTVAL('sq_member_1'), 'FM0999999999')
"""

INSERT_MEMBER = """
    INSERT INTO member (
        customer_no, kanji_family_name, kanji_given_name,
        kana_family_name, kana_given_name, birthday, gender,
        tel, zip_code, address, mail, credit_no, credit_type_cd, credit_term
    ) VALUES (
        :customer_no, :kanji_family_name, :kanji_given_name,
        :kana_family_name, :kana_given_name, :birthday, :gender,
        :tel, :zip_code, :address, :mail, :credit_no, :credit_type_cd, :credit_term
    )
"""

INSERT_MEMBER_LOGIN = """
    INSERT INTO member_login (customer_no, password, last_password, login_flg)
    VALUES (:customer_no, :password, :last_password, :login_flg)
"""

UPDATE_MEMBER = """
    UPDATE member SET
        kanji_family_name = :kanji_family_name,
        kanji_given_name = :kanji_given_name,
        kana_family_name = :kana_family_name,
        kana_given_name = :kana_given_name,
        birthday = :birthday,
        gender = :gender,
        tel = :tel,
        zip_code = :zip_code,
        address = :address,
        mail = :mail,
        credit_no = :credit_no,
        credit_type_cd = :credit_type_cd,
        credit_term = :credit_term
    WHERE customer_no = :customer_no
"""

UPDATE_MEMBER_LOGIN_PASSWORD = """
    UPDATE member_login
    SET last_password = password, password = :password
    WHERE customer_no = :customer_no
"""
