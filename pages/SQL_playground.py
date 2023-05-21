import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image
import re

st.set_page_config(layout="wide")
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# DB

conn = sqlite3.connect('data/case2.db')

cursor = conn.cursor()
cursor.execute("PRAGMA query_only = 1")

# Get a list of table names in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
table_names = [row[0] for row in cursor.fetchall()]

# Create an empty dictionary to store the column names for each table
column_names_dict = {}

# Loop through each table and get its column names
for table_name in table_names:
    cursor.execute(f"PRAGMA table_info({table_name})")
    column_names = [row[1] for row in cursor.fetchall()]
    column_names_dict[table_name] = column_names

def sql_executor(raw_code):
	cursor.execute(raw_code)
	data = cursor.fetchall()
	return data

def is_valid_query(user_query):
    # Define the list of keywords to filter
    keywords_to_filter = ['DROP', 'ALTER', 'CREATE', 'UPDATE', 'DELETE', 'EXECUTE', 'EXEC']

    # Convert user query to uppercase for case-insensitive matching
    user_query = user_query.upper()

    # Use regular expressions to check for the presence of keywords
    pattern = r'\b(?:{})\b'.format('|'.join(map(re.escape, keywords_to_filter)))
    match = re.search(pattern, user_query)

    if match:
        return False  # Invalid query containing filtered keywords
    else:
        return True  # Valid query


st.subheader("SQL Playground")

col1, col2 = st.columns([1,2])

with col1:
    with st.form(key='query_form'):
        raw_code = st.text_area("SQL Code Here", value= 'select * from jobs')
        submit_code = st.form_submit_button("Execute")
        if is_valid_query(raw_code) == False:
            st.warning('Query contains forbidden keywords and is not allowed. Do not try to modify the database', icon="⚠️")
        else:

            # Table of Info

            with st.expander("Tables Info", expanded=True):
                table_info = column_names_dict

                # table_info = {'city': city, 'country': country, 'countrylanguage': countrylanguage}
                st.json(table_info)

            # Results Layouts
            with col2:
                if submit_code:
                    st.info("Query Submitted")
                    st.code(raw_code)

                    # Results
                    query_results = sql_executor(raw_code)
                    # with st.expander("Results"):
                    #     st.write(query_results)

                    with st.expander("Results", expanded=True):
                        query_df = pd.DataFrame(query_results, columns=[description[0] for description in cursor.description])
                        st.dataframe(query_df)