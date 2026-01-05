import json
import requests
import sqlite3
import pandas
import streamlit as st
from datetime import datetime

BASE_URL = "https://budget.abhishekprojects.com/api/v1"
# API_TOKEN = st.secrets["api_token"]

# function to show security pop-up to user
def security_info():

    # nb: show_popup is added to st.session_state. new_tab/new_reload = new_session
    if "show_popup" not in st.session_state:
        st.session_state.show_popup = True

    @st.dialog("is this application secure?")
    def show_info_dialog():
        st.subheader(":exclamation: note around security:exclamation:")
        st.write("1. you are encouraged to remove account related informations from your bank statement. upload only transactions to analyse")
        st.write("2. connection between your browser and server is encrypted")
        st.write("3. your data stays only until you keep this tab open. no information from your statement gets stored on server")

    if st.session_state.show_popup:
        show_info_dialog()
        st.session_state.show_popup = False

# function to take input from user and return data and "Description" column
def user_statement():
    st.subheader("Ready to analyse you monthly expense?")
    uploaded_file = st.file_uploader("Choose your bank statement in csv format")
    data = None
    col_description = []
    if uploaded_file is not None:
        data = pandas.read_csv(uploaded_file)
        data.drop(columns=['Balance'], inplace=True)
        data.drop(columns=['Value Date'], inplace=True)
        data.drop(columns=['Ref No./Cheque No.'], inplace=True)
        col_description = data["Description"]

    return data,col_description

# function to take user's categories
def user_categories():
    my_category_list_test = []
    st.subheader("how would you like to categorise your expense?")
    user_input_categories = st.text_input("Enter categories (comma-separated) eg: grocery,rent,food..")
    if user_input_categories:
        my_category_list_test = [item.strip() for item in user_input_categories.split(',')]
    else:
        st.write(":warning: haven't received the category list yet")
    return my_category_list_test

# function to take user's tags
def user_tags():
    st.subheader("would you like to associate them with additional tags?")
    user_input_tags = st.text_input("eg: need, luxury, child-care..")
    my_tags_list_test = None
    if user_input_tags:
        my_tags_list_test = [item.strip() for item in user_input_tags.split(',')]
    else:
        st.write(":warning: haven't received tags list yet")
    return user_input_tags, my_tags_list_test

# function to create connection with database
def create_connection():
    with sqlite3.connect('shop_category_mapping.db') as connection:
        cursor = connection.cursor()
    return connection, cursor

# function to ask user to categorise his expense
def expense_category(cursor, col_description, my_tags_list_test):
    count_credit_transactions = 0
    existing_rows = 0

    # goes through each row and updates expense category in database
    for number in range(len(col_description)):
        each_row = col_description[number]
        if each_row.startswith("BY") or each_row.startswith("CREDIT") or each_row.startswith("by"):
            # TODO: count_credit_transactions ki zaroorat hai?
            count_credit_transactions += 1
            continue
        parts = each_row.split('/')
        shop = parts[3].strip().lower()
        comment = parts[-1].lower()

        # check if shop details already exists in db
        cursor.execute("SELECT * FROM table_category WHERE shop = ? LIMIT 1", (shop,))
        shop_exists = cursor.fetchone()
        if shop_exists:
            st.markdown(
                f"shop: :green-background[{shop}] exists in db under category :orange-background[{shop_exists[1]}] & tagged as :orange-background[{shop_exists[2]}]")
            existing_rows += 1
            continue

        st.write(f'shop: :red-background[{shop}] doesnt exist in db')
        with st.form(f'shop_{shop}_form'):
            user_input_category = st.selectbox(f'shop {shop} is tagged with {comment}', my_category_list_test)
            user_input_tag = st.selectbox('tags?', my_tags_list_test)
            submit = st.form_submit_button("Submit")

        # pause script execution until all expenses are categorised
        if not submit:
            st.stop()

        # If we reach here, form was submitted in this rerun by streamlit
        insert_query = "INSERT INTO table_category VALUES (?, ?, ?)"
        cursor.execute(insert_query, (shop, user_input_category, user_input_tag))
        connection.commit()
        print(f"Inserted ({shop}, {user_input_category}, {user_input_tag}) into table_category.")
        st.markdown("Submitted successfully! ✅")

        # Optional: after inserting, trigger a clean rerun so UI updates nicely
        st.rerun()

    return count_credit_transactions


