#!/usr/bin/env python3
"""fetch.py - 上游规则拉取与解析模块"""

import os
import re
import requests
import yaml
from utils import logger, retry_on_failure

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/plain, application/yaml, application/octet-stream, */*',
}

# 会话池（复用连接）
_session = None

def get_session():
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update(HEADERS)
    return _session

@retry_on_failure(max_retries=3, delay=3, backoff=2)
def _download(url):
    """下载 URL 内容"""
    session = get_session()
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.text

def fetch_and_parse(target, fmt, output_dir, project_root=None):
    """
    智能获取并解析规则
    
    参数:
        target: URL / 本地路径 / 内联规则
        fmt: 'list' / 'yaml' / 'inline'
        output_dir: 已生成规则的输出目录（用于引用其他已生成的 list）
        project_root: 项目根目录
    
    返回:
        set of 规则字符串
    """
    # 1. 嗅探内联多项规则: '+.cn','www.baidu.com'
    if ',' in target and ("'" in target or '"' in target):
        items = re.findall(r"['\"]([^'\"]+)['\"]", target)
        if items:
            logger.info(f"  [内联] 获取多项规则: {len(items)} 条")
            return set(items)

    # 2. 嗅探单条内联规则: '+.cn'
    if target.startswith(("'", '"')) and target.endswith(("'", '"')):
        rule = target.strip("'\" ")
        logger.info(f"  [内联] 获取单条规则: {rule}")
        return {rule} if rule else set()

    content = ""
    
    # 3. 嗅探网络直链
    if target.startswith('http://') or target.startswith('https://'):
        try:
            content = _download(target)
            logger.info(f"  [网络] 下载成功: {target[:80]}...")
        except Exception as e:
            logger.error(f"  [网络] 下载失败 {target}: {e}")
            return set()
    # 4. 嗅探本地路径
    else:
        clean_target = target.lstrip('/')
        
        # 尝试绝对路径
        if project_root and os.path.exists(os.path.join(project_root, clean_target)):
            local_path = os.path.join(project_root, clean_target)
        elif os.path.exists(clean_target):
            local_path = clean_target
        # 尝试相对于输出目录
        elif os.path.exists(os.path.join(output_dir, target)):
            local_path = os.path.join(output_dir, target)
        elif project_root and os.path.exists(os.path.join(project_root, target)):
            local_path = os.path.join(project_root, target)
        else:
            # 尝试去掉前导斜杠后在项目根下查找
            local_path = os.path.join(project_root or '.', clean_target)
            if not os.path.exists(local_path):
                logger.error(f"  [本地] 文件不存在: {target}")
                return set()
        
        try:
            with open(local_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"  [本地] 读取成功: {local_path}")
        except Exception as e:
            logger.error(f"  [本地] 读取失败 {local_path}: {e}")
            return set()

    # 解析内容
    return parse_content(content, fmt)

def parse_content(content, fmt):
    """根据格式解析规则内容"""
    result = set()
    
    if fmt == 'yaml':
        try:
            data = yaml.safe_load(content)
            if data and isinstance(data, dict) and 'payload' in data:
                for item in data['payload']:
                    item_str = str(item).strip("'\" ")
                    if item_str and not item_str.startswith('#'):
                        result.add(item_str)
            elif data and isinstance(data, list):
                for item in data:
                    item_str = str(item).strip("'\" ")
                    if item_str and not item_str.startswith('#'):
                        result.add(item_str)
        except Exception as e:
            logger.error(f"  [YAML] 解析异常: {e}")
            # 尝试当 list 格式解析
            for line in content.splitlines():
                clean_line = line.split('#')[0].strip("'\" ")
                if clean_line:
                    result.add(clean_line)
    
    elif fmt == 'list':
        for line in content.splitlines():
            clean_line = line.split('#')[0].strip("'\" ")
            if clean_line and not clean_line.startswith('!'):
                result.add(clean_line)
    
    elif fmt == 'inline':
        # 内联模式：直接把整个内容当规则
        for line in content.splitlines():
            clean_line = line.strip("'\" ")
            if clean_line and not clean_line.startswith('#'):
                result.add(clean_line)
    
    return result
