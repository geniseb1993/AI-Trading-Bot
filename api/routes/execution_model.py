from flask import Blueprint, jsonify, request
from execution_model.execution_algorithm import ExecutionAlgorithm
from execution_model.config import get_config
from execution_model.risk_manager import RiskManager

execution_bp = Blueprint('execution', __name__)

# Initialize components
config = get_config()
risk_manager = RiskManager(config.get("risk_management"))
execution_algorithm = ExecutionAlgorithm(risk_manager, config)

@execution_bp.route('/cooldown-status', methods=['GET'])
def get_cooldown_status():
    """
    Get the current status of the cooldown timer
    
    Returns:
        JSON: Cooldown status information
    """
    try:
        status = execution_algorithm.get_cooldown_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@execution_bp.route('/trade-setup', methods=['POST'])
def create_trade_setup():
    """
    Create a new trade setup
    
    Returns:
        JSON: Trade setup with execution status
    """
    try:
        data = request.json
        market_data = data.get('market_data', {})
        account_info = data.get('account_info', {})
        trade_setup = data.get('trade_setup', {})
        
        # Execute the trade
        result = execution_algorithm.execute_trade(trade_setup, market_data, account_info)
        
        if result:
            return jsonify({"status": "success", "trade": result}), 200
        else:
            return jsonify({"status": "failed", "reason": "Trade execution failed"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@execution_bp.route('/active-trades', methods=['GET'])
def get_active_trades():
    """
    Get all active trades
    
    Returns:
        JSON: Active trades
    """
    try:
        active_trades = execution_algorithm.get_active_trades()
        return jsonify(active_trades), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@execution_bp.route('/completed-trades', methods=['GET'])
def get_completed_trades():
    """
    Get all completed trades
    
    Returns:
        JSON: Completed trades
    """
    try:
        completed_trades = execution_algorithm.get_completed_trades()
        return jsonify(completed_trades), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500 