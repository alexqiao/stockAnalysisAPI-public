#!/usr/bin/env python3
"""
手动触发股票分析任务，用于测试报告生成功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.daily_tasks import DailyReportScheduler
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """手动运行股票分析"""
    logger.info("Starting manual stock analysis...")
    
    # 创建调度器实例
    scheduler = DailyReportScheduler()
    
    try:
        # 手动运行股票分析任务
        scheduler.run_daily_stock_analysis()
        logger.info("Manual stock analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during manual analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
