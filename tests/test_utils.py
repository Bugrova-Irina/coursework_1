import json
import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

import numpy as np
import pandas as pd
import pytest
from numpy._core.numeric import nan

from src.utils import (get_currency_rate, get_greeting, get_number_of_card_amount_cashback, get_stocks_price,
                       get_top_5_of_transactions, get_transactions_from_file)


@pytest.mark.parametrize(
    "date, expected",
    [
        ("26.12.2021 15:31:11", "Добрый день"),
        ("31.12.2021 00:12:53", "Доброй ночи"),
        ("24.12.2021 19:30:55", "Добрый вечер"),
        ("28.12.2021 09:36:56", "Доброе утро"),
    ],
)
def test_get_greeting(date, expected):
    """
    Тестирует выдачу приветствия в соответствии
    со временем, указанном в дате
    """
    assert get_greeting(date) == expected


def test_get_empty_date_for_greeting(empty_date):
    """
    Проверяет работу функции при вводе пустой даты
    """
    with pytest.raises(Exception):
        get_greeting(empty_date)


def test_get_bad_date_for_greeting(bad_date):
    """
    Проверяет работу функции при вводе даты с ошибкой
    """
    with pytest.raises(ValueError):
        get_greeting(bad_date)


@patch("utils.get_transactions_from_xlsx")
def test_get_transactions_from_file(mock_get_transactions_from_xlsx, mock_transactions_for_period):
    """
    Тестируем получение списка транзакций за выбранный период
    """
    mock_get_transactions_from_xlsx.return_value = mock_transactions_for_period

    result = get_transactions_from_file("03.06.2018 10:23:52")

    expected_result = [
        {
            "Дата операции": "03.06.2018 10:23:52",
            "Дата платежа": "05.06.2018",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -512.95,
            "Валюта операции": "RUB",
            "Сумма платежа": -512.95,
            "Валюта платежа": "RUB",
            "Кэшбэк": nan,
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "SPAR",
            "Бонусы (включая кэшбэк)": 10,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 512.95,
        },
        {
            "Дата операции": "02.06.2018 14:07:54",
            "Дата платежа": "05.06.2018",
            "Номер карты": "*4556",
            "Статус": "OK",
            "Сумма операции": -164.0,
            "Валюта операции": "RUB",
            "Сумма платежа": -164.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": 1.0,
            "Категория": "Ж/д билеты",
            "MCC": 4111.0,
            "Описание": "Северо-Западная пригородная пассажирская компания",
            "Бонусы (включая кэшбэк)": 1,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 164.0,
        },
    ]

    # assert result == expected_result

    for index, item in enumerate(expected_result):
        if np.isnan(item["Кэшбэк"]):
            assert np.isnan(result[index]["Кэшбэк"])  # проверка на nan
        else:
            assert item["Кэшбэк"] == result[index]["Кэшбэк"]


# @patch("utils.get_transactions_from_xlsx")
# def test_get_empty_transactions_from_file(mock_get_transactions_from_xlsx, mock_empty_transactions_for_period):
#     """
#     Тестируем обработку пустого списка транзакций за выбранный период
#     """
#     mock_get_transactions_from_xlsx.return_value = mock_empty_transactions_for_period
#
#     result = get_transactions_from_file("03.06.2018 10:23:52")
#
#     assert result == []

# with patch("utils.get_transactions_from_xlsx") as mock_get_transactions_from_xlsx:
#     mock_get_transactions_from_xlsx.return_value = mock_empty_transactions_for_period
#     print(mock_get_transactions_from_xlsx.return_value)
#     result = get_transactions_from_file("03.06.2018 10:23:52")
#     print(result)
#     assert result == []


def test_get_number_of_card_amount_cashback(mock_transactions_for_period):
    """
    Проверяет вывод последних 4 цифр каждой карты из списка транзакций,
    сумму расходов и сумму кэшбэка по каждой карте
    """
    transactions_df = pd.DataFrame(mock_transactions_for_period)
    result = get_number_of_card_amount_cashback(transactions_df)
    assert result == [
        {"last_digits": "*4556", "total_spent": 164.0, "cashback": 1.64},
        {"last_digits": "*7197", "total_spent": 512.95, "cashback": 5.13},
    ]


