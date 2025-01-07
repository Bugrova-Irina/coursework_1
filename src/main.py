from get_from_csv_xlsx import get_transactions_xlsx
from reports import generate_my_report, generate_report, get_transactions_from_xlsx
from services import get_categories_of_profitable_cashback
from views import main


def get_all_results_from_widget():
    """Выдает результат работы всех функций виджета"""

    # Получаем JSON-ответ с приветствием, данными по картам,
    # топ-5 транзакций по сумме платежа, курс валют, стоимость акций
    main_json = main("06.06.2018 20:52:16")

    # получаем список транзакций из файла и выводим из него
    # JSON-ответ с категориями выгодного кэшбэка
    transactions = get_transactions_xlsx("../coursework_1/data/operations.xlsx")
    categories_of_profitable_cashback = get_categories_of_profitable_cashback(transactions, "2021", "11")

    # Генерируем отчеты с данными за 3 месяца и выводим их в JSON-файлы
    transactions_df = get_transactions_from_xlsx()

    report = generate_report(transactions_df, "Супермаркеты", "30.12.2021 19:06:39")
    result_of_generate_report = "Стандартный отчет записан в report.json"

    my_report = generate_my_report(transactions_df, "Супермаркеты", "30.12.2021 19:06:39")
    result_of_generate_my_report = "Отчет записан в выбранный пользователем файл my_report.json"

    print(
        """
    JSON-ответ с приветствием, данными по картам, 
    топ-5 транзакций по сумме платежа, курс валют, 
    стоимость акций\n
    """,
        main_json,
    )
    print(
        """
        JSON-ответ с категориями выгодного кэшбэка\n
        """,
        categories_of_profitable_cashback,
    )
    print(
        """
        Вывод отчета по тратам по заданной категории 
        за последние три месяца в файл report.json\n
        """,
        result_of_generate_report,
    )
    print(
        """
        Вывод отчета по тратам по заданной категории 
        за последние три месяца в файл my_report.json\n
        """,
        result_of_generate_my_report,
    )


if __name__ == "__main__":
    get_all_results_from_widget()
