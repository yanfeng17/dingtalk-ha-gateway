#!/usr/bin/with-contenv bashio

# Read configuration from Home Assistant addon options
bashio::log.info "Loading DingTalk Gateway configuration..."

export DINGTALK_CLIENT_ID=$(bashio::config 'dingtalk_client_id')
export DINGTALK_CLIENT_SECRET=$(bashio::config 'dingtalk_client_secret')
export DINGTALK_AGENT_ID=$(bashio::config 'dingtalk_agent_id')
export DINGTALK_USE_STREAM=$(bashio::config 'use_stream')

# Optional configurations with defaults
if bashio::config.has_value 'gateway_token'; then
    export GATEWAY_TOKEN=$(bashio::config 'gateway_token')
fi

if bashio::config.has_value 'webhook_secret'; then
    export DINGTALK_WEBHOOK_SECRET=$(bashio::config 'webhook_secret')
fi

# Fixed settings for addon environment
export GATEWAY_HOST=0.0.0.0
export GATEWAY_PORT=8099
export CHANNEL_TYPE=dingtalk

# Validate required configuration
if [ -z "$DINGTALK_CLIENT_ID" ]; then
    bashio::exit.nok "DingTalk Client ID is required!"
fi

if [ -z "$DINGTALK_CLIENT_SECRET" ]; then
    bashio::exit.nok "DingTalk Client Secret is required!"
fi

if [ -z "$DINGTALK_AGENT_ID" ]; then
    bashio::exit.nok "DingTalk Agent ID is required!"
fi

bashio::log.info "Starting DingTalk Gateway..."
bashio::log.info "Stream mode: ${DINGTALK_USE_STREAM}"
bashio::log.info "Client ID: ${DINGTALK_CLIENT_ID:0:10}..."
bashio::log.info "Agent ID: ${DINGTALK_AGENT_ID}"

cd /app
exec python3 app.py
