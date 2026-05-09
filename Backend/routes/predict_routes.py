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
        f"- {a['name']}: {a['watts']}W, used {a['hours_per_day']} hours/day, consuming {a['daily_kwh']} kWh/day"
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