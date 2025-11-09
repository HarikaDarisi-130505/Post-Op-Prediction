# --- START OF FILE app.py ---

from flask import Flask, request, render_template, jsonify, url_for
import joblib
import numpy as np
import requests
import os
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO



# For OCR:
from PIL import Image
import pytesseract

# --- IMPORTANT: Configure Tesseract path if not in system PATH ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Windows example
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract' # macOS example (if installed via brew)
# Ensure Tesseract-OCR is installed on your system!


app = Flask(__name__)

# Load the trained model
model = joblib.load('post_op_recovery_model.joblib')

# Feature column names expected for input
# Note: These map to numeric values in your HTML, which is good.
features = ['L-CORE', 'L-SURF', 'L-O2', 'L-BP', 
            'SURF-STBL', 'CORE-STBL', 'BP-STBL', 'COMFORT']

# --- Telegram Bot Configuration (Get these from BotFather and your chat) ---
# **** IMPORTANT: REPLACE THESE WITH YOUR ACTUAL BOT TOKEN AND CHAT ID ****
# You got your bot token from BotFather (e.g., 1234567890:ABCDEFGHIJ...)
TELEGRAM_BOT_TOKEN = '8517201845:AAFOZwkT8TgUiKvRnMdklupAH2lB2MD3v5Y' # <-- REPLACE THIS!
# You got your chat ID by sending /start to your bot, then using getUpdates or a bot like @userinfobot
TELEGRAM_CHAT_ID = '6839323386'   # <-- REPLACE THIS!

def send_telegram_notification(message, chat_id=None):
    """Send a Telegram message.
    Returns: (success: bool, info: dict)
    On success, info will be Telegram's response JSON. On failure, info will contain error details.
    """
    # allow overriding chat_id for testing without changing source
    target_chat = chat_id if chat_id is not None else TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': target_chat,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload, timeout=8)
    except requests.exceptions.RequestException as e:
        err = {'error': 'request_exception', 'detail': str(e)}
        print('Telegram request exception:', err)
        return False, err

    # Try to parse JSON even if HTTP status is not 200
    try:
        resp_json = response.json()
    except Exception:
        err = {'error': 'invalid_json', 'text': response.text}
        print('Telegram: failed to parse JSON response:', response.text)
        return False, err

    if not resp_json.get('ok'):
        # API-level error (e.g., chat not found, bot blocked)
        print('Telegram API responded with error:', resp_json)
        return False, resp_json

    print('Telegram notification sent successfully! ✅', resp_json.get('result'))
    return True, resp_json

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # Parse form inputs as integers
            input_values = [int(request.form[feature]) for feature in features]

            # --- DEBUG LOG: Print received form fields and numeric vector ---
            try:
                received = {k: request.form.get(k) for k in request.form.keys()}
                print('\n--- Server DEBUG: Received form fields ---')
                for k, v in received.items():
                    print(f"{k}: {v}")
                print('Feature vector (ordered):', input_values)
                print('--- End DEBUG ---\n')
            except Exception as _e:
                print('Server debug logging failed:', _e)

            # Create numpy array for prediction
            input_array = np.array(input_values).reshape(1, -1)

            # Make prediction
            pred = model.predict(input_array)[0]

            # Label mapping
            pred_label = 'Normal' if pred == 0 else 'Abnormal'

            # --- Save Patient Data to Database ---
            trend_map = {'Normal': 1, 'Abnormal': 0}
            trend_value = trend_map[pred_label]

            DB_PATH = os.path.join(os.path.dirname(__file__), 'patients.db')
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO patients 
                (name, age, phone, L_CORE, L_SURF, L_O2, L_BP, SURF_STBL, CORE_STBL, BP_STBL, COMFORT, prediction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form['name'],
                request.form['age'],
                request.form['phone'],
                *input_values,
                trend_value
            ))
            conn.commit()
            conn.close()

            # --- Send Telegram Alert for Abnormal Patients ---
            if pred_label == 'Abnormal':
                display_map = {
                    'L-CORE': {0: 'high', 1: 'low', 2: 'mid'},
                    'L-SURF': {0: 'high', 1: 'low', 2: 'mid'},
                    'L-O2': {0: 'excellent', 1: 'good'},
                    'L-BP': {0: 'high', 1: 'low', 2: 'mid'},
                    'SURF-STBL': {0: 'stable', 1: 'unstable'},
                    'CORE-STBL': {0: 'mod-stable', 1: 'stable', 2: 'unstable'},
                    'BP-STBL': {0: 'mod-stable', 1: 'stable', 2: 'unstable'},
                    'COMFORT': {0: '10', 1: '15', 2: '5', 3: '7', 4: 'N/A'}
                }

                details = ""
                for i, f in enumerate(features):
                    original_value = input_values[i]
                    readable_value = display_map[f].get(original_value, str(original_value))
                    details += f"• *{f}*: {readable_value}\n"

                message = (
                    "⚠️ *Critical Post-Op Recovery Alert!* ⚠️\n\n"
                    f"👤 *Patient:* {request.form['name']}\n"
                    f"📞 *Phone:* {request.form['phone']}\n\n"
                    f"🔍 *Prediction:* {pred_label}\n\n"
                    "🩺 *Patient Vitals:*\n"
                    f"{details}"
                    "\n📢 *Immediate review is recommended.*"
                )

                send_telegram_notification(message)


            return render_template('result1.html', prediction=pred_label)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error processing prediction: {str(e)}"

    return render_template('form3.html')


