import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Student Management System", page_icon="🎓")

st.title("🎓 Student Management System")
st.write("Manage university student records using Flask API and SQLite.")

# Fetch students from Flask API
try:
    response = requests.get(f"{API_URL}/students", timeout=5)
    response.raise_for_status()
    students = response.json()
except requests.RequestException:
    st.error("Cannot connect to Flask API. Please check that app.py is running.")
    st.stop()

# Display all students
st.subheader("📋 All Students")

if students:
    st.dataframe(pd.DataFrame(students), use_container_width=True)
else:
    st.info("No students found. Add your first student below.")

st.divider()

# Add a student
st.subheader("➕ Add New Student")

with st.form("add_student_form"):
    student_id = st.number_input("Student ID", min_value=1, step=1)
    name = st.text_input("Student Name")
    department = st.text_input("Department")
    email = st.text_input("Email Address")

    add_button = st.form_submit_button("Add Student")

    if add_button:
        if not name.strip() or not department.strip() or not email.strip():
            st.error("Please fill in all fields.")
        else:
            try:
                result = requests.post(
                    f"{API_URL}/students",
                    json={
                        "id": int(student_id),
                        "name": name.strip(),
                        "department": department.strip(),
                        "email": email.strip()
                    },
                    timeout=5
                )

                if result.status_code == 201:
                    st.success("Student added successfully!")
                    st.rerun()
                else:
                    st.error(result.json().get("error", "Unable to add student."))

            except requests.RequestException:
                st.error("Could not connect to the API.")

st.divider()

# Select an existing student
st.subheader("✏️ Update or Delete Student")

if students:
    selected = st.selectbox(
        "Select a student",
        students,
        format_func=lambda s: f'{s["id"]} - {s["name"]}'
    )

    # Update student
    with st.form("update_student_form"):
        updated_name = st.text_input("Name", value=selected["name"])
        updated_department = st.text_input(
            "Department", value=selected["department"]
        )
        updated_email = st.text_input("Email", value=selected["email"])

        update_button = st.form_submit_button("Update Student")

        if update_button:
            if not updated_name.strip() or not updated_department.strip() or not updated_email.strip():
                st.error("Please fill in all fields.")
            else:
                try:
                    result = requests.put(
                        f'{API_URL}/students/{selected["id"]}',
                        json={
                            "name": updated_name.strip(),
                            "department": updated_department.strip(),
                            "email": updated_email.strip()
                        },
                        timeout=5
                    )

                    if result.ok:
                        st.success("Student updated successfully!")
                        st.rerun()
                    else:
                        st.error(result.json().get("error", "Update failed."))

                except requests.RequestException:
                    st.error("Could not connect to the API.")

    # Delete student
    if st.button("🗑️ Delete Selected Student"):
        try:
            result = requests.delete(
                f'{API_URL}/students/{selected["id"]}',
                timeout=5
            )

            if result.ok:
                st.success("Student deleted successfully!")
                st.rerun()
            else:
                st.error(result.json().get("error", "Delete failed."))

        except requests.RequestException:
            st.error("Could not connect to the API.")
else:
    st.info("Add a student first to enable update and delete operations.")
