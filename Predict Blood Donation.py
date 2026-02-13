import tkinter as tk
from tkinter import messagebox
import os
import hashlib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from tpot import TPOTClassifier
from sklearn import linear_model

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register():
    reg_window = tk.Toplevel(root)
    reg_window.title("Register")
    reg_window.geometry("400x300")

    tk.Label(reg_window, text="Username:").pack(pady=10)
    reg_username_entry = tk.Entry(reg_window)
    reg_username_entry.pack(pady=5)

    tk.Label(reg_window, text="Password:").pack(pady=10)
    reg_password_entry = tk.Entry(reg_window, show="*")
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

    tk.Button(reg_window, text="Register", command=save_user).pack(pady=20)

def login():
    username = username_entry.get()
    password = password_entry.get()
    if username and password:
        try:
            with open(f"users/{username}.txt", "r") as file:
                stored_password = file.read()
            if stored_password == hash_password(password):
                messagebox.showinfo("Login Success", "Welcome!")
                root.withdraw()
                prediction_window()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        except FileNotFoundError:
            messagebox.showerror("Login Failed", "User not found")
    else:
        messagebox.showerror("Error", "Both fields are required!")

def prediction_window():
    pred_window = tk.Toplevel(root)
    pred_window.title("Blood Donation Prediction")
    pred_window.geometry("400x400")

    tk.Label(pred_window, text="Recency (months):").pack(pady=10)
    recency_entry = tk.Entry(pred_window)
    recency_entry.pack(pady=5)

    tk.Label(pred_window, text="Frequency (times):").pack(pady=10)
    frequency_entry = tk.Entry(pred_window)
    frequency_entry.pack(pady=5)

    tk.Label(pred_window, text="Monetary (c.c. blood):").pack(pady=10)
    monetary_entry = tk.Entry(pred_window)
    monetary_entry.pack(pady=5)

    tk.Label(pred_window, text="Time (months):").pack(pady=10)
    time_entry = tk.Entry(pred_window)
    time_entry.pack(pady=5)

    def predict():
        recency = int(recency_entry.get())
        frequency = int(frequency_entry.get())
        monetary = int(monetary_entry.get())
        time = int(time_entry.get())

        # Load and preprocess the dataset
        transfusion = pd.read_csv('C:/Users/adars/Downloads/transfusion.data')
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

        # Set a threshold, typically 0.5 for classification
        prediction_result = "Yes" if prediction_logreg >= 0.5 else "No"
        percentage = prediction_logreg * 100

        result = f'Prediction: {prediction_result}\nConfidence: {percentage:.2f}%'
        messagebox.showinfo("Prediction Result", result)

    tk.Button(pred_window, text="Predict", command=predict).pack(pady=20)

root = tk.Tk()
root.title("Login Page")
root.geometry("400x400")
tk.Label(root, text="Login", font=("Arial", 24)).pack(pady=50)
tk.Label(root, text="Username:", font=("Arial", 14)).pack(pady=10)
username_entry = tk.Entry(root, font=("Arial", 14))
username_entry.pack(pady=10)
tk.Label(root, text="Password:", font=("Arial", 14)).pack(pady=10)
password_entry = tk.Entry(root, show="*", font=("Arial", 14))
password_entry.pack(pady=10)
tk.Button(root, text="Login", font=("Arial", 14), command=login).pack(pady=20)
tk.Button(root, text="Register", font=("Arial", 14), command=register).pack(pady=10)
root.mainloop()

