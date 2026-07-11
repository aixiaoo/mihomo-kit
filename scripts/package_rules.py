#!/usr/bin/env python3
"""package_rules.py - 将 output/ 重组为扁平文件夹结构用于 rules 分支"""

import os
import shutil
import json

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    project_root = get_project_root()
    output_dir = os.path.join(project_root, 'output')
    staging_dir = os.path.join(project_root, 'rules-staging')

    if not os.path.exists(output_dir):
        print("output/ 目录不存在，跳过")
        return

    # 清空 staging 目录
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    os.makedirs(staging_dir)

    # 域名规则：output/domain/{name}.list -> {name}/{name}.list
    domain_dir = os.path.join(output_dir, 'domain')
    yaml_domain_dir = os.path.join(output_dir, 'yaml', 'domain')
    mrs_domain_dir = os.path.join(output_dir, 'mrs', 'domain')

    if os.path.exists(domain_dir):
        for f in sorted(os.listdir(domain_dir)):
            if not f.endswith('.list'):
                continue
            name = f.replace('.list', '')
            rule_dir = os.path.join(staging_dir, name)
            os.makedirs(rule_dir, exist_ok=True)

            # .list
            shutil.copy2(os.path.join(domain_dir, f), os.path.join(rule_dir, f))
            # .yaml
            yaml_src = os.path.join(yaml_domain_dir, f.replace('.list', '.yaml'))
            if os.path.exists(yaml_src):
                shutil.copy2(yaml_src, os.path.join(rule_dir, f.replace('.list', '.yaml')))
            # .mrs
            mrs_src = os.path.join(mrs_domain_dir, f.replace('.list', '.mrs'))
            if os.path.exists(mrs_src):
                shutil.copy2(mrs_src, os.path.join(rule_dir, f.replace('.list', '.mrs')))

    # IP 规则：output/ip/{name}.list -> {name}/{name}-ip.list
    ip_dir = os.path.join(output_dir, 'ip')
    yaml_ip_dir = os.path.join(output_dir, 'yaml', 'ip')
    mrs_ip_dir = os.path.join(output_dir, 'mrs', 'ip')

    if os.path.exists(ip_dir):
        for f in sorted(os.listdir(ip_dir)):
            if not f.endswith('.list'):
                continue
            name = f.replace('.list', '')
            rule_dir = os.path.join(staging_dir, name)
            os.makedirs(rule_dir, exist_ok=True)

            # .list (加 -ip 后缀)
            shutil.copy2(os.path.join(ip_dir, f), os.path.join(rule_dir, f'{name}-ip.list'))
            # .yaml
            yaml_src = os.path.join(yaml_ip_dir, f.replace('.list', '.yaml'))
            if os.path.exists(yaml_src):
                shutil.copy2(yaml_src, os.path.join(rule_dir, f'{name}-ip.yaml'))
            # .mrs
            mrs_src = os.path.join(mrs_ip_dir, f.replace('.list', '.mrs'))
            if os.path.exists(mrs_src):
                shutil.copy2(mrs_src, os.path.join(rule_dir, f'{name}-ip.mrs'))

    # 复制 README.md 和 rule-providers.yaml
    readme_src = os.path.join(output_dir, 'README.md')
    if os.path.exists(readme_src):
        shutil.copy2(readme_src, os.path.join(staging_dir, 'README.md'))

    providers_src = os.path.join(output_dir, 'rule-providers.yaml')
    if os.path.exists(providers_src):
        shutil.copy2(providers_src, os.path.join(staging_dir, 'rule-providers.yaml'))

    # 统计
    rule_count = len([d for d in os.listdir(staging_dir) if os.path.isdir(os.path.join(staging_dir, d))])
    print(f"打包完成: {staging_dir} ({rule_count} 个规则目录)")

if __name__ == '__main__':
    main()
