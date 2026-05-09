from flask import Blueprint, request, jsonify
from auth import token_required
from models.units_model import get_total_daily_kwh, get_user_appliances
import os
import requests

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/predict', methods=['POST'])
@token_required
def predict():
    data = request.get_json()
    units_bought = data.get('units_bought')

    if not units_bought:
        return jsonify({"error": "units_bought is required"}), 400

    try:
        units_bought = float(units_bought)
    except ValueError:
        return jsonify({"error": "Invalid value for units_bought"}), 400

    total_daily_kwh = get_total_daily_kwh(request.user_id)

    if total_daily_kwh == 0:
        return jsonify({"error": "No appliances added yet. Add your appliances first."}), 400

    days_remaining = round(units_bought / total_daily_kwh, 1)

    return jsonify({
        "units_bought": units_bought,
        "total_daily_consumption_kwh": total_daily_kwh,
        "predicted_days": days_remaining,
        "message": f"Your {units_bought} kWh units will last approximately {days_remaining} days based on your appliances."
    }), 200


@predict_bp.route('/ai-advice', methods=['GET'])
@token_required
def ai_advice():
    appliances = get_user_appliances(request.user_id)
    total_daily_kwh = get_total_daily_kwh(request.user_id)

    if not appliances:
        return jsonify({"error": "No appliances added yet. Add your appliances first."}), 400

    appliance_list = "\n".join([
        f"- {a['name']} (x{a.get('quantity', 1)}): {a['watts']}W, {a['usage_level']} user, {a['hours_per_day']} hours/day, consuming {a['daily_kwh']} kWh/day"
        for a in appliances
    ])

    prompt = f"""You are an energy efficiency advisor. A household has the following appliances:

{appliance_list}

Total daily energy consumption: {total_daily_kwh} kWh

Please provide:
1. A brief analysis of their energy usage
2. Which appliance consumes the most energy
3. Three practical tips to reduce their energy consumption
4. An estimate of their monthly energy cost if 1 kWh costs 100 Nigerian Naira

Keep your response friendly, clear, and practical. Use simple language."""

    try:
        groq_key = os.getenv("GROQ_API_KEY")
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500
            }
        )
        result = response.json()
        print("Groq response:", result)
        if "choices" not in result:
            return jsonify({"error": result.get("error", {}).get("message", "AI service error")}), 500
        advice = result["choices"][0]["message"]["content"]
        return jsonify({"advice": advice}), 200

    except Exception as e:
        print("AI Error:", str(e))
        return jsonify({"error": str(e)}), 500


@predict_bp.route('/admin/stats', methods=['GET'])
def admin_stats():
    secret = request.args.get('key')
    if secret != 'energyadmin2026':
        return jsonify({"error": "Unauthorized"}), 401

    from config import db
    from models.units_model import appliances_collection

    users = list(db['users'].find({}, {'password': 0}))
    appliances = list(db['appliances'].find({}))
    logs = list(db['units_log'].find({}))

    formatted_users = []
    for u in users:
        user_id = str(u['_id'])
        user_apps = [a for a in appliances if a['user_id'] == user_id]
        user_logs = [l for l in logs if l['user_id'] == user_id]
        formatted_users.append({
            "id": user_id,
            "name": u.get('name', ''),
            "email": u.get('email', ''),
            "registered": u.get('created_at', '').isoformat() if u.get('created_at') else 'N/A',
            "appliance_count": len(user_apps),
            "log_count": len(user_logs),
        })

    appliance_names = [a['name'] for a in appliances]
    appliance_counts = {}
    for name in appliance_names:
        appliance_counts[name] = appliance_counts.get(name, 0) + 1
    top_appliances = sorted(appliance_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return jsonify({
        "total_users": len(users),
        "total_appliances": len(appliances),
        "total_logs": len(logs),
        "users": formatted_users,
        "top_appliances": [{"name": k, "count": v} for k, v in top_appliances]
    }), 200