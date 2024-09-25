import attr
from datetime import datetime


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
            if self._next_month == self._intervals.months[0]:
                self._next_year = self._actual_year + 1
            else:
                self._next_year = self._actual_year

            if not self._check_week_day(
                self._next_year,
                self._next_month,
                self._intervals.monthdays[0]
            ):
                self._calculate_next_day(
                    self._intervals.monthdays[0],
                    self._next_month,
                    self._next_year
                )
            else:
                self._next_day = self._intervals.monthdays[0]
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
        next_month_day = self._get_next_greater(self._intervals.monthdays, actual_day)
        if next_month_day != self._intervals.monthdays[0]:
            if self._check_week_day(self._actual_year, self._actual_month, next_month_day):
                self._next_day = next_month_day
                self._next_month = actual_month
                self._next_year = actual_year
            else:
                self._calculate_next_day(actual_year, actual_month, next_month_day)
        else:
            self._next_month = self._get_next_greater(self._intervals.months, self._actual_month)
            if self._next_month == self._intervals.months[0]:
                self._next_year = actual_year + 1
            else:
                self._next_year = actual_year
            if self._check_week_day(self._next_year, self._next_month, next_month_day):
                self._next_day = next_month_day
            else:
                self._calculate_next_day(actual_year, actual_month, next_month_day)


    def _check_week_day(self, actual_year, actual_month, actual_day):
        date_object = datetime(actual_year, actual_month, actual_day)
        week_day = int((date_object.isoweekday() % 7) + 1)
        return week_day in self._intervals.weekdays

    def _get_next_greater(self, array, element):
        for number in array:
            if number > element:
                return number
        return array[0]

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
