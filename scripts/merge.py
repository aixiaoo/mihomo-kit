#!/usr/bin/env python3
"""merge.py - 合并去重模块 (Trie 树 + IP CIDR collapse)

配方格式:
  + list/yaml <url|path|inline>   -> 添加源
  - list/yaml <url|path|inline>   -> 排除源
  + list [                       -> 块级子计算开始
    + list <url>
    - list <url>
  ]                              -> 块级子计算结束

支持本地 .list 文件引用（如 proxy.list 引用 ads.list），按依赖顺序编译。
"""

import os
import re
import ipaddress
import yaml
from utils import logger
from fetch import fetch_and_parse

# ================= 域名结构定义 =================

class DomainRule:
    """域名规则对象"""
    def __init__(self, raw):
        self.raw = raw
        if raw.startswith('+.'):
            self.base = raw[2:]
            self.exact = True
            self.sub = True
            self.weight = 0  # 排序权重最高
        elif raw.startswith('*.'):
            self.base = raw[2:]
            self.exact = False
            self.sub = True
            self.weight = 1
        else:
            self.base = raw
            self.exact = True
            self.sub = False
            self.weight = 2  # 排序权重最低
        self.parts = self.base.split('.')[::-1]  # 逆序，便于 Trie 从 TLD 开始

class TrieNode:
    """Trie 树节点"""
    def __init__(self):
        self.children = {}
        self.exact = False
        self.sub = False

def insert_trie(root, rule_obj):
    """将规则插入 Trie 树"""
    node = root
    for part in rule_obj.parts:
        if part not in node.children:
            node.children[part] = TrieNode()
        node = node.children[part]
    if rule_obj.exact:
        node.exact = True
    if rule_obj.sub:
        node.sub = True

def is_covered_by_trie(root, rule_obj):
    """检查规则是否被 Trie 树中的已有规则覆盖"""
    node = root
    for i, part in enumerate(rule_obj.parts):
        if part not in node.children:
            return False
        node = node.children[part]
        if i < len(rule_obj.parts) - 1:
            # 中间节点有 sub 标记，说明父域名已覆盖
            if node.sub:
                return True
        else:
            # 最后一个节点
            if (not rule_obj.exact or node.exact) and (not rule_obj.sub or node.sub):
                return True
            if node.sub:
                return True
    return False

# ================= 词法分析器 (支持 [ ] 块级) =================

def parse_lines_to_batches(lines):
    """
    将配方文件行解析为批次列表
    每个批次 = (op, items)，op 为 '+' 或 '-'
    items 为 (fmt, target) 列表
    """
    batches = []
    current_op = None
    current_items = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            i += 1
            continue
        
        parts = line.split(maxsplit=2)
        
        # 检测块级开始: "+ list [" or "- yaml ["
        if len(parts) >= 3 and parts[2].startswith('['):
            op = parts[0]
            block_lines = []
            i += 1
            # 持续抓取直到遇到 ]
            while i < len(lines) and not lines[i].strip().startswith(']'):
                block_lines.append(lines[i].strip())
                i += 1
            
            if op == current_op:
                current_items.append(('block', block_lines))
            else:
                if current_op is not None:
                    batches.append((current_op, current_items))
                current_op = op
                current_items = [('block', block_lines)]
        elif len(parts) >= 3:
            op, fmt, target = parts[0], parts[1], parts[2]
            if op == current_op:
                current_items.append((fmt, target))
            else:
                if current_op is not None:
                    batches.append((current_op, current_items))
                current_op = op
                current_items = [(fmt, target)]
        i += 1
    
    if current_op is not None:
        batches.append((current_op, current_items))
    
    return batches

# ================= 递归运算引擎 =================

