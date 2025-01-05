import json
import logging
import os
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv

from get_from_csv_xlsx import get_transactions_xlsx

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

log_file_path = os.path.join(log_dir, "utils.log")
file_handler = logging.FileHandler(log_file_path, "w", encoding="utf-8")

file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_greeting(date):
    """
    Выдает приветствие пользователю в зависимости от времени
    в конечной дате временного периода
    """

    if not date:
        logging.error("Не задано время")
        raise Exception("Не задано время")

    try:
        # Получаем время для приветствия
        time_of_last_transaction = int(date[-8:-6])
        # print(time_of_last_transaction)

        if 0 <= time_of_last_transaction < 6:
            return "Доброй ночи"

        elif 6 <= time_of_last_transaction < 12:
            return "Доброе утро"

        elif 12 <= time_of_last_transaction < 18:
            return "Добрый день"

        else:
            return "Добрый вечер"
    except ValueError as ex:
        logging.error(f"Задана некорректная дата: {ex}")
        print(f"Задана некорректная дата: {ex}")


def get_transactions_from_file():
    """Получает список транзакций за выбранный период"""

    last_date = "06.06.2018 20:52:16"

    # Получаем начальную дату периода, в котором будут обрабатываться транзакции
    date_list = ["01.", "06.06.2018 20:52:16"[3:11], "00:00:00"]
    first_date = "".join(date_list)
    # print(date_of_first_transaction)

    transactions_list = []
    try:
        first_date = datetime.strptime(first_date, "%d.%m.%Y %H:%M:%S")
        last_date = datetime.strptime(last_date, "%d.%m.%Y %H:%M:%S")

        transactions = get_transactions_xlsx("../coursework_1/data/operations.xlsx")

        for transaction in transactions:
            date_operation = transaction.get("Дата операции")

            # Проверяем наличие нужных для вывода значений в словарях
            if not isinstance(transaction, dict):
                logger.warning("Нет данных для вывода")
                continue

            if date_operation and (isinstance(date_operation, str)):
                # Преобразуем строку даты операции в datetime
                date_operation = datetime.strptime(date_operation, "%d.%m.%Y %H:%M:%S")

                # Сравниваем даты
                if first_date <= date_operation <= last_date:
                    transactions_list.append(transaction)

        if transactions_list:
            return transactions_list

        else:
            logger.error("Список транзакций пуст.")
            return None

    except Exception as ex:
        logger.error(f"Произошла ошибка: {ex}")
        print(f"Произошла ошибка: {ex}")


def get_number_of_card_amount_cashback(transactions):
    """
    Выводит последние 4 цифры каждой карты из списка транзакций,
    сумму расходов и сумму кэшбэка по каждой карте
    """
    if not transactions:
        logger.error("Список транзакций пуст.")
        raise ValueError("Список транзакций пуст.")

    try:
        df = pd.DataFrame(transactions)
        df_ok = df.loc[(df["Статус"] == "OK") & (df["Сумма операции"] < 0)]

        # Группируем данные по номеру карты
        card_number_grouped = df_ok.groupby("Номер карты")
        # Суммируем расходы по каждой карте, преобразуем в положительное число
        card_amount_sum = abs(round(card_number_grouped["Сумма операции"].sum(), 2))
        # получаем кэшбэк
        cashback = round(card_amount_sum / 100, 2)

        results = []
        cards_dict_cashback = cashback.to_dict()

        for card, total in card_amount_sum.items():
            result_dict = {"last_digits": card, "total_spent": total, "cashback": cards_dict_cashback[card]}
            results.append(result_dict)

        return results

    except ValueError as ex:
        logging.error(f"Некорректные исходные данные: {ex}")
        print(f"Некорректные исходные данные: {ex}")


