
import streamlit as st
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth

API_URL = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="Employee Management System",
    page_icon="👥",
    layout="wide"
)

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.title("👥 Employee Management System")
st.caption("Secure Employee Portal | Flask API + Streamlit")

# Login screen
if not st.session_state.logged_in:

    st.subheader("Login to your account")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login", use_container_width=True)

    if login_button:

        try:
            response = requests.get(
                f"{API_URL}/employees",
                auth=HTTPBasicAuth(username, password),
                timeout=5
            )

            if response.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.password = password
                st.session_state.role = (
                    "admin" if username == "admin" else "employee"
                )
                st.rerun()

            elif response.status_code == 401:
                st.error("Invalid username or password.")

            else:
                st.error("Login failed.")

        except requests.exceptions.RequestException:
            st.error("Cannot connect to Flask API. Start app.py first.")

else:

    username = st.session_state.username
    password = st.session_state.password
    role = st.session_state.role

    auth = HTTPBasicAuth(username, password)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.success(f"Welcome, {username.title()}!")
        st.write(f"Your role: **{role.title()}**")

    with col2:
        if st.button("Logout"):
            for key in ["logged_in", "username", "password", "role"]:
                st.session_state.pop(key, None)
            st.rerun()

    st.divider()

    # Fetch employees
    try:
        response = requests.get(
            f"{API_URL}/employees",
            auth=auth,
            timeout=5
        )

        if response.status_code == 200:
            employee_data = response.json()

            st.subheader("Employee Records")

            if employee_data:
                df = pd.DataFrame(employee_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No employee records found.")

            st.metric("Total Employees", len(employee_data))

        else:
            st.error("Could not load employee records.")

    except requests.exceptions.RequestException:
        st.error("Flask API is not running.")
        st.stop()

    # Admin controls
    if role == "admin":

        st.divider()
        st.subheader("Admin Management Panel")

        tab1, tab2, tab3 = st.tabs([
            "Add Employee",
            "Update Employee",
            "Delete Employee"
        ])

        with tab1:
            with st.form("add_form"):
                name = st.text_input("Employee Name")
                department = st.text_input("Department")
                add_button = st.form_submit_button("Add Employee")

            if add_button:
                result = requests.post(
                    f"{API_URL}/employees",
                    auth=auth,
                    json={"name": name, "department": department},
                    timeout=5
                )

                if result.status_code == 201:
                    st.success("Employee added successfully!")
                    st.rerun()
                else:
                    st.error(result.json().get("error", "Add failed"))

        with tab2:
            if employee_data:
                ids = [e["id"] for e in employee_data]
                selected_id = st.selectbox("Select Employee ID", ids)

                selected = next(
                    e for e in employee_data if e["id"] == selected_id
                )

                with st.form("update_form"):
                    new_name = st.text_input(
                        "New Name", value=selected["name"]
                    )
                    new_department = st.text_input(
                        "New Department", value=selected["department"]
                    )
                    update_button = st.form_submit_button("Update Employee")

                if update_button:
                    result = requests.put(
                        f"{API_URL}/employees/{selected_id}",
                        auth=auth,
                        json={
                            "name": new_name,
                            "department": new_department
                        },
                        timeout=5
                    )

                    if result.status_code == 200:
                        st.success("Employee updated successfully!")
                        st.rerun()
                    else:
                        st.error(result.json().get("error", "Update failed"))

        with tab3:
            if employee_data:
                delete_id = st.selectbox(
                    "Select Employee to Delete",
                    [e["id"] for e in employee_data],
                    key="delete_id"
                )

                if st.button("Delete Employee", type="primary"):
                    result = requests.delete(
                        f"{API_URL}/employees/{delete_id}",
                        auth=auth,
                        timeout=5
                    )

                    if result.status_code == 200:
                        st.success("Employee deleted successfully!")
                        st.rerun()
                    else:
                        st.error(result.json().get("error", "Delete failed"))

    else:
        st.info("Employee account: You have view-only access.")
