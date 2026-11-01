
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# Demo employee records
employees = [
    {"id": 1, "name": "Ali", "department": "Computer Science"},
    {"id": 2, "name": "Ahmed", "department": "Information Technology"},
    {"id": 3, "name": "Abdul Basit", "department": "Software Engineering"}
]

# Demo users
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "employee": {"password": "emp123", "role": "employee"}
}


# Authentication and authorization
def authenticate(required_role=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            auth = request.authorization

            if not auth:
                return jsonify({"error": "Login required"}), 401

            user = users.get(auth.username)

            if not user or user["password"] != auth.password:
                return jsonify({"error": "Invalid username or password"}), 401

            if required_role and user["role"] != required_role:
                return jsonify({"error": "Admin access required"}), 403

            return func(*args, **kwargs)

        return wrapper
    return decorator


# GET: View all employees (Admin and Employee)
@app.route("/employees", methods=["GET"])
@authenticate()
def get_employees():
    return jsonify(employees), 200


# POST: Add employee (Admin only)
@app.route("/employees", methods=["POST"])
@authenticate("admin")
def add_employee():

    data = request.get_json()

    if not data or not data.get("name") or not data.get("department"):
        return jsonify({"error": "Name and department are required"}), 400

    new_employee = {
        "id": max([e["id"] for e in employees], default=0) + 1,
        "name": data["name"],
        "department": data["department"]
    }

    employees.append(new_employee)

    return jsonify({
        "message": "Employee added successfully",
        "employee": new_employee
    }), 201


# PUT: Update employee (Admin only)
@app.route("/employees/<int:employee_id>", methods=["PUT"])
@authenticate("admin")
def update_employee(employee_id):

    employee = next(
        (e for e in employees if e["id"] == employee_id), None
    )

    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    data = request.get_json() or {}

    employee["name"] = data.get("name", employee["name"])
    employee["department"] = data.get(
        "department", employee["department"]
    )

    return jsonify({
        "message": "Employee updated successfully",
        "employee": employee
    }), 200


# DELETE: Delete employee (Admin only)
@app.route("/employees/<int:employee_id>", methods=["DELETE"])
@authenticate("admin")
def delete_employee(employee_id):

    employee = next(
        (e for e in employees if e["id"] == employee_id), None
    )

    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    employees.remove(employee)

    return jsonify({
        "message": "Employee deleted successfully"
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
