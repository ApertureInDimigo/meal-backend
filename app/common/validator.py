from marshmallow import Schema, fields, ValidationError
import datetime

def date_validator(str_date):

    try:
        year = int(str_date[0:4])
        month = int(str_date[4:6])
        day = int(str_date[6:])

        date = datetime.date(year=year, month=month ,day=day)

        if not (datetime.date(year=2000, month = 1, day = 1) <= date  <= datetime.date(year=2025, month = 1, day = 1)):
            raise ValidationError("날짜 포맷이 올바르지 않습니다.")


    except:

        raise ValidationError("날짜 포맷이 올바르지 않습니다.")

    # if (not (2000 <= year <= 2025)) or (not (1 <= month <= 12)) or (not (1 <= day <= 31)):


    #
    #
    # if n < 0:
    #     raise ValidationError("Quantity must be greater than 0.")
    # if n > 30:
    #     raise ValidationError("Quantity must not be greater than 30.")