import streamlit as st
import pandas as pd
import sqlite3

# DB

conn = sqlite3.connect('data/world.sqlite')
c = conn.cursor()

cursor = conn.cursor()

# Get a list of table names in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
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

def main():
    st.title("SQL Playground")
    menu = ["Home", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("HomePage")

        col1, col2 = st.columns(2)

        with col1:
            with st.form(key='query_form'):
                raw_code = st.text_area("SQL Code Here")
                submit_code = st.form_submit_button("Execute")

            # Table of Info

            with st.expander("Table Info"):
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

                    with st.expander("Results"):
                        query_df = pd.DataFrame(query_results)
                        st.dataframe(query_df)




    else:
        st.subheader("About")

if __name__ == '__main__':
    main()