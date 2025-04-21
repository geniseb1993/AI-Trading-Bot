from flask import Flask, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/api/health')
def health_check():
    logger.info("Health check endpoint called")
    return jsonify({'status': 'healthy', 'service': 'Test API'})

if __name__ == '__main__':
    try:
        logger.info("Starting test server...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}") 