def test_get_number_of_card_amount_cashback_from_empty_transactions():
    """
    Проверяет вывод ошибки при обработке пустого списка транзакций
    """
    transactions_df = pd.DataFrame([])
    with pytest.raises(ValueError):
        get_number_of_card_amount_cashback(transactions_df)


def test_get_number_of_card_amount_cashback_from_bad_transactions():
    """
    Проверяет вывод ошибки при обработке некорректного списка транзакций
    """
    transactions_df = pd.DataFrame(["dfdf"])
    result = get_number_of_card_amount_cashback(transactions_df)
    assert result == None


def test_get_top_5_of_transactions(mock_transactions_for_period):
    """Проверяет вывод 5 транзакций с самой большой суммой платежа"""
    transactions_df = pd.DataFrame(mock_transactions_for_period)
    result = get_top_5_of_transactions(transactions_df)
    assert result == [
        {"date": "03.06.2018 14:19:08", "amount": -22000.0, "category": "Переводы", "description": "Константин Ф."},
        {"date": "03.06.2018 10:23:52", "amount": -512.95, "category": "Супермаркеты", "description": "SPAR"},
        {
            "date": "02.06.2018 14:07:54",
            "amount": -164.0,
            "category": "Ж/д билеты",
            "description": "Северо-Западная пригородная пассажирская компания",
        },
    ]


def test_get_top_5_of_transactions_from_empty_transactions():
    """Проверяет вывод ошибки при обработке пустого списка транзакций"""
    transactions_df = pd.DataFrame([])
    with pytest.raises(ValueError):
        get_top_5_of_transactions(transactions_df)


def test_get_top_5_of_transactions_from_bad_transactions():
    """Проверяет вывод ошибки при обработке некорректного списка транзакций"""
    transactions_df = pd.DataFrame(["jjj"])
    result = get_top_5_of_transactions(transactions_df)
    assert result == None


class TestGetCurrencyRate(unittest.TestCase):
    @patch("os.getenv")
    @patch("requests.get")
    def test_get_currency_rate(self, mock_get, mock_getenv):
        """Проверяет получение стоимости валют"""
        mock_getenv.return_value = "mock_api_key"
        mock_response_usd = MagicMock()

        mock_response_usd.json.return_value = {
            "success": True,
            "query": {"from": "USD", "to": "RUB", "amount": 1},
            "info": {"timestamp": 1736632635, "rate": 101.640033},
            "date": "2025-01-11",
            "result": 101.640033,
        }

        mock_response_usd.status_code = 200

        mock_response_eur = MagicMock()

        mock_response_eur.json.return_value = {
            "success": True,
            "query": {"from": "EUR", "to": "RUB", "amount": 1},
            "info": {"timestamp": 1736632635, "rate": 104.230108},
            "date": "2025-01-11",
            "result": 104.230108,
        }

        mock_response_eur.status_code = 200

        def side_effect(url, headers=None):
            if "from=USD" in url:
                return mock_response_usd
            elif "from=EUR" in url:
                return mock_response_eur
            return None

        mock_get.side_effect = side_effect

        with patch("builtins.open", mock_open(read_data=json.dumps({"user_currencies": ["USD", "EUR"]}))):
            result = get_currency_rate()

        assert result == [{"currency": "USD", "rate": 101.64}, {"currency": "EUR", "rate": 104.23}]


class TestGetCurrencyRate2(unittest.TestCase):
    @patch("os.getenv")
    @patch("requests.get")
    def test_get_currency_rate_bad_status_code(self, mock_get, mock_getenv):
        """Проверяет поведение функции при неуспешном запросе на сервер"""
        mock_getenv.return_value = "mock_api_key"
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            get_currency_rate()
        self.assertEqual(str(context.exception), "Ошибка API: 401")


