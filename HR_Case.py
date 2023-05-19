import streamlit as st
import pandas as pd
import sqlite3
from PIL import Image

# app settings

st.set_page_config(layout="wide", page_title="HR Case SQL",)
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

def sql_executor(raw_code):
	cursor.execute(raw_code)
	data = cursor.fetchall()
	return data

def main():
    st.title("HR Case")




    st.subheader("Case")
    col1, col2 = st.columns([55, 45])
    with col1:
        st.text("Case description")
        st.write("""**Part 1:**
        Head of HR asked you to answer some of the questions for him while working with this data, provide answers in short form as if you are replying to the email. As a challenging task - try answering without looking into the big table, try building a query that would fetch you a result.

1. Who is the manager with the most employees, how many, and which team is it? 
2. Who is the manager with the highest average salary in his team excluding CEO and Management Team? What is the team and what’s the average salary?
3. In which city should we open the third office? Currently, we have 2 in two of the most popular cities where our employees are.""")
        st.write("""**Part 2:**
                             The second part of the request from Head of HR is the to help creating the wide table for HR analyst to build dashboards on. You don’t need to build any dashboards, but your SQL skills are needed to join necessary tables and produce the end result.
                              To help you with specifications HR team made a prototype table""")

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
                            l.region as State,
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

        query_results = sql_executor(raw_code)

        with st.expander("Final table preview", expanded=True):
            query_df = pd.DataFrame(query_results,
                                    columns=[description[0] for description in cursor.description])
            st.dataframe(query_df)




        with st.expander("Hint: How to approach this task?"):
            st.write("""
            1. Start by checking individual tables in the SQL playground. Explore ‘employees’, ‘department’, and other tables to learn the data. Use the ‘table info’ section to peak into columns of the tables in the database
            2. Look again at the final solution and mark the columns coming from the ‘employees’ table. Which columns are missing and should be taken from other tables? 
            3. Start solving columns you know clearly. Such as “select employees.employee_id” - this is the first column and you can consider it done. 
            4. Once you joined all the needed tables take a look at the columns which require some calculations such as Average Salary per Manager and Tenure in Years. Which columns can be used to make these? 
""")
            with st.expander("Table Info"):
                table_info = column_names_dict
                st.json(table_info)

    with col2:

        image = Image.open('hr_db.png')
        st.image(image)


if __name__ == '__main__':
    main()