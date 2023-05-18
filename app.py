import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image

# DB

conn = sqlite3.connect('data/case2.db')
c = conn.cursor()

cursor = conn.cursor()

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

st.set_page_config(layout="wide")


def sql_executor(raw_code):
	cursor.execute(raw_code)
	data = cursor.fetchall()
	return data

def main():
    st.title("HR Case")
    menu = ["Case Description", "SQL Database", "Solution Preview"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "SQL Database":
        st.subheader("SQL Playground")

        col1, col2 = st.columns([1,2])

        with col1:
            with st.form(key='query_form'):
                raw_code = st.text_area("SQL Code Here", value= 'select * from jobs')
                submit_code = st.form_submit_button("Execute")

            # Table of Info

            with st.expander("Table Info", expanded=True):
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

    elif choice == "Case Description":
        st.subheader("Case")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.text("Case description")
            st.write("""Head of HR asked you to answer some of the questions for him while working with this data, provide answers in short form as if you are replying to the email. As a challenging task - try answering without looking into the big table, try building a query that would fetch you a result.

1. Who is the manager with the most employees, how many, and which team is it? 
2. Who is the manager with the highest average salary in his team excluding CEO and Management Team? What is the team and what’s the average salary?
3. In which city should we open the third office? Currently, we have 2 in two of the most popular cities where our employees are.""")

        with col2:

            image = Image.open('hr_db.png')
            st.image(image)

        st.write("additionally Link to preview page")




    else:
        st.subheader("Solution")

        col1, col2 = st.columns([1, 2])

        with col1:
            with st.form(key='query_form'):
                raw_code = '''select 
                    e.employee_id,
                    e.first_name || " " || e.last_name as Employee_Name,
                    e.salary,
                    ROUND(AVG(e.salary) OVER (PARTITION BY (m.first_name || " " || m.last_name)), 1) as AVG_Salary_by_mngr,
                    ROUND(AVG(e.salary) OVER (PARTITION BY d.department_name), 1) as AVG_Salary_by_dept,
                    m.first_name || " " || m.last_name as Manager_Name,
                    cast(strftime('%Y.%m%d', 'now') - strftime('%Y.%m%d', e.hire_date) as int) as Tenure_years, 
                    j.job_title,
                    d.department_name,
                    l.city,
                    c.country_name,
                    r.region_name 
                    
                    from employees e
                    inner join jobs j on e.job_id = j.job_id
                    inner join departments d on e.department_id = d.department_id
                    inner join locations l on e.location_id = l.location_id
                    inner join countries c on l.country_id = c.country_id
                    inner join regions r on c.region_id = r.region_id
                    left join employees m on e.manager_id = m.employee_id
                    LIMIT 3'''
                mock_code = st.text_area("SQL Code Here", value='''Enter your SQL here''')
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
                    st.code("Solution code hidden, preview results below")

                    # Results
                    query_results = sql_executor(raw_code)
                    # with st.expander("Results"):
                    #     st.write(query_results)

                    with st.expander("Results", expanded=True):
                        query_df = pd.DataFrame(query_results,
                                                columns=[description[0] for description in cursor.description])
                        st.dataframe(query_df)

if __name__ == '__main__':
    main()