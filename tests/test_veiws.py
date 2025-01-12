import json
from unittest.mock import patch

from src.views import main


def test_main():
    """
    Тестирует вывод результатов работы всех функций из модуля utils.py
    """
    expected_result = {
        "greeting": "Добрый вечер",
        "cards": [
            {"last_digits": "*4556", "total_spent": 164.0, "cashback": 1.64},
            {"last_digits": "*7197", "total_spent": 1855.59, "cashback": 18.56},
        ],
        "top_transactions": [
            {
                "date": "03.06.2018 14:19:08",
                "amount": -22000.0,
                "category": "Переводы",
                "description": "Константин Ф.",
            },
            {"date": "06.06.2018 11:05:01", "amount": -10000.0, "category": "Переводы", "description": "Иван Ф."},
            {"date": "03.06.2018 10:23:52", "amount": -512.95, "category": "Супермаркеты", "description": "SPAR"},
            {"date": "05.06.2018 13:13:33", "amount": -353.94, "category": "Супермаркеты", "description": "Магнит"},
            {
                "date": "05.06.2018 16:36:50",
                "amount": -300.0,
                "category": "Ж/д билеты",
                "description": "Метро Санкт-Петербург",
            },
        ],
        "currency_rates": [{"currency": "USD", "rate": 101.64}, {"currency": "EUR", "rate": 104.23}],
        "stock_prices": [
            {"stock": "AAPL", "price": 236.85},
            {"stock": "AMZN", "price": 218.94},
            {"stock": "GOOGL", "price": 192.04},
            {"stock": "MSFT", "price": 418.95},
            {"stock": "TSLA", "price": 394.74},
        ],
    }

    with patch("src.views.get_greeting", return_value="Добрый вечер"), patch(
        "src.views.get_number_of_card_amount_cashback", return_value=expected_result["cards"]
    ), patch("src.views.get_top_5_of_transactions", return_value=expected_result["top_transactions"]), patch(
        "src.views.get_currency_rate", return_value=expected_result["currency_rates"]
    ), patch(
        "src.views.get_stocks_price", return_value=expected_result["stock_prices"]
    ):

        result = main("06.06.2018 20:52:16")
        if result is None:
            print("Результат: None")
        else:
            assert json.loads(result) == expected_result
