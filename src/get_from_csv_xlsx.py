from typing import Any

import pandas as pd


def get_transactions_csv(df: str) -> list[dict[str, Any]]:
    """Считывание финансовых операций из csv-файла"""
    try:
        transactions = pd.read_csv(df, delimiter=";")
        result = transactions.to_dict(orient="records")
        return result
    except Exception as ex:
        return f"Произошла ошибка {ex}"


def get_transactions_xlsx(df: str) -> list[dict[str, Any]]:
    """Считывание финансовых операций из xlsx-файла"""
    try:
        transactions = pd.read_excel(df)
        result = transactions.to_dict(orient="records")
        return result
    except Exception as ex:
        return f"Произошла ошибка {ex}"


if __name__ == "__main__":
    result = get_transactions_csv("../coursework_1/data/transactions.csv")
    # result2 = get_transactions_xlsx("../coursework_1/data/transactions_excel1.xlsx")
    print(result)
    # print(result2)
