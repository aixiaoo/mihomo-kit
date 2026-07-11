#!/usr/bin/env python3
"""generate_rules_readme.py - 为 rules 分支生成精简 README"""

import os
import json
from datetime import datetime, timezone, timedelta

BJ_TZ = timezone(timedelta(hours=8))

# 规则描述
RULE_DESC = {
    'domain': {
        'proxy': '代理域名（GFWList + tld-not-cn）',
        'direct': '直连域名（中国域名 + Apple/Microsoft/Games CN）',
        'ads': '广告拦截（AWAvenue + adblockfilters + AdRules + Loyalsoldier）',
        'cn': '中国域名',
        'ai': 'AI 服务域名（ChatGPT, Claude, Gemini 等）',
        'media': '流媒体（Netflix, YouTube 等，排除中国媒体）',
        'google': 'Google 服务（排除中国区和 YouTube）',
        'download': '下载相关（PikPak, Docker 等）',
        'safe': '安全/金融（Twitter, PayPal, 加密货币, Stripe, Reddit）',
        'telegram': 'Telegram',
        'proxy-lite': '精简代理（proxy 去除细分类别）',
        'direct-lite': '精简直连（direct 去除广告和代理）',
    },
    'ip': {
        'cn': '中国 IP 段',
        'direct': '直连 IP 段（私有 IP + 中国 IP）',
        'telegram': 'Telegram IP 段',
        'google': 'Google IP 段',
        'media': '流媒体 IP 段',
    },
}

RAW_BASE = "https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules"

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    project_root = get_project_root()
    stats_path = os.path.join(project_root, 'output', 'stats.json')

    stats = {}
    if os.path.exists(stats_path):
        with open(stats_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)

    domain_stats = stats.get('domain', {})
    ip_stats = stats.get('ip', {})
    total_rules = stats.get('total_rules', 0)
    total_mrs_kb = stats.get('total_mrs_size_kb', 0.0)
    generated_at = stats.get('generated_at', datetime.now(BJ_TZ).strftime('%Y-%m-%d %H:%M:%S'))

    lines = []
    lines.append("# mihomo-kit 规则集\n")
    lines.append(f"> 自动同步 · 合并去重 · 失效检测 | 更新于 {generated_at}\n")
    lines.append(f"> 总规则数: {total_rules:,} | MRS 总大小: {total_mrs_kb:.2f} KB\n")
    lines.append("")

    # 收集所有规则名（domain + ip）
    all_names = set(domain_stats.keys()) | set(ip_stats.keys())
    all_names = sorted(all_names)

    lines.append("## 规则列表\n")
    lines.append("| 规则 | 说明 | 类型 | 条数 | .list | .yaml | .mrs |")
    lines.append("|------|------|------|------|-------|-------|------|")

    for name in all_names:
        desc = RULE_DESC['domain'].get(name) or RULE_DESC['ip'].get(name, '')
        rule_dir = f"{RAW_BASE}/{name}"

        if name in domain_stats and name in ip_stats:
            # 同时有域名和 IP 规则
            d_count = domain_stats[name]
            ip_count = ip_stats[name]
            ip_desc = RULE_DESC['ip'].get(name, '')
            lines.append(
                f"| {name} | {desc} | 域名 | {d_count:,} | "
                f"[list]({rule_dir}/{name}.list) | [yaml]({rule_dir}/{name}.yaml) | [mrs]({rule_dir}/{name}.mrs) |"
            )
            lines.append(
                f"| {name} | {ip_desc} | IP | {ip_count:,} | "
                f"[list]({rule_dir}/{name}-ip.list) | [yaml]({rule_dir}/{name}-ip.yaml) | [mrs]({rule_dir}/{name}-ip.mrs) |"
            )
        elif name in domain_stats:
            count = domain_stats[name]
            lines.append(
                f"| {name} | {desc} | 域名 | {count:,} | "
                f"[list]({rule_dir}/{name}.list) | [yaml]({rule_dir}/{name}.yaml) | [mrs]({rule_dir}/{name}.mrs) |"
            )
        else:
            count = ip_stats[name]
            desc = RULE_DESC['ip'].get(name, '')
            lines.append(
                f"| {name} | {desc} | IP | {count:,} | "
                f"[list]({rule_dir}/{name}-ip.list) | [yaml]({rule_dir}/{name}-ip.yaml) | [mrs]({rule_dir}/{name}-ip.mrs) |"
            )

    lines.append("")
    lines.append("## rule-providers 配置\n")
    lines.append(f"完整配置文件: [rule-providers.yaml]({RAW_BASE}/rule-providers.yaml)\n")
    lines.append("```yaml")
    lines.append("rule-providers:")
    lines.append("  proxy:")
    lines.append("    type: http")
    lines.append("    behavior: domain")
    lines.append("    format: text")
    lines.append(f"    url: {RAW_BASE}/proxy/proxy.list")
    lines.append("    path: ./ruleset/proxy.list")
    lines.append("    interval: 86400")
    lines.append("```")
    lines.append("")

    readme_path = os.path.join(project_root, 'output', 'README.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"rules 分支 README 已生成: {readme_path}")

if __name__ == '__main__':
    main()
