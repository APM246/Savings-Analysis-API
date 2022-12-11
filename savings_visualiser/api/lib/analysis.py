import pandas as pd
import matplotlib.pyplot as plt

def analyse(file):
    transaction_history = pd.read_csv(file, parse_dates=[2], infer_datetime_format=True, dayfirst=True)
    START_DATE = transaction_history["Transaction Date"].min()
    END_DATE = transaction_history["Transaction Date"].max()

    processed_accounts = []
    account_numbers = set(transaction_history["Account Number"])
    new_index = pd.date_range(start=START_DATE, end=END_DATE)

    for account_number in account_numbers:
        transactions = transaction_history[transaction_history["Account Number"] == account_number]
        
        # First value from top reflects the latest balance on that date
        transactions = transactions.groupby('Transaction Date').first()
        
        # need to use reindex to fill latest values up to current day
        # create full time range
        transactions = transactions.reindex(new_index, method="ffill", fill_value=0).reset_index().rename(columns={'index': 'Transaction Date'})
        processed_accounts.append(transactions)

    bankwest_processed_transactions = pd.concat(processed_accounts, ignore_index=True)
    bankwest_processed_transactions = bankwest_processed_transactions.groupby('Transaction Date').sum().reset_index()
    bankwest_processed_transactions.tail()

    daily_balance = pd.concat([bankwest_processed_transactions], ignore_index=True)
    daily_balance = daily_balance.groupby('Transaction Date').sum().reset_index()
    daily_balance.tail()

    plt.figure(figsize=(10,10))
    plt.xlabel('Date')
    plt.ylabel('Balance')

    end_date_offset = END_DATE + pd.DateOffset(5)
    dates = pd.date_range(start=START_DATE, end=end_date_offset, freq='2W')
    plt.xticks(dates, dates.strftime("%B %d"), rotation=35)

    highest_balance = daily_balance['Balance'].max()
    plt.yticks(range(0, int(highest_balance), 2500))
    plt.title("Savings over time since {0}".format(pd.to_datetime(START_DATE).strftime("%B %d")))

    plt.plot(daily_balance['Transaction Date'], daily_balance['Balance'])
    plt.axhline(highest_balance, color='red', alpha=0.2)
    plt.show()