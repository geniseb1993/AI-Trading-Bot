#!/usr/bin/env python
"""
Dual Bot Quick Test Script
This script runs a quick test of the Dual Bot simulation.
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the dual_bot package
sys.path.append(str(Path(__file__).parent.parent))

# Import the simulation script
from dual_bot.simulate_bot import SimulatedDualBot
from dual_bot.config.config_loader import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dual_bot/logs/quick_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("QuickTest")

def main():
    """Run a quick test of the Dual Bot simulation."""
    logger.info("Starting quick test of Dual Bot simulation...")
    
    # Load configuration in simulation mode
    config = load_config(simulation_mode=True)
    if not config:
        logger.error("Failed to load configuration.")
        return
    
    # Create and run the simulated bot with a shorter duration
    bot = SimulatedDualBot(config)
    bot.run(duration_minutes=5)  # Run for 5 minutes
    
    logger.info("Quick test completed.")

if __name__ == "__main__":
    main() 