from flask import Flask, request, render_template
import joblib
import numpy as np

app = Flask(__name__)

# Load the trained model
model = joblib.load('post_op_recovery_model.joblib')

# Feature column names expected for input
features = ['L-CORE', 'L-SURF', 'L-O2', 'L-BP', 
            'SURF-STBL', 'CORE-STBL', 'BP-STBL', 'COMFORT']

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # Parse form inputs as integers
            input_values = [int(request.form[feature]) for feature in features]
            
            # Create numpy array for prediction
            input_array = np.array(input_values).reshape(1, -1)
            
            # Make prediction
            pred = model.predict(input_array)[0]
            
            # Map numeric prediction back to label (optional)
            # Update accordingly with your label classes
            pred_label = 'Normal' if pred == 0 else 'Abnormal'
            
            return render_template('result.html', prediction=pred_label)
        except Exception as e:
            return f"Error: {str(e)}"
    
    return render_template('form.html', features=features)

if __name__ == '__main__':
    app.run(debug=False)
