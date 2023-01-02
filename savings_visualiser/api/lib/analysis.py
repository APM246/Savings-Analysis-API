import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

def analyse(bankwest_file: InMemoryUploadedFile, commbank_file: InMemoryUploadedFile, hidden: bool) -> BytesIO:
    transaction_history = pd.read_csv(bankwest_file, parse_dates=[2], infer_datetime_format=True, dayfirst=True)
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

    if commbank_file:
        # Process Commbank transactions
        column_names = ["Transaction Date", "Change", "Description", "Balance"]
        smart_access = pd.read_csv("smart_access.csv", names=column_names, parse_dates=[0], infer_datetime_format=True, dayfirst=True)
        netbank_saver = pd.read_csv("netbank_saver.csv", names=column_names, parse_dates=[0], infer_datetime_format=True, dayfirst=True)

        # Latest value for each date
        smart_access = smart_access.groupby('Transaction Date').first()
        netbank_saver = netbank_saver.groupby('Transaction Date').first()

        # Filling missing dates
        smart_access = smart_access.reindex(new_index, method="ffill", fill_value=0).reset_index().rename(columns={'index': 'Transaction Date'})
        netbank_saver = netbank_saver.reindex(new_index, method="ffill", fill_value=0).reset_index().rename(columns={'index': 'Transaction Date'})

        # problem below: it appears as if on 26th income was earnt but actually just balance of netbank saver not considered before first transaction.
        # data insufficient and needs manual intervention

        commbank_processed_transactions = pd.concat([smart_access, netbank_saver], ignore_index=True)
        commbank_processed_transactions = commbank_processed_transactions.groupby('Transaction Date').sum().reset_index()

    daily_balance = pd.concat([bankwest_processed_transactions], ignore_index=True)
    daily_balance = daily_balance.groupby('Transaction Date').sum().reset_index()
    daily_balance.tail()

    plt.figure(figsize=(10,10))
    plt.xlabel('Date')
    plt.ylabel('Balance')

    end_date_offset = END_DATE + pd.DateOffset(5)
    dates = pd.date_range(start=START_DATE, end=end_date_offset, freq='2W')
    plt.xticks(dates, dates.strftime("%B %d"   ), rotation=35)
    highest_balance = daily_balance['Balance'].max()
    if hidden:
        plt.yticks([])
    else:
        plt.yticks(range(0, int(highest_balance), 2500))

    plt.title("Savings over time since {0}".format(pd.to_datetime(START_DATE).strftime("%B %d")))
    plt.plot(daily_balance['Transaction Date'], daily_balance['Balance'])
    plt.axhline(highest_balance, color='red', alpha=0.2)
    
    file_object = BytesIO()
    plt.savefig(file_object, format="png")
    file_object = file_object.getbuffer()

    return file_object