#!/usr/bin/env python3
"""main.py - mihomo-kit 主入口

功能流程:
1. Phase 1: 拉取上游规则并合并去重（配方驱动 + Trie 树）
2. Phase 2: 失效规则检测与移除（格式验证 + DNS 检测）
3. Phase 3: 格式转换（.list -> .yaml -> .mrs）
4. Phase 4: 生成 rule-providers 配置和统计信息

用法:
  python scripts/main.py [--dns-check] [--sample-ratio 0.1] [--no-mrs]

环境变量:
  GITHUB_TOKEN: GitHub API token（可选，用于提升请求频率限制）
  MIHOMO_PATH: mihomo 内核路径（默认: mihomo）
  DNS_CHECK: 是否启用 DNS 检测（默认: false）
  SAMPLE_RATIO: DNS 检测采样比例（默认: 0.1）
  NO_MRS: 是否跳过 MRS 转换（默认: false）
"""

import os
import sys
import json
import argparse
import subprocess

# 确保可以 import 同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import logger, format_bj_time, count_lines, get_file_size
from merge import process_directory
from validate import validate_file
from convert import convert_directory, generate_provider_yaml, generate_stats

def get_project_root():
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    parser = argparse.ArgumentParser(description='mihomo-kit 规则集自动同步工具')
    parser.add_argument('--dns-check', action='store_true', 
                        help='启用 DNS 失效域名检测（较慢）')
    parser.add_argument('--sample-ratio', type=float, default=0.1,
                        help='DNS 检测采样比例 (0.0-1.0，默认: 0.1)')
    parser.add_argument('--no-mrs', action='store_true',
                        help='跳过 MRS 二进制转换')
    parser.add_argument('--no-yaml', action='store_true',
                        help='跳过 YAML 格式转换')
    parser.add_argument('--phase', choices=['all', 'merge', 'validate', 'convert'], 
                        default='all', help='只运行指定阶段')
    args = parser.parse_args()
    
    # 从环境变量读取配置
    dns_check = args.dns_check or os.environ.get('DNS_CHECK', 'false').lower() == 'true'
    sample_ratio = float(os.environ.get('SAMPLE_RATIO', str(args.sample_ratio)))
    no_mrs = args.no_mrs or os.environ.get('NO_MRS', 'false').lower() == 'true'
    mihomo_path = os.environ.get('MIHOMO_PATH', 'mihomo')
    
    project_root = get_project_root()
    recipes_domain_dir = os.path.join(project_root, 'recipes', 'domain')
    recipes_ip_dir = os.path.join(project_root, 'recipes', 'ip')
    output_domain_dir = os.path.join(project_root, 'output', 'domain')
    output_ip_dir = os.path.join(project_root, 'output', 'ip')
    yaml_domain_dir = os.path.join(project_root, 'output', 'yaml', 'domain')
    yaml_ip_dir = os.path.join(project_root, 'output', 'yaml', 'ip')
    mrs_domain_dir = os.path.join(project_root, 'output', 'mrs', 'domain')
    mrs_ip_dir = os.path.join(project_root, 'output', 'mrs', 'ip')
    
    logger.info("=" * 60)
    logger.info("  mihomo-kit 规则集自动同步工具")
    logger.info(f"  时间: {format_bj_time()}")
    logger.info(f"  DNS检测: {'启用' if dns_check else '禁用'} (采样: {sample_ratio})")
    logger.info(f"  MRS转换: {'跳过' if no_mrs else '启用'}")
    logger.info("=" * 60)
    
    # ==================== Phase 1: 合并去重 ====================
    if args.phase in ('all', 'merge'):
        logger.info("\n" + "=" * 60)
        logger.info("  Phase 1: 拉取上游规则并合并去重")
        logger.info("=" * 60)
        
        # 处理域名规则
        domain_stats = process_directory(
            recipes_domain_dir, output_domain_dir, 'domain', project_root
        )
        
        # 处理 IP 规则
        ip_stats = process_directory(
            recipes_ip_dir, output_ip_dir, 'ip', project_root
        )
        
        logger.info("\n" + "-" * 40)
        logger.info("  Phase 1 统计:")
        if domain_stats:
            logger.info("  域名规则:")
            for name, count in sorted(domain_stats.items()):
                logger.info(f"    {name}: {count} 条")
        if ip_stats:
            logger.info("  IP 规则:")
            for name, count in sorted(ip_stats.items()):
                logger.info(f"    {name}: {count} 条")
        logger.info("-" * 40)
    
    # ==================== Phase 2: 失效检测 ====================
    if args.phase in ('all', 'validate'):
        logger.info("\n" + "=" * 60)
        logger.info("  Phase 2: 失效规则检测与移除")
        logger.info("=" * 60)
        
        # 域名规则验证
        if os.path.exists(output_domain_dir):
            for f in sorted(os.listdir(output_domain_dir)):
                if not f.endswith('.list'):
                    continue
                filepath = os.path.join(output_domain_dir, f)
                logger.info(f"  验证域名规则: {f}")
                result = validate_file(filepath, 'domain', dns_check, sample_ratio)
                logger.info(f"    原始: {result['original']}, 有效: {result['valid']}, "
                          f"格式错误移除: {result['malformed_removed']}")
                if dns_check and 'dns_checked' in result:
                    logger.info(f"    DNS检测: {result['dns_checked']}, 失效移除: {result['dead_removed']}")
        
        # IP 规则验证
        if os.path.exists(output_ip_dir):
            for f in sorted(os.listdir(output_ip_dir)):
                if not f.endswith('.list'):
                    continue
                filepath = os.path.join(output_ip_dir, f)
                logger.info(f"  验证IP规则: {f}")
                result = validate_file(filepath, 'ip', dns_check, sample_ratio)
                logger.info(f"    原始: {result['original']}, 有效: {result['valid']}, "
                          f"格式错误移除: {result['malformed_removed']}")
    
    # ==================== Phase 3: 格式转换 ====================
    if args.phase in ('all', 'convert'):
        logger.info("\n" + "=" * 60)
        logger.info("  Phase 3: 格式转换")
        logger.info("=" * 60)
        
        # 域名规则转换
        if not args.no_yaml or not no_mrs:
            convert_directory(
                output_domain_dir, yaml_domain_dir, mrs_domain_dir, 
                'domain', mihomo_path if not no_mrs else 'mihomo_not_found'
            )
            
            # IP 规则转换
            convert_directory(
                output_ip_dir, yaml_ip_dir, mrs_ip_dir, 
                'ip', mihomo_path if not no_mrs else 'mihomo_not_found'
            )
    
    # ==================== Phase 4: 生成配置和统计 ====================
    if args.phase in ('all', 'convert'):
        logger.info("\n" + "=" * 60)
        logger.info("  Phase 4: 生成配置和统计")
        logger.info("=" * 60)
        
        # 从 git remote 获取仓库 URL
        repo_url = os.environ.get('REPO_URL', '')
        if not repo_url:
            try:
                result = subprocess.run(
                    ['git', 'remote', 'get-url', 'origin'],
                    capture_output=True, text=True, cwd=project_root
                )
                if result.returncode == 0:
                    git_url = result.stdout.strip()
                    # 转换 git URL 为 raw URL
                    # https://github.com/user/repo.git -> https://raw.githubusercontent.com/user/repo/main
                    if 'github.com' in git_url:
                        parts = git_url.replace('.git', '').split('/')
                        if len(parts) >= 5:
                            repo_url = f"https://raw.githubusercontent.com/{parts[3]}/{parts[4]}/main"
            except Exception:
                pass
        
        provider_yaml_path = os.path.join(project_root, 'output', 'rule-providers.yaml')
        providers = generate_provider_yaml(
            output_domain_dir, output_ip_dir, 
            provider_yaml_path, repo_url
        )
        
        # 生成统计信息
        stats = generate_stats(
            output_domain_dir, output_ip_dir, 
            os.path.join(project_root, 'output', 'mrs')
        )
        
        stats['generated_at'] = format_bj_time()
        stats['dns_check'] = dns_check
        stats['providers_count'] = len(providers)
        
        stats_path = os.path.join(project_root, 'output', 'stats.json')
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  统计信息已写入: {stats_path}")
        logger.info(f"  规则提供者配置: {provider_yaml_path}")
        logger.info(f"  总规则数: {stats['total_rules']}")
        logger.info(f"  MRS 总大小: {stats['total_mrs_size_kb']:.2f} KB")
    
    logger.info("\n" + "=" * 60)
    logger.info("  ✅ 全部完成!")
    logger.info("=" * 60)

if __name__ == '__main__':
    main()
