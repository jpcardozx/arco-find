"""
📝 LOGGING UTILITIES - STRATEGIC MONITORING AND DEBUGGING
Cost-efficient logging with actionable insights
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import sys

def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Setup strategic logger with cost monitoring and actionable formatting
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Simple console formatter
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handler for detailed logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / f"arco_lead_discovery_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

class CostTracker:
    """Track API costs and usage across all operations"""
    
    def __init__(self):
        self.daily_costs = {}
        self.operation_costs = {}
        self.logger = setup_logger(__name__)
    
    def track_operation_cost(self, operation: str, cost: float, details: Dict[str, Any] = None):
        """Track cost for specific operation"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today not in self.daily_costs:
            self.daily_costs[today] = 0.0
        
        if operation not in self.operation_costs:
            self.operation_costs[operation] = []
        
        self.daily_costs[today] += cost
        self.operation_costs[operation].append({
            'timestamp': datetime.utcnow().isoformat(),
            'cost': cost,
            'details': details or {}
        })
        
        self.logger.info(f"💰 Operation '{operation}' cost: ${cost:.4f} (Daily total: ${self.daily_costs[today]:.4f})")
    
    def get_daily_summary(self, date: Optional[str] = None) -> Dict:
        """Get cost summary for specific date"""
        target_date = date or datetime.now().strftime('%Y-%m-%d')
        
        return {
            'date': target_date,
            'total_cost': self.daily_costs.get(target_date, 0.0),
            'operation_breakdown': {
                op: sum(entry['cost'] for entry in entries 
                       if entry['timestamp'].startswith(target_date))
                for op, entries in self.operation_costs.items()
            }
        }

class PerformanceMonitor:
    """Monitor system performance and execution times"""
    
    def __init__(self):
        self.execution_times = {}
        self.logger = setup_logger(__name__)
    
    def start_operation(self, operation_id: str) -> str:
        """Start timing an operation"""
        start_time = datetime.utcnow()
        self.execution_times[operation_id] = {
            'start_time': start_time,
            'operation_id': operation_id
        }
        return operation_id
    
    def end_operation(self, operation_id: str, details: Dict[str, Any] = None) -> Dict:
        """End timing an operation and log results"""
        if operation_id not in self.execution_times:
            self.logger.warning(f"⚠️ Operation {operation_id} not found in timing records")
            return {}
        
        end_time = datetime.utcnow()
        start_time = self.execution_times[operation_id]['start_time']
        duration = (end_time - start_time).total_seconds()
        
        result = {
            'operation_id': operation_id,
            'duration_seconds': duration,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'details': details or {}
        }
        
        # Log with appropriate level based on duration
        if duration > 30:  # Slow operation
            self.logger.warning(f"🐌 Slow operation '{operation_id}': {duration:.2f}s")
        elif duration > 10:  # Moderate operation
            self.logger.info(f"⏱️ Operation '{operation_id}': {duration:.2f}s")
        else:  # Fast operation
            self.logger.debug(f"⚡ Fast operation '{operation_id}': {duration:.2f}s")
        
        # Clean up
        del self.execution_times[operation_id]
        
        return result

# Global instances
cost_tracker = CostTracker()
performance_monitor = PerformanceMonitor()

# Default logger instance
logger = setup_logger(__name__)

def get_system_stats() -> Dict:
    """Get current system performance and cost statistics"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    return {
        'date': today,
        'cost_summary': cost_tracker.get_daily_summary(),
        'active_operations': len(performance_monitor.execution_times),
        'system_status': 'operational'
    }
