import tkinter as tk
from tkinter import messagebox, filedialog
import os
import hashlib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from tpot import TPOTClassifier
from sklearn import linear_model
from datetime import datetime, timedelta

# Password Hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Registration Page
def register():
    reg_window = tk.Toplevel(root)
    reg_window.title("Register")
    reg_window.geometry("400x300")
    reg_window.config(bg="#FF6347")

    # Title Label
    tk.Label(reg_window, text="Register", font=("Arial", 24), bg="#FF6347").pack(pady=10)

    # Username Entry
    tk.Label(reg_window, text="Username:", bg="#FF6347", font=("Arial", 12)).pack(pady=5)
    reg_username_entry = tk.Entry(reg_window, font=("Arial", 12))
    reg_username_entry.pack(pady=5)

    # Password Entry
    tk.Label(reg_window, text="Password:", bg="#FF6347", font=("Arial", 12)).pack(pady=5)
    reg_password_entry = tk.Entry(reg_window, show="*", font=("Arial", 12))
    reg_password_entry.pack(pady=5)

    def save_user():
        username = reg_username_entry.get()
        password = reg_password_entry.get()
        if username and password:
            if not os.path.exists("users"):
                os.mkdir("users")
            with open(f"users/{username}.txt", "w") as file:
                file.write(hash_password(password))
            messagebox.showinfo("Success", "User registered successfully!")
            reg_window.destroy()
        else:
            messagebox.showerror("Error", "Both fields are required!")

    # Register Button
    tk.Button(reg_window, text="Register", command=save_user, font=("Arial", 14), bg="black", fg="white").pack(pady=20)

# Login Page
def login():
    username = username_entry.get()
    password = password_entry.get()
    if username and password:
        try:
            with open(f"users/{username}.txt", "r") as file:
                stored_password = file.read()
            if stored_password == hash_password(password):
                messagebox.showinfo("Login Success", "Welcome :)")
                if check_last_donation(username):
                    root.withdraw()
                    prediction_window(username)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        except FileNotFoundError:
            messagebox.showerror("Login Failed", "User not found")
    else:
        messagebox.showerror("Error", "Both fields are required!")

# Check Last Donation Date
def check_last_donation(username):
    last_donation_file = f"users/{username}_last_donation.txt"
    if os.path.exists(last_donation_file):
        with open(last_donation_file, 'r') as file:
            last_donation_date_str = file.read()
            last_donation_date = datetime.strptime(last_donation_date_str, "%Y-%m-%d")
            if datetime.now() < last_donation_date + timedelta(days=180):
                remaining_days = (last_donation_date + timedelta(days=180) - datetime.now()).days
                messagebox.showwarning(
                    "Wait for Donation",
                    f"You cannot donate again yet. You must wait {remaining_days} more days Because you are donating blood today"
                )
                return False
    return True

