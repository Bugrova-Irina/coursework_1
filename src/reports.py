import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

log_file_path = os.path.join(log_dir, "reports.log")
file_handler = logging.FileHandler(log_file_path, "w", encoding="utf-8")

file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_transactions_from_xlsx():
    """Считывание финансовых операций из xlsx-файла"""
    try:
        transactions = pd.read_excel("../coursework_1/data/operations.xlsx")
        transactions = transactions.dropna(how="all")
        return transactions
    except Exception as ex:
        return f"Произошла ошибка {ex}"


def get_spending_by_categories(
    transactions: pd.DataFrame, category: str, end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории
    за последние три месяца (от переданной даты)
    """

    try:
        # если не задана конечная дата, принимаем ее равной текущей дате
        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, "%d.%m.%Y %H:%M:%S")

        # начальная дата периода = "минус 3 месяца" от конечной
        start_date = end_date - timedelta(days=90)

        # преобразуем дату операции из списка транзакций в datetime
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

        # фильтруем транзакции
        filtered_transactions = transactions[
            (transactions["Статус"] == "OK")
            & (transactions["Сумма операции"] < 0)
            & (transactions["Категория"] == category)
            & (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= end_date)
        ]

        # проверка на пустой датафрейм
        if filtered_transactions.empty:
            return pd.DataFrame(columns=transactions.columns)

        # json_result = filtered_transactions.to_json(orient="records", indent=4, force_ascii=False)

        return filtered_transactions
        # return json_result

    except Exception as ex:
        logger.error(f"Произошла ошибка: {ex}")
        return f"Произошла ошибка: {ex}"


def get_json_file(func):
    """
    Записывает полученный ранее отчет в формате датафрейма
    в json-файл report.json
    """

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, pd.DataFrame):
            wrapper_result = result.to_json(orient="records", indent=4, force_ascii=False)
            os.makedirs(os.path.dirname("../coursework_1/reports/report.json"), exist_ok=True)
            with open("../coursework_1/reports/report.json", "w", encoding="utf-8") as file:
                file.write(wrapper_result)
            return result
        else:
            logger.error(f"Функция {func.__name__} вернула ошибку: {result}")
            raise ValueError(f"Функция {func.__name__} вернула ошибку: {result}")

    return wrapper


def get_name_json_file(file_name):
    """
    Записывает полученный ранее отчет в формате датафрейма
    в json-файл, имя которого задает пользователь
    """

    def my_decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if isinstance(result, pd.DataFrame):
                os.makedirs(os.path.dirname("../coursework_1/reports"), exist_ok=True)
                with open(os.path.join("../coursework_1/reports", file_name), "w", encoding="utf-8") as file:
                    json_result = result.to_json(file, orient="records", indent=4, force_ascii=False)

                return json_result
            else:
                logger.error(f"Функция {func.__name__} вернула ошибку: {result}")
                raise ValueError(f"Функция {func.__name__} вернула ошибку: {result}")

        return wrapper

    return my_decorator


@get_json_file
def generate_report(transactions: pd.DataFrame, category: str, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    выдает отчет в файл report.json
    """
    result_df = get_spending_by_categories(transactions, category, end_date)

    result_df.loc[:, "Дата операции"] = result_df["Дата операции"].dt.strftime("%d.%m.%Y %H:%M:%S")

    return result_df


@get_name_json_file("my_report.json")
def generate_my_report(transactions: pd.DataFrame, category: str, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    выдает отчет в файл my_report.json
    """
    result_df = get_spending_by_categories(transactions, category, end_date)

    result_df.loc[:, "Дата операции"] = result_df["Дата операции"].dt.strftime("%d.%m.%Y %H:%M:%S")

    return result_df


if __name__ == "__main__":
    # print(get_transactions_xlsx())
    # print(get_spending_by_categories(get_transactions_from_xlsx(), "Супермаркеты", "30.12.2021 19:06:39"))
    transactions_df = get_transactions_from_xlsx()

    report = generate_report(transactions_df, "Супермаркеты", "30.12.2021 19:06:39")
    print("Стандартный отчет записан в report.json")

    my_report = generate_my_report(transactions_df, "Супермаркеты", "30.12.2021 19:06:39")
    print("Отчет записан в выбранный пользователем файл my_report.json")
