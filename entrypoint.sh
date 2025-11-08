#!/bin/sh

# This script runs inside the container
# It checks if a config file exists. If not, it creates one.

CONFIG_FILE="firewall_config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "--- No $CONFIG_FILE found, creating one... ---"
  python main.py --create-config
  echo "--- Default config file created. ---"
else
  echo "--- Using existing $CONFIG_FILE. ---"
fi
echo "--- Starting firewall... ---"
exec "$@"