# function to add all expenses for each category
def expense_per_category(cursor, count_credit_transactions):
    cursor.execute("SELECT DISTINCT category FROM table_category")
    categories = [row[0] for row in cursor.fetchall()]
    # Create a dictionary to hold <category_value>_debit variables, all set to 0
    category_debits = {}
    for cat in categories:
        # Replace spaces and special characters with underscores for valid variable names
        var_name = f"{cat.strip().replace(' ', '_').replace('-', '_')}_debit"
        category_debits[var_name] = 0

    # category ke according amount calculation. eg: how much grocery spend in nov
    # category_type = "party"
    # total_debit = 0
    if data is not None and not data.empty:
        col_debit = data.get("Debit")
    category_to_update_csv = []
    tags_to_update_csv = []
    for number in range(len(col_description)):
        each_row = col_description[number]
        if each_row.startswith("BY") or each_row.startswith("CREDIT") or each_row.startswith(
                "BULK") or each_row.startswith("by"):
            # self-note: BULK match needs to be added for one jan 31 transaction
            count_credit_transactions += 1
            category_to_update_csv.append('credit')
            tags_to_update_csv.append('credit')
            continue
        parts = each_row.split('/')
        shop = parts[3].strip().lower()

        # check if shop details already exists in db
        cursor.execute("SELECT 1 FROM table_category WHERE shop = ? LIMIT 1", (shop,))
        shop_exists = cursor.fetchone()
        if shop_exists:
            # fetch its category
            cursor.execute("SELECT category, tags FROM table_category WHERE shop = ?", (shop,))
            shop_s_category = cursor.fetchone()
            # jis category ka mile uska debit variable add ho
            debit_amount = col_debit[number]
            debit_amount_float = float(debit_amount.replace(',', ''))
            found_category = shop_s_category[0]
            found_tags = shop_s_category[1]
            category_to_update_csv.append(found_category)
            tags_to_update_csv.append(found_tags)
            amount_goes_to = f"{found_category.strip().replace(' ', '_').replace('-', '_')}_debit"
            category_debits[amount_goes_to] += debit_amount_float

    return category_debits, category_to_update_csv, tags_to_update_csv

# function to display expense per category graph
def graph_expense_per_category(category_debits):
    # show expense graph
    df = pandas.DataFrame(list(category_debits.items()), columns=['Category', 'Expense'])
    # Optional: Filter out categories with zero expense for cleaner chart
    df = df[df['Expense'] > 0]
    # Optional: Sort by expense amount
    df = df.sort_values(by='Expense', ascending=False)
    # Display bar chart
    st.subheader("gonna break your :broken_heart:..but it will get better in next 6 months")
    st.bar_chart(df.set_index('Category'))

# function to display updated csv
def updated_csv(data, category_to_update_csv, tags_to_update_csv):
    st.subheader("here's how your expenses were categorised & tagged. use :mag: to search and :arrow_down: to download")

    # create updated dataframe with categories
    data['tagged category'] = category_to_update_csv
    data['tags'] = tags_to_update_csv
    st.write(data)


security_info()
data, col_description = user_statement()
st.subheader("your raw bank statement looks like -")
st.write(data)
my_category_list_test = user_categories()
user_input_tags, my_tags_list_test = user_tags()
connection, cursor = create_connection()
# my_category_list is not used. have put for abhishek's expense category
my_category_list = ['scooty operation', 'personal shopping need', 'personal shopping luxury', 'outside food need', 'outside food luxury', 'luxurychai', 'grocery', 'blr electricity bill', 'pat electricity bill', 'medicine', 'festive expense', 'khet expense', 'subscription', 'urban company', 'rent', 'cook', 'trip', 'upi wallet', 'amazon', 'simpl', 'untrackable', 'phone bill', 'internet bill', 'travel', 'q commerce']
count_credit_transactions = expense_category(cursor, col_description, my_tags_list_test)
category_debits, category_to_update_csv, tags_to_update_csv = expense_per_category(cursor, count_credit_transactions)
graph_expense_per_category(category_debits)
updated_csv(data, category_to_update_csv, tags_to_update_csv)

