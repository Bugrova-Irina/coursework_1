from unittest.mock import patch

import numpy as np
import pandas as pd
from numpy import nan

from src.reports import get_spending_by_categories, get_transactions_from_xlsx


@patch("pandas.read_excel")
def test_get_transactions_from_xlsx(mock_pd_read_excel, mock_transactions_for_period):
    """Тестирует получение транзакций из файла в формате DataFrame"""
    mock_pd_read_excel.return_value = pd.read_excel(mock_transactions_for_period)
    result = get_transactions_from_xlsx()
    # expected_result = mock_pd_read_excel.return_value.to_dict(orient="records")
    assert result == mock_pd_read_excel.return_value.dropna(how="all")


def test_get_spending_by_categories(mock_transactions_for_period):
    """
    Тестирует возврат трат по заданной категории
    за последние три месяца (от переданной даты)
    """

    transactions_df = pd.DataFrame(mock_transactions_for_period)
    result = get_spending_by_categories(transactions_df, "Супермаркеты", "03.06.2018 10:23:52")
    result_list = result.to_dict(orient="records")

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
    ]

    for index, item in enumerate(expected_result):
        if np.isnan(item["Кэшбэк"]):
            assert np.isnan(result_list[index]["Кэшбэк"])  # проверка на nan
        else:
            assert item["Кэшбэк"] == result_list[index]["Кэшбэк"]