@app.route('/predict_ajax', methods=['POST'])
def predict_ajax():
    """AJAX-friendly prediction endpoint. Returns JSON with prediction and whether Telegram was sent."""
    try:
        # Parse numeric features
        input_values = [int(request.form[feature]) for feature in features]
        input_array = np.array(input_values).reshape(1, -1)

        pred = model.predict(input_array)[0]
        pred_label = 'Normal' if pred == 0 else 'Abnormal'

        # Save to DB
        trend_map = {'Normal': 1, 'Abnormal': 0}
        trend_value = trend_map[pred_label]
        conn = sqlite3.connect('patients.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO patients 
            (name, age, phone, L_CORE, L_SURF, L_O2, L_BP, SURF_STBL, CORE_STBL, BP_STBL, COMFORT, prediction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form.get('name',''),
            request.form.get('age',''),
            request.form.get('phone',''),
            *input_values,
            trend_value
        ))
        conn.commit()
        conn.close()
        telegram_sent = False
        telegram_resp = None
        # Send Telegram only for Abnormal predictions
        if pred_label == 'Abnormal':
            display_map = {
                'L-CORE': {0: 'high', 1: 'low', 2: 'mid'},
                'L-SURF': {0: 'high', 1: 'low', 2: 'mid'},
                'L-O2': {0: 'excellent', 1: 'good'},
                'L-BP': {0: 'high', 1: 'low', 2: 'mid'},
                'SURF-STBL': {0: 'stable', 1: 'unstable'},
                'CORE-STBL': {0: 'mod-stable', 1: 'stable', 2: 'unstable'},
                'BP-STBL': {0: 'mod-stable', 1: 'stable', 2: 'unstable'},
                'COMFORT': {0: '10', 1: '15', 2: '5', 3: '7', 4: 'N/A'}
            }

            details = ""
            for i, f in enumerate(features):
                original_value = input_values[i]
                readable_value = display_map[f].get(original_value, str(original_value))
                details += f"• *{f}*: {readable_value}\n"

            message = (
                "⚠️ *Critical Post-Op Recovery Alert!* ⚠️\n\n"
                f"👤 *Patient:* {request.form.get('name','Unknown')}\n"
                f"📞 *Phone:* {request.form.get('phone','N/A')}\n\n"
                f"🔍 *Prediction:* {pred_label}\n\n"
                "🩺 *Patient Vitals:*\n"
                f"{details}"
                "\n📢 *Immediate review is recommended.*"
            )

            try:
                telegram_sent, telegram_resp = send_telegram_notification(message)
            except Exception as e:
                telegram_sent = False
                telegram_resp = {'error': 'exception', 'detail': str(e)}

        result = {'prediction': pred_label, 'telegram_sent': bool(telegram_sent)}
        if telegram_resp is not None:
            result['telegram_response'] = telegram_resp
        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/send_alert', methods=['POST'])