@patch("requests.get")
def test_get_currency_rate_no_apikey(mock_get):
    """Проверяет поведение функции при отсутствии API-ключа"""

    os.environ["apikey"] = ""

    with pytest.raises(ValueError, match="API ключ не найден. Проверьте файл .env"):
        get_currency_rate()

    assert mock_get.call_count == 0


class TestGetStocksPrice(unittest.TestCase):
    @patch("os.getenv")
    @patch("requests.get")
    def test_get_stocks_price(self, mock_get, mock_getenv):
        """Проверяет успешное получение стоимости акций"""
        mock_getenv.return_value = "mock_api_key"

        mock_response_aapl = MagicMock()

        mock_response_aapl.json.return_value = {
            "ticker": "AAPL",
            "name": "Apple Inc.",
            "price": 236.85,
            "exchange": "NASDAQ",
            "updated": 1736542802,
            "currency": "USD",
        }
        mock_response_aapl.status_code = 200

        mock_response_amzn = MagicMock()

        mock_response_amzn.json.return_value = {
            "ticker": "AMZN",
            "name": "Amazon.com, Inc.",
            "price": 218.94,
            "exchange": "NASDAQ",
            "updated": 1736542802,
            "currency": "USD",
        }

        mock_response_amzn.status_code = 200

        mock_response_googl = MagicMock()

        mock_response_googl.json.return_value = {
            "ticker": "GOOGL",
            "name": "Alphabet Inc.",
            "price": 192.04,
            "exchange": "NASDAQ",
            "updated": 1736542802,
            "currency": "USD",
        }

        mock_response_googl.status_code = 200

        mock_response_msft = MagicMock()

        mock_response_msft.json.return_value = {
            "ticker": "MSFT",
            "name": "Microsoft Corporation",
            "price": 418.95,
            "exchange": "NASDAQ",
            "updated": 1736542801,
            "currency": "USD",
        }

        mock_response_msft.status_code = 200

        mock_response_tsla = MagicMock()

        mock_response_tsla.json.return_value = {
            "ticker": "TSLA",
            "name": "Tesla, Inc.",
            "price": 394.74,
            "exchange": "NASDAQ",
            "updated": 1736542801,
            "currency": "USD",
        }

        mock_response_tsla.status_code = 200

        def side_effect(url, headers=None):
            if "ticker=AAPL" in url:
                return mock_response_aapl
            elif "ticker=AMZN" in url:
                return mock_response_amzn
            elif "ticker=GOOGL" in url:
                return mock_response_googl
            elif "ticker=MSFT" in url:
                return mock_response_msft
            elif "ticker=TSLA" in url:
                return mock_response_tsla
            return None

        mock_get.side_effect = side_effect

        with patch(
            "builtins.open",
            mock_open(read_data=json.dumps({"user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]})),
        ):
            result = get_stocks_price()

        assert result == [
            {"stock": "AAPL", "price": 236.85},
            {"stock": "AMZN", "price": 218.94},
            {"stock": "GOOGL", "price": 192.04},
            {"stock": "MSFT", "price": 418.95},
            {"stock": "TSLA", "price": 394.74},
        ]


class TestGetStocksPrice2(unittest.TestCase):
    @patch("os.getenv")
    @patch("requests.get")
    def test_get_stocks_price_bad_status_code(self, mock_get, mock_getenv):
        """Проверяет поведение функции при неуспешном запросе на сервер"""
        mock_getenv.return_value = "mock_api_key"
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError) as context:
            get_stocks_price()
        self.assertEqual(str(context.exception), "Ошибка API: 401")


@patch("requests.get")
def test_get_stocks_price_no_apikey(mock_get):
    """Проверяет поведение функции при отсутствии API-ключа"""

    os.environ["ninjas_apikey"] = ""

    with pytest.raises(ValueError, match="API ключ не найден. Проверьте файл .env"):
        get_stocks_price()

    assert mock_get.call_count == 0
