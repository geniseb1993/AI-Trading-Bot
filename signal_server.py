from flask import Flask, jsonify
from flask_cors import CORS
import os
import pandas as pd
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint to verify server is running"""
    return jsonify({
        'success': True,
        'message': 'Signal API server is running'
    })

@app.route('/api/get-saved-signals', methods=['GET'])
def get_saved_signals():
    """Get saved buy and short signals"""
    try:
        # Check both the current directory and data directory
        data_dir = os.path.join(os.getcwd(), 'data')
        buy_file = os.path.join(data_dir, 'buy_signals.csv')
        short_file = os.path.join(data_dir, 'short_signals.csv')
        
        if os.path.exists(buy_file) and os.path.exists(short_file):
            logger.info(f"Reading signal files from: {buy_file} and {short_file}")
            buy_signals = pd.read_csv(buy_file)
            short_signals = pd.read_csv(short_file)
            
            logger.info(f"Found {len(buy_signals)} buy signals and {len(short_signals)} short signals")
            
            return jsonify({
                'success': True,
                'buy_signals': buy_signals.to_dict('records'),
                'short_signals': short_signals.to_dict('records')
            })
        else:
            # Return error
            logger.warning(f"Signal files not found at {buy_file} and {short_file}")
            return jsonify({
                'success': False,
                'error': 'Signal files not found'
            }), 404
    except Exception as e:
        logger.error(f"Error in get-saved-signals: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/refresh-signals', methods=['GET'])
def refresh_signals():
    """Run the generate_signals.py script to refresh signal data"""
    try:
        import subprocess
        
        logger.info("Running generate_signals.py to refresh signal data")
        result = subprocess.run(['python', 'generate_signals.py'], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Successfully refreshed signal data")
            return jsonify({
                'success': True,
                'message': 'Signal data refreshed successfully',
                'output': result.stdout
            })
        else:
            logger.error(f"Error refreshing signal data: {result.stderr}")
            return jsonify({
                'success': False,
                'error': 'Failed to refresh signal data',
                'output': result.stderr
            }), 500
    except Exception as e:
        logger.error(f"Error in refresh-signals: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = 5678  # Use a specific port for this API
    logger.info(f"Starting Signal API server on port {port}")
    logger.info(f"API endpoints:")
    logger.info(f" - Test endpoint: http://localhost:{port}/api/test")
    logger.info(f" - Signals endpoint: http://localhost:{port}/api/get-saved-signals")
    logger.info(f" - Refresh signals: http://localhost:{port}/api/refresh-signals")
    
    app.run(host='0.0.0.0', port=port, debug=True) 