def send_alert():
    """Send a manual Telegram alert for testing. Accepts either a 'message' field or builds a simple message from name/phone."""
    try:
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        custom = request.form.get('message', '').strip()
        # allow optional chat_id override via form or JSON
        json_data = request.get_json(silent=True)
        chat_id = request.form.get('chat_id') or (json_data and json_data.get('chat_id'))

        if custom:
            message = custom
        else:
            # Basic test message
            message = (
                "🔔 *Manual Test Alert*\n\n"
                f"👤 *Patient:* {name or 'Unknown'}\n"
                f"📞 *Phone:* {phone or 'N/A'}\n\n"
                "This is a manual test alert."
            )

        try:
            sent, resp = send_telegram_notification(message, chat_id=chat_id if chat_id else None)
            result = {'telegram_sent': bool(sent), 'telegram_response': resp}
            return jsonify(result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/tg_debug', methods=['GET'])
def tg_debug():
    """Call Telegram getMe to verify token validity and return API response."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    try:
        resp = requests.get(url, timeout=6)
        try:
            return jsonify(resp.json())
        except Exception:
            return jsonify({'error': 'invalid_response', 'text': resp.text}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'request_exception', 'detail': str(e)}), 500


@app.route('/set_chat', methods=['POST'])
def set_chat():
    """Temporarily set TELEGRAM_CHAT_ID at runtime for testing (POST form: chat_id)."""
    global TELEGRAM_CHAT_ID
    json_data = request.get_json(silent=True)
    chat = request.form.get('chat_id') or (json_data and json_data.get('chat_id'))
    if not chat:
        return jsonify({'error': 'no_chat_id_provided'}), 400
    TELEGRAM_CHAT_ID = str(chat)
    return jsonify({'chat_id': TELEGRAM_CHAT_ID})


@app.route('/get_chat', methods=['GET'])
def get_chat():
    return jsonify({'chat_id': TELEGRAM_CHAT_ID})


@app.route('/patient/<phone>')
def patient_history(phone):
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, prediction FROM patients 
        WHERE phone = ?
        ORDER BY timestamp ASC
    """, (phone,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        return f"No records found for phone {phone}"

    timestamps = [row[0] for row in data]
    scores = [row[1] for row in data]

    plt.figure(figsize=(7,4))
    plt.plot(timestamps, scores, marker='o', linewidth=2)
    plt.ylim(-0.5, 2.5)
    plt.yticks([0,1,2], ['Critical', 'Observe', 'Stable'])
    plt.xticks(rotation=30)
    plt.xlabel("Visit Date")
    plt.ylabel("Recovery Status")
    plt.title("Recovery Trend")
    
    img = BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()

    return render_template("patient_history.html", graph=graph_url, phone=phone)

@app.route('/records')
def show_records():
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id,             -- ✅ include id
            name,
            age,
            phone,
            CAST(prediction AS INTEGER),  -- ✅ ensure numeric for status
            timestamp
        FROM patients
        ORDER BY timestamp ASC
    """)
    data = cursor.fetchall()
    conn.close()
    return render_template('records.html', records=data)

@app.route('/delete/<int:id>', methods=['GET'])
def delete_record(id):
    import sqlite3
    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return """<script>
                alert('Record deleted successfully!');
                window.location.href='/records';
              </script>"""
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_record(id):
    import sqlite3

    conn = sqlite3.connect('patients.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        cursor.execute("""
            UPDATE patients SET 
            name=?, age=?, phone=?, L_CORE=?, L_SURF=?, L_O2=?, L_BP=?, 
            SURF_STBL=?, CORE_STBL=?, BP_STBL=?, COMFORT=?, prediction=?
            WHERE id=?
        """, (
            request.form['name'],
            request.form['age'],
            request.form['phone'],
            request.form['L-CORE'],
            request.form['L-SURF'],
            request.form['L-O2'],
            request.form['L-BP'],
            request.form['SURF-STBL'],
            request.form['CORE-STBL'],
            request.form['BP-STBL'],
            request.form['COMFORT'],
            request.form['prediction'],
            id
        ))
        conn.commit()
        conn.close()
        return """<script>alert('Record Updated Successfully!'); window.location.href='/records';</script>"""

    cursor.execute("SELECT * FROM patients WHERE id=?", (id,))
    patient = cursor.fetchone()
    conn.close()

    return render_template('edit.html', patient=patient)



if __name__ == '__main__':
    # Make sure to create a 'static/images' directory for your logo and background
    # Example:
    # os.makedirs('static/images', exist_ok=True)
    # Then place 'logo.png' and 'recovery_background.png' inside it.
    app.run(debug=False) # Set debug=False for production
