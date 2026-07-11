#!/usr/bin/env python3
"""update_readme.py - 自动更新 README 中的规则统计信息"""

import os
import re
import json
import subprocess
from datetime import datetime, timezone, timedelta

BJ_TZ = timezone(timedelta(hours=8))

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_file_info(filepath, project_root):
    """获取文件行数和最后更新日期"""
    if not os.path.exists(filepath):
        return None, None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        count = sum(1 for line in f if line.strip())
    
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%cd', '--date=format:%Y.%m.%d', filepath],
            capture_output=True, text=True, cwd=project_root
        )
        date_str = result.stdout.strip() if result.returncode == 0 else ""
        if not date_str:
            date_str = datetime.now(BJ_TZ).strftime("%Y.%m.%d")
    except Exception:
        date_str = datetime.now(BJ_TZ).strftime("%Y.%m.%d")
    
    return count, date_str

def main():
    project_root = get_project_root()
    readme_path = os.path.join(project_root, 'README.md')
    stats_path = os.path.join(project_root, 'output', 'stats.json')
    
    # 读取统计数据
    stats = {}
    if os.path.exists(stats_path):
        with open(stats_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)
    
    domain_stats = stats.get('domain', {})
    ip_stats = stats.get('ip', {})
    total_rules = stats.get('total_rules', 0)
    total_mrs_kb = stats.get('total_mrs_size_kb', 0.0)
    generated_at = stats.get('generated_at', datetime.now(BJ_TZ).strftime('%Y-%m-%d %H:%M:%S'))
    
    # 生成统计表格
    def gen_table(title, stats_dict, rule_type, project_root):
        if not stats_dict:
            return f"### {title}\n\n暂无数据\n"
        
        lines = f"### {title}\n\n"
        lines += "| 规则 | 条数 | 更新日期 | .list | .yaml | .mrs |\n"
        lines += "|------|------|----------|-------|-------|------|\n"
        
        for name in sorted(stats_dict.keys()):
            count = stats_dict[name]
            list_dir = os.path.join(project_root, 'output', rule_type)
            list_file = os.path.join(list_dir, f"{name}.list")
            
            _, date_str = get_file_info(list_file, project_root)
            if not date_str:
                date_str = datetime.now(BJ_TZ).strftime("%Y.%m.%d")
            
            base_url = f"output/{rule_type}"
            yaml_url = f"output/yaml/{rule_type}"
            mrs_url = f"output/mrs/{rule_type}"
            
            lines += f"| {name} | {count} | {date_str} | "
            lines += f"[.list](../../{base_url}/{name}.list) | "
            lines += f"[.yaml](../../{yaml_url}/{name}.yaml) | "
            lines += f"[.mrs](../../{mrs_url}/{name}.mrs) |\n"
        
        return lines
    
    domain_table = gen_table("域名规则", domain_stats, 'domain', project_root)
    ip_table = gen_table("IP 规则", ip_stats, 'ip', project_root)
    
    # 读取现有 README 或创建新
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = ""
    
    # 更新统计区域
    stats_block = f"""<!-- STATS:START -->
## 📊 规则统计

> 最后更新: {generated_at} | 总规则数: {total_rules} | MRS 总大小: {total_mrs_kb:.2f} KB

{domain_table}

{ip_table}
<!-- STATS:END -->"""
    
    # 替换或追加统计区域
    if '<!-- STATS:START -->' in content:
        content = re.sub(
            r'<!-- STATS:START -->.*?<!-- STATS:END -->',
            stats_block,
            content,
            flags=re.DOTALL
        )
    else:
        content = content.rstrip() + "\n\n" + stats_block + "\n"
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"README.md 已更新")

if __name__ == '__main__':
    main()
