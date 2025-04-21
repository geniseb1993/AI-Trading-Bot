# Environment Variables Security Guide

## Overview

This project uses environment variables to store sensitive configuration data such as API keys. This README provides guidance on how to handle these securely.

## Security Best Practices

1. **Never commit actual API keys to the repository**
   - Use `.env.example` as a template with placeholders
   - Create your own local `.env` file with real credentials
   - The `.gitignore` file is configured to exclude `.env` files from Git

2. **For local development**
   - Copy `.env.example` to `.env`
   - Fill in your own API keys and credentials
   - Keep your `.env` file secure and don't share it

3. **For deployment**
   - Use environment variable features of your hosting platform
   - Consider using a secrets manager for production environments
   - Rotate API keys periodically for better security

## Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/geniseb1993/AI-Trading-Bot.git

# 2. Navigate to the project directory
cd AI-Trading-Bot

# 3. Copy the example environment file
cp .env.example .env

# 4. Edit your .env file with your actual credentials
# DO NOT commit this file!
```

## Required API Keys

The system requires several API keys to function:

- **Polygon API** - For market data (https://polygon.io/)
- **OpenRouter API** - For AI model access (https://openrouter.ai/)
- **Alpaca API** - For trading execution (https://alpaca.markets/)
- **Hume AI** - For advanced AI features (https://hume.ai/)

## Troubleshooting

If you encounter "Cannot find module 'dotenv'" errors, make sure to install the required packages:

```bash
npm install dotenv  # For Node.js
# or
pip install python-dotenv  # For Python
``` 