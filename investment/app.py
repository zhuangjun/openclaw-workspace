from flask import Flask
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# 数据库路径
DB_PATH = os.environ.get('FRIDAY_DB_PATH', '/home/ubuntu/friday/friday.db')

# 注册路由
from routes.tasks import tasks_bp
from routes.portfolio import portfolio_bp
from routes.reports import reports_bp

app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
app.register_blueprint(reports_bp, url_prefix='/api/reports')

# 向后兼容的旧路由
from routes.tasks import get_latest_morning_report, get_morning_report_history
from routes.tasks import get_latest_davies, get_davies_history
from routes.tasks import get_latest_bitcoin, get_bitcoin_history

app.add_url_rule('/api/morning-report/latest', 'morning_report_latest', get_latest_morning_report)
app.add_url_rule('/api/morning-report/history', 'morning_report_history', get_morning_report_history)
app.add_url_rule('/api/davies/latest', 'davies_latest', get_latest_davies)
app.add_url_rule('/api/davies/history', 'davies_history', get_davies_history)
app.add_url_rule('/api/bitcoin/latest', 'bitcoin_latest', get_latest_bitcoin)
app.add_url_rule('/api/bitcoin/history', 'bitcoin_history', get_bitcoin_history)

@app.route('/api/health')
def health_check():
    return {
        'status': 'ok',
        'time': datetime.now().isoformat(),
        'service': 'Friday Investment API',
        'version': '2.0'
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)