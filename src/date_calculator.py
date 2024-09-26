import attr
from datetime import datetime


class LeapYearException(Exception):
    pass


@attr.s(auto_attribs=True, frozen=True)
class ScheduleIntervals:
    minutes: tuple
    hours: tuple
    weekdays: tuple
    monthdays: tuple
    months: tuple


class Calculator:
    def calculate_date(self, enter_date: str, scheduler_params_str: str):
        self._parse_actual_date(enter_date)
        self._parse_params(scheduler_params_str)
        self.check_actual_consistency()

        self._next_minute = self._get_next_greater(self._intervals.minutes, self._actual_minute)
        if self._next_minute == self._intervals.minutes[0] or not self._consistent:
            self._calculate_next_date_params()
        else:
            self._next_hour = self._actual_hour
            self._next_day = self._actual_day
            self._next_month = self._actual_month
            self._next_year = self._actual_year

        result_date = datetime(
            self._next_year,
            self._next_month,
            self._next_day,
            self._next_hour,
            self._next_minute
        )

        return result_date.strftime("%d.%m.%Y %H:%M")

    def check_actual_consistency(self):
        self._is_hour = self._actual_hour in self._intervals.hours
        self._is_day = self._actual_day in self._intervals.monthdays
        self._is_week_day = self._actual_week_day in self._intervals.weekdays
        self._is_month = self._actual_month in self._intervals.months
        self._consistent = all((
            self._is_hour,
            self._is_day,
            self._is_week_day,
            self._is_month
        ))

    def _calculate_next_date_params(self):
        if not self._is_month:
            self._next_month = self._get_next_greater(self._intervals.months, self._actual_month)
            self._next_year = self._get_year(self._actual_year, self._next_month, leap=False)
            try:
                next_day = self._get_next_day(self._next_year, self._next_month, next_first=True)
            except LeapYearException:
                self._next_year = self._get_year(self._next_year, self._next_month, leap=True)
                self._next_month = self._intervals.months[0]
                next_day = self._intervals.monthdays[0]
            if not self._check_week_day(
                self._next_year,
                self._next_month,
                next_day
            ):
                self._calculate_next_day(
                    self._next_year,
                    self._next_month,
                    self._intervals.monthdays[0]
                )
            else:
                self._next_day = next_day
            self._next_hour = self._intervals.hours[0]
            self._next_minute = self._intervals.minutes[0]
        elif not self._is_day or not self._is_week_day:
            self._calculate_next_day(
                self._actual_year,
                self._actual_month,
                self._actual_day
            )
            self._next_hour = self._intervals.hours[0]
            self._next_minute = self._intervals.minutes[0]
        else:
            next_hour = self._get_next_greater(self._intervals.hours, self._actual_hour)
            if next_hour == self._intervals.hours[0]:
                self._calculate_next_day(
                    self._actual_year,
                    self._actual_month,
                    self._actual_day
                )
                self._next_hour = self._intervals.hours[0]
                self._next_minute = self._intervals.minutes[0]
            else:
                self._next_minute = self._intervals.minutes[0]
                self._next_hour = next_hour
                self._next_day = self._actual_day
                self._next_month = self._actual_month
                self._next_year = self._actual_year

    def _calculate_next_day(self, actual_year, actual_month, actual_day):
        leap_year = False
        try:
            next_month_day = self._get_next_day(actual_year, actual_month, actual_day)
        except LeapYearException:
            leap_year = True
            actual_year = self._get_year(actual_year, actual_month, leap=True)
            actual_month = self._intervals.months[0]
            next_month_day = self._intervals.monthdays[0]
        if next_month_day != self._intervals.monthdays[0]:
            if self._check_week_day(actual_year, self._actual_month, next_month_day):
                self._next_day = next_month_day
                self._next_month = actual_month
                self._next_year = actual_year
            else:
                self._calculate_next_day(actual_year, actual_month, next_month_day)
        else:
            self._next_month = self._get_next_greater(self._intervals.months, self._actual_month)
            self._next_year = self._get_year(actual_year, actual_month, leap=leap_year)
            if not leap_year:
                if self._check_week_day(self._next_year, self._next_month, next_month_day):
                    self._next_day = next_month_day
            else:
                self._calculate_next_day(actual_year, actual_month, next_month_day)

    def _get_year(self, actual_year, actual_month, leap):
        if not leap:
            if actual_month == self._intervals.months[0]:
                return actual_year + 1
            else:
                return actual_year
        else:
            return self._get_next_leap_year_with_consistence_weak_day(actual_year)

    def _check_week_day(self, actual_year, actual_month, actual_day):
        date_object = datetime(actual_year, actual_month, actual_day)
        week_day = int((date_object.isoweekday() % 7) + 1)
        return week_day in self._intervals.weekdays

    def _get_next_greater(self, array, element):
        for number in array:
            if number > element:
                return number
        return array[0]

    def _get_next_day(self, actual_year, actual_month, actual_day = None, next_first = False):
        next_day = self._intervals.monthdays[0]
        if not next_first:
            next_day = self._get_next_greater(self._intervals.monthdays, actual_day)
        if next_day == 29 and actual_month == 2:
            if not self._check_leap_februaury(actual_year) and len(self._intervals.monthdays) > 1:
                next_day = self._get_next_greater(self._intervals.monthdays, next_day)
            else:
                raise LeapYearException()
        return next_day

    def _check_leap_februaury(self, actual_year):
        if (actual_year % 4 == 0 and actual_year % 100 != 0) or (actual_year % 400 == 0):
            return True
        return False

    def _get_next_leap_year_with_consistence_weak_day(self, actual_year):
        while True:
            if (actual_year % 4 == 0 and actual_year % 100 != 0) or (actual_year % 400 == 0):
                if self._check_week_day(
                    actual_year,
                    self._intervals.months[0],
                    self._intervals.monthdays[0]
                ):
                    return actual_year
            actual_year += 1

    def _parse_actual_date(self, enter_date: str):
        date_object = datetime.strptime(enter_date, "%d.%m.%Y %H:%M")

        self._actual_year = date_object.year
        self._actual_month = date_object.month
        self._actual_day = date_object.day
        self._actual_hour = date_object.hour
        self._actual_minute = int(date_object.minute)
        self._actual_week_day = int((date_object.isoweekday() % 7) + 1)


    def _parse_params(self, scheduler_params_str: str):
        params_list = scheduler_params_str.split(';')
        self._intervals = ScheduleIntervals(
            minutes=self._get_elements(params_list[0]),
            hours=self._get_elements(params_list[1]),
            weekdays=self._get_elements(params_list[2]),
            monthdays=self._get_elements(params_list[3]),
            months=self._get_elements(params_list[4])
        )

    def _get_elements(self, interval_str: str):
        elements = list(map(int, interval_str.split(",")))
        elements.sort()
        return tuple(elements)
