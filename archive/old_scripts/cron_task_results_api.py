"""
定时任务结果API
用于查询和管理定时任务的执行结果
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from app.models.cron_task_result import CronTaskResult
from app import db

bp = Blueprint('cron_task_results', __name__)


@bp.route('/cron-results', methods=['GET'])
def get_cron_results():
    """
    获取定时任务结果列表
    支持按任务类型过滤和分页
    """
    try:
        task_type = request.args.get('task_type')
        limit = request.args.get('limit', 30, type=int)
        
        query = CronTaskResult.query
        
        if task_type:
            query = query.filter_by(task_type=task_type)
        
        results = query.order_by(
            CronTaskResult.execution_date.desc()
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [r.to_dict(include_data=False) for r in results]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/cron-results/latest', methods=['GET'])
def get_latest_results():
    """
    获取各类任务的最新结果
    用于任务监控页面展示
    """
    try:
        # 获取所有任务类型
        task_types = CronTaskResult.get_all_task_types()
        
        if not task_types:
            return jsonify({
                'success': True,
                'data': [],
                'message': '暂无任务结果数据'
            })
        
        # 获取每种类型的最新结果
        latest_results = []
        for task_type in task_types:
            result = CronTaskResult.get_latest_by_type(task_type)
            if result:
                latest_results.append(result.to_dict(include_data=True))
        
        # 按执行时间排序
        latest_results.sort(
            key=lambda x: x.get('execution_time', ''), 
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'data': latest_results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/cron-results/<int:result_id>', methods=['GET'])
def get_result_detail(result_id):
    """
    获取单个任务结果的详细信息
    """
    try:
        result = CronTaskResult.query.get(result_id)
        if not result:
            return jsonify({
                'success': False,
                'error': '结果不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': result.to_dict(include_data=True)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/cron-results/by-type/<task_type>', methods=['GET'])
def get_results_by_type(task_type):
    """
    获取指定类型的任务结果历史
    """
    try:
        limit = request.args.get('limit', 30, type=int)
        
        results = CronTaskResult.get_results_by_type(task_type, limit=limit)
        
        return jsonify({
            'success': True,
            'data': [r.to_dict(include_data=True) for r in results],
            'task_type': task_type
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/cron-results/task-types', methods=['GET'])
def get_task_types():
    """
    获取所有任务类型列表
    """
    try:
        task_types = CronTaskResult.get_all_task_types()
        
        # 获取每个类型的最新结果用于展示
        type_info = []
        for task_type in task_types:
            latest = CronTaskResult.get_latest_by_type(task_type)
            if latest:
                type_info.append({
                    'task_type': task_type,
                    'task_name': latest.task_name,
                    'last_execution': latest.execution_time.isoformat() if latest.execution_time else None,
                    'last_status': latest.status
                })
        
        return jsonify({
            'success': True,
            'data': type_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/cron-results', methods=['POST'])
def create_result():
    """
    创建或更新任务结果
    供定时任务调用
    """
    try:
        data = request.get_json()
        
        required_fields = ['task_type', 'task_name', 'execution_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'缺少必填字段: {field}'
                }), 400
        
        # 解析日期
        execution_date = datetime.strptime(
            data['execution_date'], 
            '%Y-%m-%d'
        ).date()
        
        result = CronTaskResult.save_result(
            task_type=data['task_type'],
            task_name=data['task_name'],
            execution_date=execution_date,
            result_data=data.get('result_data'),
            status=data.get('status', 'success'),
            result_summary=data.get('result_summary'),
            error_message=data.get('error_message'),
            items_processed=data.get('items_processed', 0),
            items_succeeded=data.get('items_succeeded', 0),
            items_failed=data.get('items_failed', 0),
            duration_seconds=data.get('duration_seconds'),
            meta_info=data.get('meta_info')
        )
        
        return jsonify({
            'success': True,
            'data': result.to_dict(include_data=False),
            'message': '结果保存成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
