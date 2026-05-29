import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# ==========================================
# LOAD DATASET
# ==========================================

df = pd.read_excel("svm.xlsx")

print("First 5 Rows:\n")
print(df.head())

print("\nDataset Shape:")
print(df.shape)

# ==========================================
# FEATURES AND TARGET
# ==========================================

X = df.drop(
    ["ID", "ZIP Code", "Personal Loan"],
    axis=1
)

y = df["Personal Loan"]

# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ==========================================
# FEATURE SCALING
# ==========================================

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ==========================================
# TRAIN SVM MODEL
# ==========================================

print("\nTraining Model...")

model = SVC(
    kernel="rbf",
    C=1,
    gamma="scale"
)

model.fit(X_train, y_train)

print("\nModel Training Completed!")

# ==========================================
# TEST MODEL
# ==========================================

y_pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\nModel Accuracy:", round(accuracy, 4))

# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    model,
    "svm_model.pkl"
)

joblib.dump(
    scaler,
    "scaler.pkl"
)

print("\nModel Saved Successfully!")