#!/usr/bin/env python3
"""
ARCO-FIND Configuration with ngrok tunnel
Configuration file for development with ngrok proxy
"""

import os

# Current ngrok tunnel configuration (updated automatically)
NGROK_CONFIG = {
    'public_url': 'https://d20097e520ec.ngrok-free.app',
    'local_port': 8081,
    'tunnel_name': 'command_line',
    'created_at': '2025-09-17'
}

# API Base URLs using ngrok
API_ENDPOINTS = {
    'base_url': NGROK_CONFIG['public_url'],
    'api_base': f"{NGROK_CONFIG['public_url']}/api",
    'webhook_url': f"{NGROK_CONFIG['public_url']}/webhook",
    'health_check': f"{NGROK_CONFIG['public_url']}/health",
    'status': f"{NGROK_CONFIG['public_url']}/status"
}

# Environment configuration
ENVIRONMENT = {
    'mode': 'development',
    'debug': True,
    'use_ngrok': True,
    'local_fallback': 'http://localhost:8081'
}

def get_api_url(endpoint: str = '') -> str:
    """Get full API URL with ngrok tunnel"""
    base = API_ENDPOINTS['api_base']
    return f"{base}/{endpoint.lstrip('/')}" if endpoint else base

def get_webhook_url() -> str:
    """Get webhook URL for external services"""
    return API_ENDPOINTS['webhook_url']

def get_base_url() -> str:
    """Get base application URL"""
    return API_ENDPOINTS['base_url']

if __name__ == "__main__":
    print("🔗 ARCO-FIND ngrok Configuration")
    print("=" * 40)
    print(f"Public URL: {NGROK_CONFIG['public_url']}")
    print(f"Local Port: {NGROK_CONFIG['local_port']}")
    print(f"API Base: {API_ENDPOINTS['api_base']}")
    print(f"Webhook: {API_ENDPOINTS['webhook_url']}")
    print("=" * 40)