# mihomo-kit

> 自动同步上游、合并去重、去除失效的 mihomo 规则集仓库

[![Sync Rules](https://img.shields.io/github/actions/workflow/status/aixiaoo/mihomo-kit/sync.yml?style=flat-square&label=Sync%20Rules)](https://github.com/aixiaoo/mihomo-kit/actions/workflows/sync.yml)
[![GitHub Stars](https://img.shields.io/github/stars/aixiaoo/mihomo-kit?style=flat-square&color=blue&label=Stars)](https://github.com/aixiaoo/mihomo-kit/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/aixiaoo/mihomo-kit?style=flat-square&color=60c5ba&label=Forks)](https://github.com/aixiaoo/mihomo-kit/network/members)
[![GitHub Last commit](https://img.shields.io/github/last-commit/aixiaoo/mihomo-kit/main?style=flat-square&color=orange&label=Last%20Commit)](https://github.com/aixiaoo/mihomo-kit/commits/main)
[![GitHub License](https://img.shields.io/github/license/aixiaoo/mihomo-kit?style=flat-square&label=License)](https://github.com/aixiaoo/mihomo-kit/blob/main/LICENSE)

## 项目简介

mihomo-kit 是一个基于 GitHub Actions 自动维护的 [mihomo](https://github.com/MetaCubeX/mihomo)（原 Clash Meta）规则集仓库。

### 核心特性

- **配方驱动** - 使用简洁的 `+/- list/yaml url` 配方文件声明规则来源，支持块级子计算
- **自动合并** - 每日定时从多个上游规则源拉取、合并
- **智能去重** - 域名规则使用 Trie 树检测覆盖关系（如 `+.google.com` 覆盖 `www.google.com`），IP 规则使用 CIDR collapse 合并重叠网段
- **失效检测** - 格式验证 + 可选 DNS 检测，移除不可解析的域名
- **多格式输出** - 同时输出 `.list`（文本）、`.yaml`（mihomo YAML）、`.mrs`（mihomo 二进制）
- **白名单保护** - 全局白名单防止误杀重要域名

## 使用方法

### 在 mihomo 配置中引用

```yaml
rule-providers:
  proxy:
    type: http
    behavior: domain
    format: text
    url: https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/proxy/proxy.list
    path: ./ruleset/proxy.list
    interval: 86400

  ads:
    type: http
    behavior: domain
    format: text
    url: https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/ads/ads.list
    path: ./ruleset/ads.list
    interval: 86400

  cn_ip:
    type: http
    behavior: ipcidr
    format: text
    url: https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/cn/cn-ip.list
    path: ./ruleset/cn_ip.list
    interval: 86400
```

也可以直接引用 `rule-providers.yaml` 获取全部规则提供者配置：

```
https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/rule-providers.yaml
```

### 使用 MRS 二进制格式（更小更快）

```yaml
rule-providers:
  proxy:
    type: http
    behavior: domain
    format: mrs
    url: https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/proxy/proxy.mrs
    path: ./ruleset/proxy.mrs
    interval: 86400
```

## 配方语法

配方文件位于 `recipes/` 目录，使用简单的声明式语法：

```list
# 添加规则源（支持 list 和 yaml 格式）
+ list https://example.com/rules.list
+ yaml https://example.com/rules.yaml

# 排除规则源
- list https://example.com/exclude.list

# 引用本地自定义文件
+ list /custom/proxy_add.list
- list /custom/proxy_del.list

# 内联规则
- list '+.cn'

# 块级子计算（子块内先计算，再作为整体参与主计算）
+ list [
+ list https://example.com/tld-not-cn.list
- list https://example.com/cn.list
]

# 引用其他已生成的配方文件
+ list proxy.list
- list ads.list
```

### 运算逻辑

1. **`+` 操作**：将当前批次的所有规则合并到主规则集，使用 Trie 树去重（被已有规则覆盖的不再添加）
2. **`-` 操作**：从主规则集中移除被当前批次规则覆盖的所有规则
3. **块级子计算**：`[ ... ]` 内的规则先独立计算，计算结果作为整体参与外层运算
4. **跨文件引用**：`proxy-lite.list` 可以引用 `proxy.list`（已先生成），实现规则叠加

## 自定义规则

在 `custom/` 目录中编辑以下文件：

| 文件 | 说明 |
|------|------|
| `proxy_add.list` | 追加到代理规则的域名 |
| `proxy_del.list` | 从代理规则中排除的域名 |
| `ads_add.list` | 追加到广告规则的域名 |
| `ads_del.list` | 从广告规则中排除的域名 |
| `direct_add.list` | 追加到直连规则的域名 |
| `direct_del.list` | 从直连规则中排除的域名 |
| `whitelist.list` | 全局白名单（从所有广告规则中移除，防止误杀） |

## 上游规则源

感谢以下优秀的规则源：

- [DustinWin/ruleset_geodata](https://github.com/DustinWin/ruleset_geodata) - 预构建的 mihomo 规则集
- [Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules) - 经典 clash 规则
- [MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat) - 从 geosite/geoip 转换的规则
- [TG-Twilight/AWAvenue-Ads-Rule](https://github.com/TG-Twilight/AWAvenue-Ads-Rule) - 广告规则
- [217heidai/adblockfilters](https://github.com/217heidai/adblockfilters) - 广告过滤规则
- [Cats-Team/AdRules](https://github.com/Cats-Team/AdRules) - 广告规则
- [wwqgtxx/clash-rules](https://github.com/wwqgtxx/clash-rules) - tld-not-cn 等规则
- [gaoyifan/china-operator-ip](https://github.com/gaoyifan/china-operator-ip) - 中国 IP 段
- [ispip.clang.cn](https://ispip.clang.cn) - 中国 IP 段
- [metowolf/iplist](https://github.com/metowolf/iplist) - IP 列表

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行完整流程（不含 MRS 转换）
python scripts/main.py --no-mrs

# 仅运行合并去重阶段
python scripts/main.py --phase merge --no-mrs

# 运行 DNS 失效检测（采样 10%）
python scripts/main.py --phase validate --dns-check --sample-ratio 0.1 --no-mrs

# 完整流程（含 MRS 转换，需要安装 mihomo 内核）
MIHOMO_PATH=/path/to/mihomo python scripts/main.py
```

## 项目结构

```
mihomo-kit/
├── .github/workflows/sync.yml     # GitHub Actions 工作流
├── recipes/                       # 规则配方（声明上游来源和运算逻辑）
│   ├── domain/                    # 域名规则配方
│   └── ip/                       # IP 规则配方
├── custom/                        # 自定义增删规则
├── scripts/                       # Python 脚本
│   ├── main.py                    # 主入口（4 阶段流水线）
│   ├── fetch.py                   # 上游规则拉取
│   ├── merge.py                   # 合并去重（Trie 树 + IP collapse）
│   ├── validate.py                # 失效检测
│   ├── convert.py                 # 格式转换 + rule-providers 生成
│   ├── package_rules.py           # rules 分支扁平化打包
│   ├── generate_rules_readme.py   # rules 分支 README 生成
│   ├── update_readme.py           # README 统计更新
│   └── utils.py                   # 工具函数
├── requirements.txt
├── LICENSE
└── README.md
```

> `output/` 目录不在 `main` 分支中，由 Actions 自动生成并推送到 `rules` 分支。

## License

GPL-3.0
