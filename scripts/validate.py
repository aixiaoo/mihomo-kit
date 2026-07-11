#!/usr/bin/env python3
"""validate.py - 失效规则检测模块

功能:
1. 格式验证 - 检测并移除格式错误的规则
2. 失效域名检测 - 通过 DNS 查询检测不可解析的域名
3. 上游 URL 可用性检测 - 检测永久失效的上游源
"""

import os
import re
import socket
import ipaddress
import concurrent.futures
from utils import logger, read_file, write_file

# 域名格式正则
DOMAIN_PATTERN = re.compile(
    r'^(?:'
    r'\+\..+'          # +.example.com
    r'|\*\..+'         # *.example.com  
    r'|[a-zA-Z0-9]'    # example.com (必须以字母数字开头)
    r'(?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?'  # 中间可以有连字符
    r'(?:\.[a-zA-Z0-9\-]*[a-zA-Z0-9])+'
    r')$'
)

# IP CIDR 正则
IP_CIDR_PATTERN = re.compile(
    r'^'
    r'(?:'
    r'(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?'  # IPv4
    r'|'
    r'[0-9a-fA-F:]+(?:/\d{1,3})?'             # IPv6
    r')$'
)

def validate_domain_rule(rule):
    """验证单条域名规则格式是否正确"""
    rule = rule.strip()
    if not rule:
        return False
    # 跳过 GEOSITE/GEOIP 等特殊规则
    if rule.startswith(('GEOSITE:', 'GEOIP:', 'PROCESS-NAME:', 'MATCH', 'DIRECT', 'REJECT')):
        return True
    # 跳过 DOMAIN-SUFFIX/DOMAIN-KEYWORD 等格式
    if rule.startswith(('DOMAIN-SUFFIX,', 'DOMAIN-KEYWORD,', 'DOMAIN,')):
        return True
    return bool(DOMAIN_PATTERN.match(rule))

def validate_ip_rule(rule):
    """验证单条 IP CIDR 规则格式是否正确"""
    rule = rule.strip()
    if not rule:
        return False
    if rule.startswith(('GEOIP:', 'PROCESS-NAME:')):
        return True
    try:
        ipaddress.ip_network(rule, strict=False)
        return True
    except ValueError:
        return False

def remove_malformed_rules(input_path, rule_type):
    """
    移除格式错误的规则
    
    参数:
        input_path: 规则文件路径
        rule_type: 'domain' 或 'ip'
    
    返回:
        (原始数量, 保留数量, 移除数量)
    """
    rules = read_file(input_path, skip_comments=True)
    original_count = len(rules)
    
    if rule_type == 'domain':
        valid_rules = [r for r in rules if validate_domain_rule(r)]
    else:
        valid_rules = [r for r in rules if validate_ip_rule(r)]
    
    removed = original_count - len(valid_rules)
    if removed > 0:
        logger.info(f"  [格式验证] {os.path.basename(input_path)}: 移除 {removed} 条格式错误规则")
        write_file(input_path, valid_rules)
    
    return original_count, len(valid_rules), removed

def check_domain_dns(domain, timeout=3):
    """
    DNS 检测域名是否可解析
    
    返回:
        True = 可解析（存活）
        False = 不可解析（可能失效）
    """
    # 去除前缀
    if domain.startswith('+.'):
        domain = domain[2:]
    elif domain.startswith('*.'):
        domain = domain[2:]
    
    try:
        socket.setdefaulttimeout(timeout)
        socket.getaddrinfo(domain, None)
        return True
    except socket.gaierror:
        return False
    except socket.timeout:
        return False
    except Exception:
        return True  # 未知错误，保守处理（认为存活）

def detect_dead_domains(input_path, max_workers=50, timeout=3, sample_ratio=1.0):
    """
    并发检测失效域名
    
    参数:
        input_path: 规则文件路径
        max_workers: 最大并发数
        timeout: DNS 超时秒数
        sample_ratio: 采样比例 (0.0-1.0)，1.0 = 全量检测
    
    返回:
        (检测数量, 失效数量, 失效域名列表)
    """
    rules = read_file(input_path, skip_comments=True)
    
    # 采样
    import random
    if sample_ratio < 1.0:
        sample_size = max(1, int(len(rules) * sample_ratio))
        rules = random.sample(rules, sample_size)
    
    total = len(rules)
    if total == 0:
        return 0, 0, []
    
    logger.info(f"  [DNS检测] 开始检测 {total} 个域名（并发={max_workers}, 超时={timeout}s）")
    
    dead_domains = []
    checked = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_domain = {
            executor.submit(check_domain_dns, domain, timeout): domain 
            for domain in rules
        }
        
        for future in concurrent.futures.as_completed(future_to_domain):
            domain = future_to_domain[future]
            checked += 1
            try:
                alive = future.result()
                if not alive:
                    dead_domains.append(domain)
            except Exception:
                pass
            
            if checked % 100 == 0:
                logger.info(f"  [DNS检测] 进度: {checked}/{total}, 失效: {len(dead_domains)}")
    
    logger.info(f"  [DNS检测] 完成: 检测 {total} 个域名, 失效 {len(dead_domains)} 个")
    return total, len(dead_domains), dead_domains

def remove_dead_domains(input_path, dead_list, max_workers=50, timeout=3, sample_ratio=1.0):
    """
    检测并移除失效域名
    
    参数:
        input_path: 规则文件路径
        dead_list: 失效域名输出路径（记录失效域名）
        其他参数同 detect_dead_domains
    """
    total, dead_count, dead_domains = detect_dead_domains(
        input_path, max_workers, timeout, sample_ratio
    )
    
    if dead_count > 0:
        rules = read_file(input_path, skip_comments=True)
        dead_set = set(dead_domains)
        # 移除失效域名（包括其变体形式）
        clean_rules = []
        for r in rules:
            base = r
            if base.startswith('+.'):
                base = base[2:]
            elif base.startswith('*.'):
                base = base[2:]
            if base in dead_set or r in dead_set:
                continue
            clean_rules.append(r)
        
        write_file(input_path, clean_rules)
        write_file(dead_list, dead_domains)
        logger.info(f"  [失效移除] {os.path.basename(input_path)}: 移除 {dead_count} 个失效域名")
    
    return total, dead_count

def validate_file(input_path, rule_type, dns_check=False, sample_ratio=1.0):
    """
    验证单个规则文件
    
    参数:
        input_path: 规则文件路径
        rule_type: 'domain' 或 'ip'
        dns_check: 是否启用 DNS 检测
        sample_ratio: DNS 检测采样比例
    """
    # 1. 格式验证
    orig, kept, removed = remove_malformed_rules(input_path, rule_type)
    
    # 2. DNS 失效检测（仅域名规则）
    if dns_check and rule_type == 'domain':
        dead_list = input_path.replace('.list', '.dead.list')
        total, dead_count = remove_dead_domains(
            input_path, dead_list, 
            max_workers=50, timeout=3, 
            sample_ratio=sample_ratio
        )
        return {'original': orig, 'valid': kept, 'malformed_removed': removed,
                'dns_checked': total, 'dead_removed': dead_count}
    
    return {'original': orig, 'valid': kept, 'malformed_removed': removed}
