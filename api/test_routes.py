#!/usr/bin/env python
"""Test script to verify the institutional flow routes are registered correctly."""

from flask import Flask
try:
    from market_analysis_routes import bp
    
    app = Flask(__name__)
    app.register_blueprint(bp)
    
    print('Routes registered successfully')
    print('Available routes:')
    for rule in app.url_map.iter_rules():
        if 'institutional-flow' in str(rule):
            print(f'Route: {rule}')
            print(f'Endpoint: {rule.endpoint}')
            print(f'Methods: {rule.methods}')
            print('---')
    
except Exception as e:
    print(f"Error loading routes: {str(e)}") 