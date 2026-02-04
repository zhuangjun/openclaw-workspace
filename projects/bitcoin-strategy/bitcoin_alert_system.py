#!/usr/bin/env python3
"""
Bitcoin Trading Alert System
This script integrates with OpenClaw to check Bitcoin trading signals daily
and send alerts when buy/sell opportunities arise.
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from bitcoin_strategy import BitcoinTradingStrategy, check_daily_signals

def send_openclaw_message(message, channel=None):
    """
    Send a message through OpenClaw's message system
    """
    try:
        cmd = [
            "node", "-e",
            f"""
            const {{ spawn }} = require('child_process');
            const messageData = {{
                action: 'send',
                message: {json.dumps(message)},
            }};
            if ('{channel}' !== 'None') {{
                messageData.channel = '{channel}';
            }}
            
            // We'll save the message to a file that can be processed by OpenClaw
            const fs = require('fs');
            const logEntry = {{
                timestamp: new Date().toISOString(),
                type: 'bitcoin_alert',
                message: messageData.message,
                channel: messageData.channel || 'default'
            }};
            fs.appendFileSync('bitcoin_alerts.log', JSON.stringify(logEntry) + '\\n');
            console.log('Alert logged successfully');
            """
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def run_daily_check():
    """
    Execute the daily Bitcoin signal check and send alerts if needed
    """
    print(f"Running daily Bitcoin check at {datetime.now()}")
    
    try:
        alert_result = check_daily_signals()
        
        # Always log the daily check
        daily_log = {
            'timestamp': datetime.now().isoformat(),
            'type': 'daily_check',
            'summary': alert_result[:100] + '...' if len(alert_result) > 100 else alert_result
        }
        
        with open('bitcoin_daily_checks.log', 'a') as f:
            f.write(json.dumps(daily_log) + '\n')
        
        # Check if this is an actual alert (not just an overview)
        if '🚨' in alert_result or 'BUY' in alert_result or 'SELL' in alert_result:
            print("ALERT DETECTED - Sending notification")
            print(alert_result)
            send_openclaw_message(alert_result)
            
            # Log the alert separately
            alert_log = {
                'timestamp': datetime.now().isoformat(),
                'type': 'trading_alert',
                'alert': alert_result
            }
            
            with open('bitcoin_trading_alerts.log', 'a') as f:
                f.write(json.dumps(alert_log) + '\n')
                
            return alert_result
        else:
            print("No trading alerts today")
            print(alert_result)
            return "Daily check completed - no alerts"
            
    except Exception as e:
        error_msg = f"Error during daily Bitcoin check: {str(e)}"
        print(error_msg)
        
        error_log = {
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'error': error_msg
        }
        
        with open('bitcoin_errors.log', 'a') as f:
            f.write(json.dumps(error_log) + '\n')
            
        return error_msg

def setup_cron_job():
    """
    Set up a cron job to run the daily Bitcoin check
    This function generates the necessary OpenClaw cron command
    """
    cron_job = {
        "name": "Bitcoin Daily Trading Check",
        "schedule": {
            "kind": "every",
            "everyMs": 86400000  # Every 24 hours (in milliseconds)
        },
        "payload": {
            "kind": "agentTurn",
            "message": "Check Bitcoin trading signals and send alerts if BUY or SELL signals are detected",
            "sessionTarget": "isolated"
        },
        "enabled": True
    }
    
    print("To set up the daily Bitcoin alert system, run this OpenClaw command:")
    print(f"\ncron.add(job={json.dumps(cron_job, indent=2)})\n")
    
    # Also save to a config file
    with open('bitcoin_cron_config.json', 'w') as f:
        json.dump(cron_job, f, indent=2)
    
    print("Cron configuration saved to bitcoin_cron_config.json")

def manual_check():
    """
    Manual function to test the alert system
    """
    print("Running manual Bitcoin signal check...")
    result = run_daily_check()
    print(f"\nResult: {result}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            setup_cron_job()
        elif sys.argv[1] == "manual":
            manual_check()
        elif sys.argv[1] == "test":
            # Quick test of the strategy
            from bitcoin_strategy import BitcoinTradingStrategy
            strategy = BitcoinTradingStrategy()
            analysis = strategy.analyze_market()
            print("Test analysis:", json.dumps(analysis, indent=2, default=str))
        else:
            print("Usage: python bitcoin_alert_system.py [setup|manual|test]")
    else:
        # Run the daily check by default
        run_daily_check()