# Prediction Window (styled like a medical form with dark blue background)
def prediction_window(username):
    pred_window = tk.Toplevel(root)
    pred_window.title("Blood Donation Prediction")
    pred_window.geometry("500x700")
    pred_window.config(bg="#003366")  # Dark blue background

    # Title Label with underline
    tk.Label(pred_window, text="Medical Blood Donation Form", font=("Arial", 24, "bold", "underline"), bg="#003366", fg="white").pack(pady=20)

    # Logout Button
    def logout():
        pred_window.destroy()
        root.deiconify()
    tk.Button(pred_window, text="Logout", command=logout, font=("Arial", 20), bg="black", fg="white").place(x=715, y=650)
    # Patient Information Section with underline
    section_title = tk.Label(pred_window, text="Patient Information", font=("Arial", 18, "bold", "underline"), bg="#003366", fg="light blue")
    section_title.pack(pady=5)

    # Align Patient Information Entries and Labels
    form_frame = tk.Frame(pred_window, bg="#003366")
    form_frame.pack(pady=5)

    tk.Label(form_frame, text="Patient Name:", bg="#003366", fg="white", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    patient_name_entry = tk.Entry(form_frame, font=("Arial", 12))
    patient_name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(form_frame, text="Male/Female:", bg="#003366", fg="white", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
    patient_name_entry = tk.Entry(form_frame, font=("Arial", 12))
    patient_name_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(form_frame, text="Age:", bg="#003366", fg="white", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
    age_entry = tk.Entry(form_frame, font=("Arial", 12))
    age_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(form_frame, text="Blood Group:", bg="#003366", fg="white", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=5, sticky="w")
    blood_group_entry = tk.Entry(form_frame, font=("Arial", 12))
    blood_group_entry.grid(row=3, column=1, padx=10, pady=5)

    # File Upload for Blood Report
    previous_report_path = tk.StringVar()
    def upload_report():
        report_file = filedialog.askopenfilename(title="Select Blood Group Report",
                                                 filetypes=[("Text files", "*.txt"), ("only reports", "*.*")])
        if report_file:
            previous_report_path.set(report_file)
            messagebox.showinfo("File Selected", f"Selected file: {os.path.basename(report_file)}")
        else:
            messagebox.showerror("Error", "No file selected")

    tk.Button(pred_window, text="Upload Blood Group Report", command=upload_report, font=("Arial", 16),
              bg="light blue", fg="black").pack(pady=10)

    # Donation Information Section with underline
    section_title = tk.Label(pred_window, text="Donation Information", font=("Arial", 18, "bold", "underline"), bg="#003366", fg="light blue")
    section_title.pack(pady=10)

    # Align Donation Information Entries and Labels
    donation_frame = tk.Frame(pred_window, bg="#003366")
    donation_frame.pack(pady=5)

    tk.Label(donation_frame, text="Recency (months):", bg="#003366", fg="white", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    recency_entry = tk.Entry(donation_frame, font=("Arial", 12))
    recency_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(donation_frame, text="Frequency (times):", bg="#003366", fg="white", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
    frequency_entry = tk.Entry(donation_frame, font=("Arial", 12))
    frequency_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(donation_frame, text="Monetary blood {C.C(Cubic centimeter)(1 unit blood = 500cc)}:", bg="#003366", fg="white", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
    monetary_entry = tk.Entry(donation_frame, font=("Arial", 12))
    monetary_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(donation_frame, text="Time (months):", bg="#003366", fg="white", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=5, sticky="w")
    time_entry = tk.Entry(donation_frame, font=("Arial", 12))
    time_entry.grid(row=3, column=1, padx=10, pady=5)

    # Prediction Function
    def predict():
        if not check_last_donation(username):
            return  # Stop if user has to wait

        patient_name = patient_name_entry.get()
        age = age_entry.get()
        blood_group = blood_group_entry.get()

        try:
            recency = int(recency_entry.get())
            frequency = int(frequency_entry.get())
            monetary = int(monetary_entry.get())
            time = int(time_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Recency, Frequency, Monetary, and Time must be integers.")
            return

        if previous_report_path.get():
            try:
                with open(previous_report_path.get(), 'r') as file:
                    previous_report = file.read()
                    messagebox.showinfo("Previous Blood Group Report", f"Content of Report:\n{previous_report}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load the report: {str(e)}")

        try:
            transfusion = pd.read_csv('C:/Users/adars/Downloads/transfusion.data')
        except FileNotFoundError:
            messagebox.showerror("Error", "Dataset not found. Please ensure the file is present at the specified location.")
            return

        transfusion.rename(columns={'whether he/she donated blood in March 2007': 'target'}, inplace=True)

        X_train, X_test, y_train, y_test = train_test_split(
            transfusion.drop(columns='target'),
            transfusion.target,
            test_size=0.25,
            random_state=42,
            stratify=transfusion.target
        )

        tpot = TPOTClassifier(
            generations=5,
            population_size=20,
            verbosity=2,
            scoring='roc_auc',
            random_state=42,
            disable_update_check=True,
            config_dict='TPOT light'
        )
        tpot.fit(X_train, y_train)

        X_train_normed, X_test_normed = X_train.copy(), X_test.copy()
        col_to_normalize = 'Monetary (c.c. blood)'
        for df_ in [X_train_normed, X_test_normed]:
            df_['monetary_log'] = np.log(df_[col_to_normalize])
            df_.drop(columns=col_to_normalize, inplace=True)

        logreg = linear_model.LogisticRegression(solver='liblinear', random_state=42)
        logreg.fit(X_train_normed, y_train)

        input_data = pd.DataFrame([[recency, frequency, monetary, time]], columns=X_train.columns)
        input_data['monetary_log'] = np.log(input_data['Monetary (c.c. blood)'])
        input_data.drop(columns='Monetary (c.c. blood)', inplace=True)

        prediction_logreg = logreg.predict_proba(input_data)[:, 1][0]
        prediction_result = "Yes" if prediction_logreg >= 0.5 else "No"
        percentage = prediction_logreg * 100

        result = f'Patient Name: {patient_name}\nAge: {age}\nBlood Group: {blood_group}\n\nPrediction: {prediction_result}\nConfidence: {percentage:.2f}%'
        messagebox.showinfo("Prediction Result", result)

        if prediction_result == "Yes":
            last_donation_file = f"users/{username}_last_donation.txt"
            with open(last_donation_file, 'w') as file:
                file.write(datetime.now().strftime("%Y-%m-%d"))

    # Predict Button
    tk.Button(pred_window, text="Predict", command=predict, font=("Arial", 20), bg="black", fg="white").pack(pady=20)

root = tk.Tk()
root.title("Login Page")
root.geometry("400x400")
root.config(bg="#ffffcc")

# Title Label
tk.Label(root, text="Login", font=("Arial", 28), bg="#ffffcc").pack(pady=40)

# Username Entry
tk.Label(root, text="Username:", font=("Arial", 14), bg="#ffffcc").pack(pady=10)
username_entry = tk.Entry(root, font=("Arial", 14))
username_entry.pack(pady=10)

# Password Entry
tk.Label(root, text="Password:", font=("Arial", 14), bg="#ffffcc").pack(pady=10)
password_entry = tk.Entry(root, show="#", font=("Arial", 14))
password_entry.pack(pady=10)

# Login Button
tk.Button(root, text="Login", font=("Arial", 18), command=login, bg="black", fg="white").pack(pady=20)

# Register Button
tk.Button(root, text="Register", font=("Arial", 18), command=register, bg="black", fg="white").pack(pady=20)

root.mainloop()
