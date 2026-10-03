import sqlite3
import pandas
import streamlit as st

# line 6 to 16 - is to create table. run only very first time
# connection = sqlite3.connect('shop_category_mapping.db')
# with sqlite3.connect('shop_category_mapping.db') as connection:
#     cursor = connection.cursor()
#     create_table_query = '''
#         CREATE TABLE IF NOT EXISTS table_category (
#             shop TEXT PRIMARY KEY,
#             category TEXT
#         );
#         '''
#     cursor.execute(create_table_query)
#     connection.commit() # commit kab karne ki zaroorat hai?

# take input from user
uploaded_file = st.file_uploader("Choose a file")
col_description = ""
if uploaded_file is not None:
    data = pandas.read_csv(uploaded_file)
    col_description = data["Description"]

count_credit_transactions = 0
existing_rows = 0

#create connection with db
with sqlite3.connect('shop_category_mapping.db') as connection:
    cursor = connection.cursor()

# line 30 to 52 is for creating db.
for number in range(len(col_description)):
    each_row = col_description[number]
    if each_row.startswith("BY") or each_row.startswith("CREDIT"):
        count_credit_transactions += 1
        continue
    parts = each_row.split('/')
    shop = parts[3].strip().lower()
    comment = parts[-1].lower()

    # check if shop details already exists in db
    cursor.execute("SELECT 1 FROM table_category WHERE shop = ? LIMIT 1", (shop,))
    shop_exists = cursor.fetchone()
    if shop_exists:
        print(f"shop: {shop} exists in db")
        existing_rows += 1
    else:
        print(f'shop exists. temporary print')
        # user_input_category = screen.textinput(title=f"user input", prompt=f'shop {shop} is tagged with {comment}')
        # print(f'shop {shop} is tagged with {comment}. user says to mark this: {user_input_category}')
        # insert_query = "INSERT INTO table_category VALUES (?, ?)"
        # cursor.execute(insert_query, (shop, user_input_category))
        # connection.commit()
        # print(f"Inserted ({shop}, {user_input_category}) into table_category.")

print(f'number of credits: {count_credit_transactions}')
print(f'number of already existing records: {existing_rows}')

# 58 - 60: to print list of categories in table
cursor.execute("SELECT DISTINCT category FROM table_category")
categories = [row[0] for row in cursor.fetchall()] # gives categories : []
print(f'categories: {categories}')

# Create a dictionary to hold <category_value>_debit variables, all set to 0
category_debits = {}
for cat in categories:
    # Replace spaces and special characters with underscores for valid variable names
    var_name = f"{cat.strip().replace(' ', '_').replace('-', '_')}_debit"
    category_debits[var_name] = 0

# category ke according amount calculation. eg: how much grocery spend in nov
# category_type = "party"
# total_debit = 0
col_debit = data["Debit"]
category_to_update_csv = []
for number in range(len(col_description)):
    each_row = col_description[number]
    if each_row.startswith("BY") or each_row.startswith("CREDIT"):
        count_credit_transactions += 1
        category_to_update_csv.append('credit')
        continue
    parts = each_row.split('/')
    shop = parts[3].strip().lower()

    # check if shop details already exists in db
    cursor.execute("SELECT 1 FROM table_category WHERE shop = ? LIMIT 1", (shop,))
    shop_exists = cursor.fetchone()
    if shop_exists:
        # fetch its category
        cursor.execute("SELECT category FROM table_category WHERE shop = ?", (shop,))
        shop_s_category = cursor.fetchone()
        # jis category ka mile uska debit variable add ho
        debit_amount = col_debit[number]
        debit_amount_float = float(debit_amount.replace(',', ''))
        found_category = shop_s_category[0]
        category_to_update_csv.append(found_category)
        print(f'found_category: {found_category}')
        amount_goes_to = f"{found_category.strip().replace(' ', '_').replace('-', '_')}_debit"
        category_debits[amount_goes_to] += debit_amount_float

print(f'category_variables: {category_debits}')
total_dec_expense = 0
for value in category_debits.values():
    total_dec_expense += value

data['expense_category'] = category_to_update_csv
data.to_csv("test-sheet-jan'24.csv", index=False)

print(f'total_nov_expense: {total_dec_expense}')
# prints total_nov_expense: 54357.759999999995 and is right

