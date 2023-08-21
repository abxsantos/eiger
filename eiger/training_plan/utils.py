from datetime import date, datetime, timedelta


def get_dates_in_week(year, week_number):
    # Calculate the start date of the week
    start_date = datetime.strptime(
        f'{year}-{week_number}-1', '%Y-%W-%w'
    ).date()

    # Create a list of dates for the entire week
    dates_in_week = [start_date + timedelta(days=i) for i in range(7)]

    return dates_in_week


def get_specific_date(week_number: int, day_of_week: str) -> date:
    days_of_week_map = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6,
    }

    current_year = datetime.now().year  # Get the current year
    day_of_week_value = days_of_week_map[day_of_week.lower()]

    # Find the first day of the year that matches the desired day of the week
    first_day_of_year = datetime(current_year, 1, 1)
    days_to_add = (day_of_week_value - first_day_of_year.weekday() + 7) % 7
    first_day_of_week = first_day_of_year + timedelta(days=days_to_add)

    # Calculate the specific date based on the week number
    specific_date = first_day_of_week + timedelta(weeks=week_number - 1)

    return specific_date.date()
