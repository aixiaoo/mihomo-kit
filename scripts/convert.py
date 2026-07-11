#!/usr/bin/env python3
"""convert.py - 格式转换模块

支持输出格式:
1. .list  - 纯文本规则（mihomo behavior=domain/ipcidr format=text）
2. .yaml  - mihomo YAML 格式（payload 列表）
3. .mrs   - mihomo 二进制格式（需 mihomo 内核）
"""

import os
import json
import yaml
import subprocess
from utils import logger, read_file, write_file, format_bj_time

def list_to_yaml(input_path, output_path, behavior='domain'):
    """
    将 .list 转换为 mihomo YAML 格式
    
    参数:
        input_path: 输入 .list 文件
        output_path: 输出 .yaml 文件
        behavior: 'domain' 或 'ipcidr'
    """
    rules = read_file(input_path, skip_comments=True)
    
    data = {
        'payload': rules
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    logger.info(f"  [YAML] {os.path.basename(input_path)} -> {os.path.basename(output_path)} ({len(rules)} 条)")
    return len(rules)

def list_to_mrs(input_path, output_path, behavior='domain', mihomo_path='mihomo'):
    """
    将 .list 转换为 mihomo MRS 二进制格式
    
    参数:
        input_path: 输入 .list 文件
        output_path: 输出 .mrs 文件
        behavior: 'domain' 或 'ipcidr'
        mihomo_path: mihomo 内核路径
    
    返回:
        True = 转换成功, False = 转换失败
    """
    # 清洗输入文件（去除注释和空行）
    rules = read_file(input_path, skip_comments=True)
    if not rules:
        logger.warning(f"  [MRS] 跳过空文件: {input_path}")
        return False
    
    # 写入临时清洁文件
    temp_path = input_path + '.clean'
    write_file(temp_path, rules)
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        cmd = [mihomo_path, 'convert-ruleset', behavior, 'text', temp_path, output_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            size_kb = os.path.getsize(output_path) / 1024
            logger.info(f"  [MRS] {os.path.basename(input_path)} -> {os.path.basename(output_path)} ({size_kb:.1f}KB)")
            return True
        else:
            logger.error(f"  [MRS] 转换失败 {input_path}: {result.stderr}")
            return False
    except FileNotFoundError:
        logger.warning(f"  [MRS] mihomo 内核未找到，跳过 MRS 转换")
        return False
    except subprocess.TimeoutExpired:
        logger.error(f"  [MRS] 转换超时: {input_path}")
        return False
    except Exception as e:
        logger.error(f"  [MRS] 转换异常 {input_path}: {e}")
        return False
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def generate_provider_yaml(domain_dir, ip_dir, output_path, base_url=None):
    """
    生成 mihomo rule-providers 配置 YAML
    
    参数:
        domain_dir: 域名规则目录
        ip_dir: IP 规则目录
        output_path: 输出文件路径
        base_url: 规则文件的基 URL（如 https://raw.githubusercontent.com/user/repo/main/）
    """
    providers = {}
    
    # 处理域名规则
    if os.path.exists(domain_dir):
        for f in sorted(os.listdir(domain_dir)):
            if not f.endswith('.list'):
                continue
            name = f.replace('.list', '')
            key = name.replace('-', '_').replace('@', '_at_')
            
            entry = {
                'type': 'http',
                'behavior': 'domain',
                'format': 'text',
            }
            if base_url:
                entry['url'] = f"{base_url}/output/domain/{f}"
            entry['path'] = f"./ruleset/{f}"
            entry['interval'] = 86400
            
            providers[key] = entry
    
    # 处理 IP 规则
    if os.path.exists(ip_dir):
        for f in sorted(os.listdir(ip_dir)):
            if not f.endswith('.list'):
                continue
            name = f.replace('.list', '')
            key = name.replace('-', '_') + '_ip'
            
            entry = {
                'type': 'http',
                'behavior': 'ipcidr',
                'format': 'text',
            }
            if base_url:
                entry['url'] = f"{base_url}/output/ip/{f}"
            entry['path'] = f"./ruleset/{f}"
            entry['interval'] = 86400
            
            providers[key] = entry
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# mihomo-kit rule-providers (Generated at {format_bj_time()})\n")
        yaml.dump({'rule-providers': providers}, f, default_flow_style=False, allow_unicode=True, sort_keys=True)
    
    logger.info(f"  [Provider] 生成 rule-providers 配置: {output_path} ({len(providers)} 个提供者)")
    return providers

def convert_directory(list_dir, yaml_dir, mrs_dir, rule_type, mihomo_path='mihomo'):
    """
    转换目录下所有 .list 文件为 YAML 和 MRS 格式
    
    参数:
        list_dir: .list 文件目录
        yaml_dir: YAML 输出目录
        mrs_dir: MRS 输出目录
        rule_type: 'domain' 或 'ip'
        mihomo_path: mihomo 内核路径
    """
    if not os.path.exists(list_dir):
        return
    
    behavior = 'domain' if rule_type == 'domain' else 'ipcidr'
    
    os.makedirs(yaml_dir, exist_ok=True)
    os.makedirs(mrs_dir, exist_ok=True)
    
    for f in sorted(os.listdir(list_dir)):
        if not f.endswith('.list'):
            continue
        
        list_path = os.path.join(list_dir, f)
        yaml_path = os.path.join(yaml_dir, f.replace('.list', '.yaml'))
        mrs_path = os.path.join(mrs_dir, f.replace('.list', '.mrs'))
        
        # 转换为 YAML
        list_to_yaml(list_path, yaml_path, behavior)
        
        # 转换为 MRS
        list_to_mrs(list_path, mrs_path, behavior, mihomo_path)

def generate_stats(domain_dir, ip_dir, mrs_dir=None):
    """生成规则统计信息"""
    stats = {'domain': {}, 'ip': {}, 'total_rules': 0, 'total_mrs_size_kb': 0.0}
    
    for rule_type, directory in [('domain', domain_dir), ('ip', ip_dir)]:
        if not os.path.exists(directory):
            continue
        for f in sorted(os.listdir(directory)):
            if not f.endswith('.list'):
                continue
            name = f.replace('.list', '')
            path = os.path.join(directory, f)
            count = sum(1 for line in open(path, 'r', encoding='utf-8') if line.strip())
            stats[rule_type][name] = count
            stats['total_rules'] += count
    
    # MRS 文件大小统计
    if mrs_dir and os.path.exists(mrs_dir):
        total_size = 0
        for root, dirs, files in os.walk(mrs_dir):
            for f in files:
                if f.endswith('.mrs'):
                    total_size += os.path.getsize(os.path.join(root, f))
        stats['total_mrs_size_kb'] = total_size / 1024
    
    return stats
