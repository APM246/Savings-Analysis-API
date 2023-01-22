import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def analyse(files: list[InMemoryUploadedFile], bank_types: list[str], hidden: bool) -> BytesIO:
    MIN_DATE = None
    MAX_DATE = None
    transactions = None
    data_frames: list[pd.DataFrame] = []
    for i in range(len(files)):
        if bank_types[i] == "bankwest":
            transactions = pd.read_csv(files[i], parse_dates=[2], infer_datetime_format=True, dayfirst=True)
        elif bank_types[i] == "commbank":
            column_names = ["Transaction Date", "Change", "Description", "Balance"]
            transactions = pd.read_csv(files[i], names=column_names, parse_dates=[0], infer_datetime_format=True, dayfirst=True)

        data_frames.append(transactions)
        start_date = transactions["Transaction Date"].min()
        end_date = transactions["Transaction Date"].max()

        if i == 0:
            MIN_DATE = start_date
            MAX_DATE = end_date
        else:
            if start_date < MIN_DATE:
                MIN_DATE = start_date
            if end_date > MAX_DATE:
                MAX_DATE = end_date
    
    new_index = pd.date_range(start=MIN_DATE, end=MAX_DATE)
    processed_transactions: list[pd.DataFrame] = []
    for i in range(len(files)):
        if bank_types[i] == "bankwest":
            transactions = process_bankwest(data_frames[i], new_index)
            processed_transactions.append(transactions)
        elif bank_types[i] == "commbank":
            transactions = process_commbank(data_frames[i], new_index)
            processed_transactions.append(transactions)

    daily_balance = pd.concat(processed_transactions, ignore_index=True)
    daily_balance = daily_balance.groupby('Transaction Date').sum().reset_index()

    plt.figure(figsize=(10,10))
    plt.xlabel('Date')
    plt.ylabel('Balance')

    end_date_offset = MAX_DATE + pd.DateOffset(5)
    dates = pd.date_range(start=MIN_DATE, end=end_date_offset, freq='2W')
    plt.xticks(dates, dates.strftime("%B %d"), rotation=35)
    highest_balance = daily_balance['Balance'].max()
    if hidden:
        plt.yticks([])
    else:
        plt.yticks(range(0, int(highest_balance), 2500))

    plt.title("Savings over time since {0}".format(pd.to_datetime(MIN_DATE).strftime("%B %d")))
    plt.plot(daily_balance['Transaction Date'], daily_balance['Balance'])
    plt.axhline(highest_balance, color='red', alpha=0.2)
    
    file_object = BytesIO()
    plt.savefig(file_object, format="png")
    file_object = file_object.getbuffer()

    return file_object


def process_bankwest(transaction_history: pd.DataFrame, new_index):
    processed_accounts = []
    account_numbers = set(transaction_history["Account Number"])

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
    return bankwest_processed_transactions

def process_commbank(commbank_transactions: pd.DataFrame, new_index):
        # Latest value for each date
        commbank_transactions = commbank_transactions.groupby('Transaction Date').first()

        # Filling missing dates
        commbank_transactions = commbank_transactions.reindex(new_index, method="ffill", fill_value=0).reset_index().rename(columns={'index': 'Transaction Date'})

        # problem below: it appears as if on 26th income was earnt but actually just balance of netbank saver not considered before first transaction.
        # data insufficient and needs manual intervention

        commbank_processed_transactions = commbank_transactions.groupby('Transaction Date').sum().reset_index()
        return commbank_processed_transactions