#!/bin/bash

echo "Setting up Bitcoin Trading Alert System..."

# Create the cron job to check for Bitcoin signals daily
cat << 'EOF' > bitcoin_cron_setup.js
const cronJob = {
    "name": "Bitcoin Daily Trading Check",
    "schedule": {
        "kind": "every",
        "everyMs": 86400000  // Every 24 hours (in milliseconds)
    },
    "payload": {
        "kind": "agentTurn",
        "message": "Check Bitcoin trading signals and send alerts if BUY or SELL signals are detected",
        "sessionTarget": "isolated"
    },
    "enabled": true
};

// Add the cron job
await cron.add({ job: cronJob });
console.log("Bitcoin trading alert cron job has been added");
EOF

echo "To set up the daily Bitcoin alerts, run:"
echo "node bitcoin_cron_setup.js"
echo ""
echo "Alternatively, you can manually add the cron job using this command in OpenClaw:"
echo ""
echo 'cron.add(job={"name":"Bitcoin Daily Trading Check","schedule":{"kind":"every","everyMs":86400000},"payload":{"kind":"agentTurn","message":"Check Bitcoin trading signals and send alerts if BUY or SELL signals are detected","sessionTarget":"isolated"},"enabled":true})'

echo ""
echo "The system is now ready. You can test it manually by running:"
echo "python3 bitcoin_alert_system.py manual"