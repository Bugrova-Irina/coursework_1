import json

from utils import get_greeting, get_number_of_card_amount_cashback, get_transactions_from_file, \
    get_top_5_of_transactions, get_currency_rate, get_stocks_price


def main(date):
    """Принимает на вход дату со временем и возвращает JSON-ответ"""

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


if __name__ == '__main__':
    print(main("06.06.2018 20:52:16"))
