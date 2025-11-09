import joblib
import numpy as np

model = joblib.load('post_op_recovery_model.joblib')
# replace with the vector you saw in the debug output
vec = np.array([[1,1,1,0,1,2,2,2]])
pred = model.predict(vec)[0]
print('raw prediction:', pred)
print('label:', 'Normal' if pred==0 else 'Abnormal')