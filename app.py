from urllib.parse import urlencode
import os
import threading
import webbrowser

from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib

app = Flask(__name__)

model  = joblib.load("svm_model.pkl")
scaler = joblib.load("scaler.pkl")
df     = pd.read_excel("svm.xlsx")

REQUIRED_FIELDS = ["age","experience","income","family","ccavg","education",
                   "mortgage","securities","cd_account","online","creditcard"]


def safe_float(value, field):
    try:
        v = float(value)
        if v != v or v in (float('inf'), float('-inf')):
            raise ValueError(f"Invalid value for {field}")
        return v
    except (TypeError, ValueError):
        raise ValueError(f"Invalid numeric value for field: {field}")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


@app.route("/chart-data")
def chart_data():
    loan_counts     = df["Personal Loan"].value_counts().to_dict()
    edu_counts      = df["Education"].value_counts().sort_index().to_dict()
    income_by_loan  = df.groupby("Personal Loan")["Income"].mean().round(2).to_dict()
    approval_by_edu = df.groupby("Education")["Personal Loan"].mean().mul(100).round(1).to_dict()
    family_counts   = df["Family"].value_counts().sort_index().to_dict()
    ccavg_by_loan   = df.groupby("Personal Loan")["CCAvg"].mean().round(2).to_dict()
    cd_approval     = df.groupby("CD Account")["Personal Loan"].mean().mul(100).round(1).to_dict()
    online_approval = df.groupby("Online")["Personal Loan"].mean().mul(100).round(1).to_dict()

    return jsonify({
        "loan_counts":     {str(k): v for k, v in loan_counts.items()},
        "edu_counts":      {str(k): v for k, v in edu_counts.items()},
        "income_by_loan":  {str(k): v for k, v in income_by_loan.items()},
        "approval_by_edu": {str(k): v for k, v in approval_by_edu.items()},
        "family_counts":   {str(k): v for k, v in family_counts.items()},
        "ccavg_by_loan":   {str(k): v for k, v in ccavg_by_loan.items()},
        "cd_approval":     {str(k): v for k, v in cd_approval.items()},
        "online_approval": {str(k): v for k, v in online_approval.items()}
    })


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    for field in REQUIRED_FIELDS:
        if field not in data or str(data[field]).strip() == "":
            return jsonify({"error": f"Missing field: {field}"}), 400

    query = urlencode({field: data[field] for field in REQUIRED_FIELDS})
    return jsonify({"redirect": f"/result?{query}"})


@app.route("/result")
def result():
    data = request.args

    for field in REQUIRED_FIELDS:
        if field not in data or data[field].strip() == "":
            return render_template("index.html", error=f"Missing field: {field}"), 400

    try:
        values = [safe_float(data[f], f) for f in REQUIRED_FIELDS]
    except ValueError as e:
        return render_template("index.html", error=str(e)), 400

    sample = pd.DataFrame([values], columns=[
        "Age", "Experience", "Income", "Family", "CCAvg",
        "Education", "Mortgage", "Securities Account",
        "CD Account", "Online", "CreditCard"
    ])

    scaled     = scaler.transform(sample)
    prediction = model.predict(scaled)[0]
    eligible   = bool(prediction == 1)

    return render_template("result.html",
        eligible=eligible,
        prediction="Eligible for Personal Loan" if eligible else "Not Eligible for Personal Loan",
        age=data["age"], experience=data["experience"], income=data["income"],
        family=data["family"], ccavg=data["ccavg"], education=data["education"],
        mortgage=data["mortgage"], securities=data["securities"],
        cd_account=data["cd_account"], online=data["online"], creditcard=data["creditcard"]
    )


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=True)
