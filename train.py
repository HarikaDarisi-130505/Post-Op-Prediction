import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load dataset
file_path = 'post-operative-data.csv'
df = pd.read_csv(file_path)

# Clean target column by stripping spaces
df['decision ADM-DECS'] = df['decision ADM-DECS'].str.strip()

# Encode categorical features
label_encoders = {}
for col in df.columns:
    if col != 'decision ADM-DECS':
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le

# Encode target
target_le = LabelEncoder()
df['decision ADM-DECS'] = target_le.fit_transform(df['decision ADM-DECS'])

# Features and target
X = df.drop('decision ADM-DECS', axis=1)
y = df['decision ADM-DECS']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
report = classification_report(y_test, predictions)

# Save model to disk
model_filename = 'post_op_recovery_model.joblib'
joblib.dump(model, model_filename)

print("Accuracy:", accuracy)
print("Classification Report:\n", report)
print("Model saved to:", model_filename)
