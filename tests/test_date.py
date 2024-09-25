from src.date_calculator import Calculator


def test_date_calculator():
    calculator = Calculator()
    result = calculator.calculate_date("09.07.2010 23:36", "0,45;12;1,2,6;3,6,14,18,21,24,28;1,2,3,4,5,6,7,8,9,10,11,12;")
    print(result)
