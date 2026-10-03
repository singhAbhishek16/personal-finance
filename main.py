import sqlite3
import pandas as pd


def initialize_database():
    """Initialize SQLite database and create category mapping table"""
    with sqlite3.connect('finance.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS category_mapping 
                      (transaction_to_account TEXT PRIMARY KEY, 
                       category TEXT)''')  # [6]


def get_category_mapping(transaction):
    """Retrieve or create category mapping for transaction"""
    with sqlite3.connect('finance.db') as conn:
        cursor = conn.cursor()

        # Check existing mapping
        cursor.execute('''SELECT category FROM category_mapping 
                        WHERE transaction_to_account = ?''', (transaction,))  # [7]
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            # Get user input for new category
            category = input(f'Enter category for new transaction account "{transaction}": ')  # [3]
            cursor.execute('''INSERT INTO category_mapping (transaction_to_account, category) 
                            VALUES (?, ?)''', (transaction, category))  # [4]
            conn.commit()
            return category


def process_statement(csv_path):
    """Process bank statement CSV and generate categorized report"""
    # Read CSV file
    df = pd.read_csv(csv_path)  # [1]

    # Add category column
    df['Category'] = df['Transaction_To_Account'].apply(get_category_mapping)  # [5]

    # Generate final report
    report = df[['Amount', 'Category']]
    print("\nExpense Report:")
    print(report.to_string(index=False))


if __name__ == "__main__":
    initialize_database()
    csv_file = input("Enter path to bank statement CSV: ")  # [3]
    process_statement(csv_file)
