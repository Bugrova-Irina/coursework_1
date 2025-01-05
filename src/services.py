import json
import logging
import os
from datetime import datetime, timedelta

import pandas as pd

from get_from_csv_xlsx import get_transactions_xlsx

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

log_file_path = os.path.join(log_dir, "services.log")
file_handler = logging.FileHandler(log_file_path, "w", encoding="utf-8")

file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_categories_of_profitable_cashback(data, year, month):
    """Выводит список категорий выгодного кэшбэка за указанный месяц"""

    transactions_list = []

    try:
        # задаем дату начала и конца месяца
        start_date = datetime.strptime(f"01.{month}.{year}", "%d.%m.%Y")
        end_date = datetime.strptime(f"01.{month}.{year}", "%d.%m.%Y")
        end_date = end_date.replace(day=28) + timedelta(days=4)  # переходим к следующему месяцу
        end_date = end_date - timedelta(days=end_date.day)  # получаем последний день текущего месяца

        for transaction in data:
            date_operation = transaction.get("Дата операции")

            # Проверяем наличие нужных для вывода значений в словарях
            if not isinstance(transaction, dict):
                logger.warning("Нет данных для вывода")
                continue

            if date_operation and (isinstance(date_operation, str)):
                try:
                    # Преобразуем строку даты операции в datetime
                    transaction_date = datetime.strptime(date_operation, "%d.%m.%Y %H:%M:%S")

                    # Сравниваем даты с началом и концом месяца
                    if start_date <= transaction_date <= end_date:
                        transactions_list.append(transaction)

                except ValueError as ex:
                    logger.warning(f"Ошибка преобразования даты: {ex}")
                    continue

        if transactions_list:
            try:
                df = pd.DataFrame(transactions_list)
                df_ok = df.loc[(df["Статус"] == "OK")]

                # Группируем данные по категории
                cashback_sum = df_ok.groupby("Категория")["Бонусы (включая кэшбэк)"].sum().reset_index()

                # Сортируем данные по величине кэшбэка в порядке убывания
                sorted_cashback_sum = cashback_sum.sort_values(by="Бонусы (включая кэшбэк)", ascending=False)

                # Получаем топ-3 категории
                top_categories = sorted_cashback_sum.head(3)

                result_dict = {
                    row["Категория"]: row["Бонусы (включая кэшбэк)"] for _, row in top_categories.iterrows()
                }

                json_data = json.dumps(result_dict, indent=4, ensure_ascii=False)

                return json_data

            except Exception as ex:
                logger.error(f"Произошла ошибка: {ex}")
                return None

        else:
            logger.error("Список транзакций пуст.")
            return None

    except Exception as ex:
        logger.error(f"Произошла ошибка: {ex}")
        print(f"Произошла ошибка: {ex}")


if __name__ == "__main__":
    transactions = get_transactions_xlsx("../coursework_1/data/operations.xlsx")
    print(get_categories_of_profitable_cashback(transactions, "2021", "11"))