def get_top_5_of_transactions(transactions):
    """Выводит 5 транзакций с самой большой суммой платежа"""

    if not transactions:
        logger.error("Список транзакций пуст.")
        raise ValueError("Список транзакций пуст.")

    try:
        df = pd.DataFrame(transactions)
        df_ok = df.loc[(df["Статус"] == "OK") & (df["Сумма операции"] < 0)]

        # Получаем отсортированный по сумме платежа список транзакций
        sorted_df_ok = df_ok.sort_values(by="Сумма платежа")
        sorted_transactions = sorted_df_ok.to_dict(orient="records")

        result = dict()

        for index, item in enumerate(sorted_transactions):
            while index <= 4:
                result[f"{index + 1}"] = {
                    "date": item["Дата операции"],
                    "amount": item["Сумма платежа"],
                    "category": item["Категория"],
                    "description": item["Описание"],
                }
                break

        top_transactions = []
        for key in result.keys():
            top_transactions.append(result[key])

        return top_transactions

    except ValueError as ex:
        logging.error(f"Некорректные исходные данные: {ex}")
        print(f"Некорректные исходные данные: {ex}")


def get_currency_rate():
    """Получает курс валют"""
    with open("../coursework_1/user_settings.json", "r", encoding="utf-8") as json_file:
        currencies_data = json.load(json_file)
        currencies = currencies_data["user_currencies"]

    load_dotenv(".env")
    apikey = os.getenv("apikey")

    if not apikey:
        logger.error("API ключ не найден. Проверьте файл .env")
        raise ValueError("API ключ не найден. Проверьте файл .env")

    rates = {}
    result_rates = []

    for currency in currencies:
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency}&amount=1"

        headers = {"apikey": apikey, "Content-Type": "application/json"}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Ошибка API: {response.status_code}")
            raise ValueError(f"Ошибка API: {response.status_code}")

        # status_code = response.status_code
        # result = response.text
        #
        # print(response)
        # print(response.json())
        # print(result)
        # print(status_code)

        try:
            json_response = response.json()
            rate = json_response.get("result", 0)
            rates[currency] = round(rate, 2)

        except ValueError:
            logger.error("Ошибка при парсинге JSON ответа.")
            print("Ошибка при парсинге JSON ответа.")
            rates[currency] = 0.0

    for key, value in rates.items():
        rates_dict = {"currency": key, "rate": value}
        result_rates.append(rates_dict)

    return result_rates


def get_stocks_price():
    """Получает стоимость акций"""
    with open("../coursework_1/user_settings.json", "r", encoding="utf-8") as json_file:
        stocks_list = json.load(json_file)
        stocks = stocks_list["user_stocks"]
        # print(stocks)

    load_dotenv(".env")
    apikey = os.getenv("ninjas_apikey")
    # print(apikey)

    if not apikey:
        logger.error("API ключ не найден. Проверьте файл .env")
        raise ValueError("API ключ не найден. Проверьте файл .env")

    stocks_prices = {}
    stocks_prices_result = []

    for stock in stocks:
        # print(stock)
        url = "https://api.api-ninjas.com/v1/stockprice?ticker={}".format(stock)
        headers = {
            "X-Api-Key": apikey,
            # "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Ответ сервера: {response.text}")
            logger.error(f"Ошибка API: {response.status_code}")
            raise ValueError(f"Ошибка API: {response.status_code}")

        try:
            json_response = response.json()
            price = json_response.get("price", 0)
            stocks_prices[stock] = price
            # print(response.text)
        except ValueError:
            logger.error("Ошибка при парсинге JSON ответа")
            print("Ошибка при парсинге JSON ответа")
            stocks_prices[stock] = 0.0

    for key, value in stocks_prices.items():
        result_dict = {"stock": key, "price": value}
        stocks_prices_result.append(result_dict)

    return stocks_prices_result


if __name__ == "__main__":
    # print(get_date_from_transactions())
    # print(get_greeting())
    # print(get_transactions_from_file())
    print(get_number_of_card_amount_cashback(get_transactions_from_file()))
    # print(get_last_date_of_period())
    # print(get_top_5_of_transactions(get_transactions_from_file()))
    # print(get_currency_rate())
    # print(get_stocks_price())
