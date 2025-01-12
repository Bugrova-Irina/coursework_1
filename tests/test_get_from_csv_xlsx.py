from io import BytesIO, StringIO
from unittest.mock import patch

import pandas as pd
import pytest

from src.get_from_csv_xlsx import get_transactions_csv, get_transactions_xlsx


@pytest.fixture
def mock_data():
    csv_data = """
    id;state;date;amount;currency_name;currency_code;from;to;description
650703;EXECUTED;2023-09-05T11:30:32Z;16210;Sol;PEN;Счет 58803664561298323391;Счет 39745660563456619397;Перевод организации
3598919;EXECUTED;2020-12-06T23:00:58Z;29740;Peso;COP;Discover 3172601889670065;Discover 0720428384694643;Перевод с карты на карту
    """
    f = StringIO(csv_data)
    return pd.read_csv(f, delimiter=";")


@patch("pandas.read_csv")
def test_get_transactions_csv(mock_pd_read_csv, mock_data):
    """Тестирует возврат списка транзакций из csv-файла"""

    mock_pd_read_csv.return_value = mock_data
    result = get_transactions_csv("transactions.csv")
    expected_result = mock_data.to_dict(orient="records")
    assert result == expected_result


@pytest.fixture
def mock_bad_data():
    return pd.DataFrame(
        columns=[
            "id",
            "state",
            "date",
            "amount",
            "currency_name",
            "currency_code",
            "from",
            "to",
            "description",
        ]
    )


@patch("pandas.read_csv")
def test_get_bad_transactions_csv(mock_pd_read_csv, mock_bad_data):
    """Тестирует обработку неправильного csv-файла"""
    mock_pd_read_csv.return_value = mock_bad_data
    result = get_transactions_csv("transactions.csv")
    expected_result = mock_bad_data.to_dict(orient="records")
    assert result == expected_result


@pytest.fixture
def mock_data_xlsx():
    data = {
        "id": [650703, 3598919],
        "state": ["EXECUTED", "EXECUTED"],
        "date": ["2023-09-05T11:30:32Z", "2020-12-06T23:00:58Z"],
        "amount": [16210, 29740],
        "currency_name": ["Sol", "Peso"],
        "currency_code": ["PEN", "COP"],
        "from": ["Счет 58803664561298323391", "Discover 3172601889670065"],
        "to": ["Счет 39745660563456619397", "Discover 0720428384694643"],
        "description": ["Перевод организации", "Перевод с карты на карту"],
    }
    df = pd.DataFrame(data)

    with BytesIO() as b:
        with pd.ExcelWriter(b, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")
        b.seek(0)
        return b


@patch("pandas.read_excel")
def test_get_transactions_xlsx(mock_pd_read_excel, mock_data_xlsx):
    """Тестирует возврат списка транзакций из xlsx-файла"""

    mock_pd_read_excel.return_value = pd.read_excel(mock_data_xlsx)
    result = get_transactions_xlsx("transactions_excel.xlsx")
    expected_result = mock_pd_read_excel.return_value.to_dict(orient="records")
    assert result == expected_result


@pytest.fixture
def mock_bad_xls():
    return pd.DataFrame(
        columns=[
            "id",
            "state",
            "date",
            "amount",
            "currency_name",
            "currency_code",
            "from",
            "to",
            "description",
        ]
    )


@patch("pandas.read_excel")
def test_get_bad_transactions_xlsx(mock_pd_read_excel, mock_bad_xls):
    """Тестирует обработку неправильного xlsx-файла"""
    mock_pd_read_excel.return_value = mock_bad_xls
    result = get_transactions_xlsx("transactions_excel.xlsx")
    expected_result = mock_bad_xls.to_dict(orient="records")
    assert result == expected_result


def test_error_csv():
    """тестирует ошибку обработки csv-файла"""
    result = get_transactions_csv("transactions1.csv")
    assert result == "Произошла ошибка [Errno 2] No such file or directory: 'transactions1.csv'"


def test_error_xlsx():
    """тестирует ошибку обработки xlsx-файла"""
    result = get_transactions_xlsx("transactions_excel1.xlsx")
    assert result == "Произошла ошибка [Errno 2] No such file or directory: 'transactions_excel1.xlsx'"