def compute_rules(batches, rule_type, output_dir, project_root, depth=0):
    """
    递归计算规则集
    
    参数:
        batches: 批次列表
        rule_type: 'domain' 或 'ip'
        output_dir: 已生成规则的输出目录
        project_root: 项目根目录
        depth: 递归深度（用于日志缩进）
    
    返回:
        set of 规则字符串
    """
    indent = "  " * depth
    
    if rule_type == 'domain':
        master_rules = []
        batch_num = 1
        
        for op, items in batches:
            logger.info(f"{indent}  -> 批次 {batch_num} [{op}] ({len(items)} 条源)")
            batch_num += 1
            batch_raw_set = set()
            
            for fmt, target in items:
                if fmt == 'block':
                    logger.info(f"{indent}    [子块] 进入子集计算...")
                    inner_batches = parse_lines_to_batches(target)
                    inner_rules = compute_rules(inner_batches, rule_type, output_dir, project_root, depth + 1)
                    batch_raw_set.update(inner_rules)
                    logger.info(f"{indent}    [子块] 子集完成，{len(inner_rules)} 条结果")
                else:
                    batch_raw_set.update(
                        fetch_and_parse(target, fmt, output_dir, project_root)
                    )
            
            if op == '+':
                # 合并 + Trie 去重
                new_rules = [DomainRule(x) for x in batch_raw_set]
                combined = master_rules + new_rules
                # 排序：从 TLD 开始，短域名优先（更宽泛的规则先入 Trie）
                combined.sort(key=lambda r: (len(r.parts), not r.sub, not r.exact))
                trie = TrieNode()
                next_master = []
                for r in combined:
                    if not is_covered_by_trie(trie, r):
                        next_master.append(r)
                        insert_trie(trie, r)
                master_rules = next_master
            
            elif op == '-':
                # 排除
                exc_rules = [DomainRule(x) for x in batch_raw_set]
                exc_trie = TrieNode()
                for r in exc_rules:
                    insert_trie(exc_trie, r)
                master_rules = [r for r in master_rules if not is_covered_by_trie(exc_trie, r)]
        
        return {r.raw for r in master_rules}
    
    elif rule_type == 'ip':
        master_ips_v4 = []
        master_ips_v6 = []
        batch_num = 1
        
        for op, items in batches:
            logger.info(f"{indent}  -> 批次 {batch_num} [{op}] ({len(items)} 条源)")
            batch_num += 1
            batch_raw_set = set()
            
            for fmt, target in items:
                if fmt == 'block':
                    inner_batches = parse_lines_to_batches(target)
                    inner_rules = compute_rules(inner_batches, rule_type, output_dir, project_root, depth + 1)
                    batch_raw_set.update(inner_rules)
                else:
                    batch_raw_set.update(
                        fetch_and_parse(target, fmt, output_dir, project_root)
                    )
            
            batch_nets_v4 = []
            batch_nets_v6 = []
            for x in batch_raw_set:
                try:
                    net = ipaddress.ip_network(x, strict=False)
                    if net.version == 4:
                        batch_nets_v4.append(net)
                    else:
                        batch_nets_v6.append(net)
                except ValueError:
                    pass
            
            if op == '+':
                master_ips_v4 = list(ipaddress.collapse_addresses(master_ips_v4 + batch_nets_v4))
                master_ips_v6 = list(ipaddress.collapse_addresses(master_ips_v6 + batch_nets_v6))
            
            elif op == '-':
                next_v4 = []
                for inc in master_ips_v4:
                    if not any(inc.subnet_of(exc) for exc in batch_nets_v4):
                        next_v4.append(inc)
                master_ips_v4 = next_v4
                
                next_v6 = []
                for inc in master_ips_v6:
                    if not any(inc.subnet_of(exc) for exc in batch_nets_v6):
                        next_v6.append(inc)
                master_ips_v6 = next_v6
        
        return {str(net) for net in (master_ips_v4 + master_ips_v6)}

# ================= 排序 =================

def sort_domain_rules(rule_set):
    """域名规则排序"""
    rules = [DomainRule(x) for x in rule_set]
    rules.sort(key=lambda r: (r.parts, r.weight))
    return [r.raw for r in rules]

def sort_ip_rules(rule_set):
    """IP 规则排序"""
    nets_v4 = []
    nets_v6 = []
    for x in rule_set:
        try:
            net = ipaddress.ip_network(x, strict=False)
            if net.version == 4:
                nets_v4.append(net)
            else:
                nets_v6.append(net)
        except ValueError:
            pass
    return [str(net) for net in sorted(nets_v4)] + [str(net) for net in sorted(nets_v6)]

# ================= 顶层处理 =================

def process_file(filepath, out_filepath, rule_type, output_dir, project_root):
    """
    处理单个配方文件，生成最终规则文件
    
    参数:
        filepath: 配方文件路径
        out_filepath: 输出文件路径
        rule_type: 'domain' 或 'ip'
        output_dir: 已生成规则的输出目录
        project_root: 项目根目录
    """
    filename = os.path.basename(filepath)
    logger.info(f"\n>> 处理 [{rule_type}] 规则树: {filename}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    batches = parse_lines_to_batches(lines)
    final_set = compute_rules(batches, rule_type, output_dir, project_root)
    
    if rule_type == 'domain':
        final_list = sort_domain_rules(final_set)
    elif rule_type == 'ip':
        final_list = sort_ip_rules(final_set)
    else:
        final_list = sorted(final_set)
    
    # 写入输出文件
    os.makedirs(os.path.dirname(out_filepath), exist_ok=True)
    with open(out_filepath, 'w', encoding='utf-8') as f:
        for item in final_list:
            f.write(item + '\n')
    
    logger.info(f"  ✅ 构建完成: {len(final_list)} 条规则 -> {out_filepath}")
    return len(final_list)

def process_directory(work_dir, out_dir, rule_type, project_root):
    """
    处理目录下所有配方文件
    
    参数:
        work_dir: 配方目录
        out_dir: 输出目录
        rule_type: 'domain' 或 'ip'
        project_root: 项目根目录
    """
    if not os.path.exists(work_dir):
        logger.warning(f"目录不存在: {work_dir}")
        return
    
    os.makedirs(out_dir, exist_ok=True)
    
    all_files = [f for f in os.listdir(work_dir) if f.endswith('.list')]
    # 分离复合文件（引用其他已生成 list 的文件）和基础文件
    special_files = [f for f in all_files if f.endswith('-lite.list')]
    normal_files = [f for f in all_files if f not in special_files]
    
    stats = {}
    
    if normal_files:
        logger.info(f"\n{'='*20} 第一阶段: [{rule_type}] 基础层级编译 {'='*20}")
    for filename in sorted(normal_files):
        filepath = os.path.join(work_dir, filename)
        out_filepath = os.path.join(out_dir, filename)
        count = process_file(filepath, out_filepath, rule_type, out_dir, project_root)
        stats[filename] = count
    
    if special_files:
        logger.info(f"\n{'='*20} 第二阶段: [{rule_type}] 复合组件总装 {'='*20}")
    for filename in sorted(special_files):
        filepath = os.path.join(work_dir, filename)
        out_filepath = os.path.join(out_dir, filename)
        count = process_file(filepath, out_filepath, rule_type, out_dir, project_root)
        stats[filename] = count
    
    return stats
