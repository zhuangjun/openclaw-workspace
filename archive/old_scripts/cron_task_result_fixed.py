"""
定时任务结果数据模型
用于保存各类投资定时任务的执行结果
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from app import db


class CronTaskResult(db.Model):
    """定时任务结果表"""
    __tablename__ = 'cron_task_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 任务标识
    task_type = Column(String(50), nullable=False, index=True)
    task_name = Column(String(100), nullable=False)
    
    # 执行信息
    execution_date = Column(DateTime, nullable=False, index=True)
    execution_time = Column(DateTime, default=datetime.utcnow)
    
    # 状态
    status = Column(String(20), default='success')
    
    # 结果内容
    result_summary = Column(Text)
    result_data = Column(JSON)
    error_message = Column(Text)
    
    # 统计信息
    items_processed = Column(Integer, default=0)
    items_succeeded = Column(Integer, default=0)
    items_failed = Column(Integer, default=0)
    
    # 执行耗时（秒）
    duration_seconds = Column(Integer)
    
    # 额外元数据
    meta_info = Column(JSON)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 复合索引：按任务类型和日期查询
    __table_args__ = (
        Index('idx_task_type_date', 'task_type', 'execution_date'),
    )

    def __repr__(self):
        return f'<CronTaskResult {self.task_type}: {self.execution_date}>'

    def to_dict(self, include_data=True):
        """转换为字典格式"""
        result = {
            'id': self.id,
            'task_type': self.task_type,
            'task_name': self.task_name,
            'execution_date': self.execution_date.strftime('%Y-%m-%d') if self.execution_date else None,
            'execution_time': self.execution_time.isoformat() if self.execution_time else None,
            'status': self.status,
            'result_summary': self.result_summary,
            'error_message': self.error_message,
            'items_processed': self.items_processed,
            'items_succeeded': self.items_succeeded,
            'items_failed': self.items_failed,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_data:
            result['result_data'] = self.result_data
            result['meta_info'] = self.meta_info
        return result

    @classmethod
    def get_latest_by_type(cls, task_type):
        """获取某类型的最新结果"""
        return cls.query.filter_by(task_type=task_type)\
            .order_by(cls.execution_date.desc(), cls.execution_time.desc())\
            .first()

    @classmethod
    def get_results_by_type(cls, task_type, limit=30):
        """获取某类型的历史结果"""
        return cls.query.filter_by(task_type=task_type)\
            .order_by(cls.execution_date.desc())\
            .limit(limit)\
            .all()

    @classmethod
    def save_result(cls, task_type, task_name, execution_date, result_data, 
                    status='success', result_summary=None, error_message=None,
                    items_processed=0, items_succeeded=0, items_failed=0,
                    duration_seconds=None, meta_info=None):
        """保存任务结果"""
        # 检查是否已存在同类型同日期的记录
        existing = cls.query.filter_by(
            task_type=task_type,
            execution_date=execution_date
        ).first()
        
        if existing:
            # 更新现有记录
            existing.task_name = task_name
            existing.execution_time = datetime.utcnow()
            existing.status = status
            existing.result_data = result_data
            existing.result_summary = result_summary
            existing.error_message = error_message
            existing.items_processed = items_processed
            existing.items_succeeded = items_succeeded
            existing.items_failed = items_failed
            existing.duration_seconds = duration_seconds
            existing.meta_info = meta_info
            existing.updated_at = datetime.utcnow()
            db.session.commit()
            return existing
        else:
            # 创建新记录
            result = cls(
                task_type=task_type,
                task_name=task_name,
                execution_date=execution_date,
                execution_time=datetime.utcnow(),
                status=status,
                result_data=result_data,
                result_summary=result_summary,
                error_message=error_message,
                items_processed=items_processed,
                items_succeeded=items_succeeded,
                items_failed=items_failed,
                duration_seconds=duration_seconds,
                meta_info=meta_info
            )
            db.session.add(result)
            db.session.commit()
            return result

    @classmethod
    def get_all_task_types(cls):
        """获取所有任务类型列表"""
        from sqlalchemy import distinct
        types = db.session.query(distinct(cls.task_type)).all()
        return [t[0] for t in types]
