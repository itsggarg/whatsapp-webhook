from flask import Flask, request, jsonify
import csv, datetime, os

app = Flask(__name__)

VERIFY_TOKEN = "keshav30.11"

# Ensure CSV exists
if not os.path.exists("delivery_log.csv"):
    with open("delivery_log.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["number", "status", "reason", "timestamp"])

@app.route('/webhook', methods=['GET'])
def verify():
    # Verification step
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge')
    return "Invalid verify token", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if not data:
        return "No data", 400

    # WhatsApp webhook format
    if 'entry' in data:
        for entry in data['entry']:
            for change in entry['changes']:
                value = change.get("value", {})

                # Status updates (delivery/read/failed)
                if "statuses" in value:
                    for status in value["statuses"]:
                        log_status(status)

    return "OK", 200

def log_status(status):
    number = status.get("recipient_id")
    status_type = status.get("status")
    reason = ""

    if status_type == "failed" and status.get("errors"):
        reason = status["errors"][0].get("title", "")

    timestamp = datetime.datetime.now().isoformat()

    # Append to CSV
    with open("delivery_log.csv", "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([number, status_type, reason, timestamp])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