try:
    # display raw input to user

    st.info(
        "**Note**:\n\n -> this application is designed to :blue-background[not] store any of your data. above analysis is performed only in memory,"
        " and does not go to permanent storage.\n\n"
        "-> if above chart fulfils your need, you can just close the tab & everything will be deleted.\n\n"
        "-> if you are looking for more, like how your groceries bill rose in last 6 months, or how much"
        " budget you have left for coming weekend party, send this data to next part of application (where we have"
        " support for advanced analytics)",
        icon="ℹ️"
    )

    if st.button('send to firefly-iii'):
        #####################################
        # we have dataframe in "data" variable. now, we need to create json object that will be sent to firefly api endpoint
        #####################################
        with st.spinner("sending data in-progress ...", show_time=True):
            temp_df = data
            temp_df.rename(columns={'Txn Date': 'date', 'Description': 'description', 'tagged category': 'category_name'},
                           inplace=True)

            withdrawal_df = temp_df[temp_df['Credit'].isna()]  # rows where credit is None/NaN
            withdrawal_df.drop(columns=['Credit'], inplace=True)
            withdrawal_df.rename(columns={'Debit': 'amount'}, inplace=True)

            deposit_df = temp_df[temp_df['Debit'].isna()]  # rows where debit is None/NaN
            deposit_df.drop(columns=['Debit'], inplace=True)
            deposit_df.rename(columns={'Credit': 'amount'}, inplace=True)

            ### send deposit data to firefly ###
            for index, row in deposit_df.iterrows():

                # goes row by row
                # make format that firefly will accept
                json_data = row.to_dict()
                json_payload = json.dumps(json_data) # contains date, description, amount, category_name, tags
                date_obj = datetime.strptime(json_data["date"], "%d %B %Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                transaction = {
                    "type": "deposit",
                    "date": formatted_date,
                    "amount": json_data["amount"].replace(",", ""),  # optional: clean amount formatting
                    "description": json_data["description"],
                    "destination_id": 1
                }
                deposit = {
                    "transactions": [transaction]
                }

                url = f"{BASE_URL}/transactions"
                headers = {
                    "Authorization": f"Bearer {API_TOKEN}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                response = requests.post(url, headers=headers, json=deposit)
                if response.status_code != 200 and response.status_code != 201:
                    st.write(
                        f"Failed to post row {index}. Status code: {response.status_code}, Response: {response.text}")

            ########## send withdrawl data to firefly ##########
            for index, row in withdrawal_df.iterrows():

                # goes row by row
                # make format that firefly will accept
                json_data = row.to_dict()
                json_payload = json.dumps(json_data) # contains date, description, amount, category_name, tags
                date_obj = datetime.strptime(json_data["date"], "%d %B %Y")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                transaction = {
                    "type": "withdrawal",
                    "date": formatted_date,
                    "amount": json_data["amount"].replace(",", ""),  # optional: clean amount formatting
                    "description": json_data["description"],
                    "source_id": 1,
                    "category_name": json_data["category_name"],
                    "tags": json_data["tags"]
                }
                deposit = {
                    "transactions": [transaction]
                }

                url = f"{BASE_URL}/transactions"
                headers = {
                    "Authorization": f"Bearer {API_TOKEN}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                response = requests.post(url, headers=headers, json=deposit)
                if response.status_code != 200 and response.status_code != 201:
                    st.write(f"Failed to post row {index}. Status code: {response.status_code}, Response: {response.text}")

        st.success("sent successfully. head over to ...!")
    ########

    st.write(
        "***best thing?*** i am gonna remember your expense categories for above shops. you won't need to tag them again next month :zap:")

except NameError:
    st.write("you have not yet uploaded your bank statement!")

except st.errors.StreamlitAPIException:
    st.write("submit category for above shops to proceed ahead!")

# we have dataframe in "data" variable. now, we need to create json object that will be sent to firefly api endpoint
# temp_df = data
# temp_df.rename(columns={'Txn Date': 'date', 'Description': 'description', 'tagged category': 'category_name'}, inplace=True)
#
# withdrawal_df = temp_df[temp_df['credit'].isna()]  # rows where credit is None/NaN
# deposit_df = temp_df[temp_df['debit'].isna()]       # rows where debit is None/NaN
