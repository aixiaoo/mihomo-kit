#!/usr/bin/env python3
"""utils.py - 工具函数模块"""

import os
import re
import sys
import time
import random
import logging
import functools
from datetime import datetime, timezone, timedelta

# 北京时区
BJ_TZ = timezone(timedelta(hours=8))

# 日志配置
def setup_logging():
    """配置日志输出"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout
    )
    return logging.getLogger('mihomo-kit')

logger = setup_logging()

def get_bj_time():
    """获取北京时间"""
    return datetime.now(BJ_TZ)

def format_bj_time(fmt='%Y-%m-%d %H:%M:%S'):
    """格式化北京时间"""
    return get_bj_time().strftime(fmt)

def read_file(file_path, skip_comments=True):
    """读取文件并返回行列表"""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            if skip_comments:
                lines = [l for l in lines if not l.startswith(('#', '!', '['))]
            return lines
    except Exception as e:
        logger.error(f"读取文件失败 {file_path}: {e}")
        return []

def write_file(file_path, lines):
    """将行列表写入文件"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
    try:
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            for line in lines:
                f.write(line + '\n')
    except Exception as e:
        logger.error(f"写入文件失败 {file_path}: {e}")

def count_lines(file_path):
    """统计文件非空行数"""
    if not os.path.exists(file_path):
        return 0
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                count += 1
    return count

def get_file_size(file_path):
    """获取文件大小 (KB)"""
    if not os.path.exists(file_path):
        return 0.0
    return os.path.getsize(file_path) / 1024

def retry_on_failure(max_retries=3, delay=5, backoff=2):
    """带指数退避的重试装饰器工厂"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait = delay * (backoff ** attempt) + random.uniform(0, 1)
                        logger.warning(f"重试 {attempt + 1}/{max_retries}，{wait:.1f}s 后重试: {e}")
                        time.sleep(wait)
            raise last_exception
        return wrapper
    return decorator
