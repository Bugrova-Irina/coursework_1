import json
import logging
import os

from utils import get_greeting, get_number_of_card_amount_cashback, get_transactions_from_file, \
    get_top_5_of_transactions, get_currency_rate, get_stocks_price

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

log_file_path = os.path.join(log_dir, "views.log")
file_handler = logging.FileHandler(log_file_path,"w", encoding="utf-8")

file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def main(date):
    """Принимает на вход дату со временем и возвращает JSON-ответ"""

    if not date:
        logging.error("Не задано время")
        raise Exception("Не задано время")

    try:
        greeting = get_greeting(date)
        cards = get_number_of_card_amount_cashback(get_transactions_from_file())
        top_transactions = get_top_5_of_transactions(get_transactions_from_file())
        currency_rates = get_currency_rate()
        stock_prices = get_stocks_price()

        data = {
                "greeting": greeting,
                "cards": cards,
                "top_transactions": top_transactions,
                "currency_rates": currency_rates,
                "stock_prices": stock_prices
            }

        json_data = json.dumps(data, indent=4, ensure_ascii=False)
        return json_data

    except Exception as ex:
        logger.error(f"Произошла ошибка: {ex}")
        return  None


if __name__ == '__main__':
    print(main("06.06.2018 20:52:16"))
