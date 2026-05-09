from flask import Blueprint, request, jsonify
from models.units_model import (
    add_unit_log, get_user_logs,
    add_appliance, get_user_appliances,
    delete_appliance, get_total_daily_kwh,
    APPLIANCE_DATABASE
)
from auth import token_required

units_bp = Blueprint('units', __name__)

@units_bp.route('/add', methods=['POST'])
@token_required
def add_log():
    data = request.get_json()
    log_type = data.get('type')
    amount = data.get('amount')
    note = data.get('note', '')

    if not log_type or not amount:
        return jsonify({"error": "Type and amount are required"}), 400

    if log_type not in ['bought', 'finished']:
        return jsonify({"error": "Type must be bought or finished"}), 400

    log_id = add_unit_log(request.user_id, log_type, amount, note)
    return jsonify({"message": "Log added successfully", "log_id": log_id}), 201

@units_bp.route('/history', methods=['GET'])
@token_required
def get_history():
    logs = get_user_logs(request.user_id)
    return jsonify({"logs": logs}), 200

@units_bp.route('/appliances/add', methods=['POST'])
@token_required
def add_appliance_route():
    data = request.get_json()
    name = data.get('name')
    watts = data.get('watts')
    usage_level = data.get('usage_level')
    quantity = data.get('quantity', 1)
    hours_per_day = data.get('hours_per_day')

    if not name or not watts or not usage_level or not hours_per_day:
        return jsonify({"error": "Name, watts, usage level, and hours are required"}), 400

    if usage_level not in ['Light', 'Average', 'Heavy']:
        return jsonify({"error": "Usage level must be Light, Average, or Heavy"}), 400

    appliance_id, daily_kwh = add_appliance(
        request.user_id, name, watts, hours_per_day, quantity, usage_level
    )
    return jsonify({
        "message": "Appliance added successfully",
        "appliance_id": appliance_id,
        "daily_kwh": daily_kwh
    }), 201

@units_bp.route('/appliances', methods=['GET'])
@token_required
def get_appliances():
    appliances = get_user_appliances(request.user_id)
    total_daily_kwh = get_total_daily_kwh(request.user_id)
    return jsonify({
        "appliances": appliances,
        "total_daily_kwh": total_daily_kwh
    }), 200

@units_bp.route('/appliances/delete/<appliance_id>', methods=['DELETE'])
@token_required
def delete_appliance_route(appliance_id):
    success = delete_appliance(appliance_id, request.user_id)
    if success:
        return jsonify({"message": "Appliance deleted"}), 200
    return jsonify({"error": "Appliance not found"}), 404

@units_bp.route('/appliances/suggestions', methods=['GET'])
def get_suggestions():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify({"suggestions": []}), 200
    matches = [
        a for a in APPLIANCE_DATABASE
        if query in a['name'].lower()
    ]
    return jsonify({"suggestions": matches}), 200