# mihomo-kit

> 自动同步上游、合并去重、去除失效的 mihomo 规则集仓库

[![Sync Rules](https://github.com/aixiaoo/mihomo-kit/actions/workflows/sync.yml/badge.svg)](https://github.com/aixiaoo/mihomo-kit/actions/workflows/sync.yml)
[![License](https://img.shields.io/github/license/aixiaoo/mihomo-kit)](LICENSE)

## 项目简介

mihomo-kit 是一个基于 GitHub Actions 自动维护的 [mihomo](https://github.com/MetaCubeX/mihomo)（原 Clash Meta）规则集仓库。

### 核心特性

- **配方驱动** - 使用简洁的 `+/- list/yaml url` 配方文件声明规则来源，支持块级子计算
- **自动合并** - 每日定时从多个上游规则源拉取、合并
- **智能去重** - 域名规则使用 Trie 树检测覆盖关系（如 `+.google.com` 覆盖 `www.google.com`），IP 规则使用 CIDR collapse 合并重叠网段
- **失效检测** - 格式验证 + 可选 DNS 检测，移除不可解析的域名
- **多格式输出** - 同时输出 `.list`（文本）、`.yaml`（mihomo YAML）、`.mrs`（mihomo 二进制）
- **白名单保护** - 全局白名单防止误杀重要域名

## 规则分类

### 域名规则

| 规则 | 说明 |
|------|------|
| `proxy` | 代理域名（GFWList + tld-not-cn） |
| `direct` | 直连域名（中国域名 + Apple/Microsoft/Games CN） |
| `ads` | 广告拦截（AWAvenue + adblockfilters + AdRules + Loyalsoldier） |
| `cn` | 中国域名 |
| `ai` | AI 服务域名（ChatGPT, Claude, Gemini 等，排除中国 AI） |
| `media` | 流媒体（Netflix, YouTube 等，排除中国媒体） |
| `google` | Google 服务（排除中国区和 YouTube） |
| `download` | 下载相关（PikPak, Docker 等） |
| `safe` | 安全/金融（Twitter, PayPal, 加密货币, Stripe, Reddit） |
| `telegram` | Telegram |
| `proxy-lite` | 精简代理（proxy 去除细分类别） |
| `direct-lite` | 精简直连（direct 去除广告和代理） |

### IP 规则

| 规则 | 说明 |
|------|------|
| `cn` | 中国 IP 段 |
| `direct` | 直连 IP 段（私有 IP + 中国 IP） |
| `telegram` | Telegram IP 段 |
| `google` | Google IP 段 |
| `media` | 流媒体 IP 段 |

## 使用方法

### 在 mihomo 配置中引用

```yaml
rule-providers:
  proxy:
    type: http
    behavior: domain
    format: text
    url: https://raw.githubusercontent.com/aixiaoo/mihomo-kit/main/output/domain/proxy.list
    path: ./ruleset/proxy.list
    interval: 86400

  ads:
    type: http
    behavior: domain
    format: text
    url: https://raw.githubusercontent.com/aixiaoo/mihomo-kit/main/output/domain/ads.list
    path: ./ruleset/ads.list
    interval: 86400

  cn_ip:
    type: http
    behavior: ipcidr
    format: text
    url: https://raw.githubusercontent.com/aixiaoo/mihomo-kit/main/output/ip/cn.list
    path: ./ruleset/cn_ip.list
    interval: 86400
```

也可以直接引用 `output/rule-providers.yaml` 获取全部规则提供者配置。

### 使用 MRS 二进制格式（更小更快）

```yaml
rule-providers:
  proxy:
    type: http
    behavior: domain
    format: mrs
    url: https://raw.githubusercontent.com/aixiaoo/mihomo-kit/main/output/mrs/domain/proxy.mrs
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
│   ├── main.py                    # 主入口
│   ├── fetch.py                   # 上游规则拉取
│   ├── merge.py                   # 合并去重（Trie 树 + IP collapse）
│   ├── validate.py                # 失效检测
│   ├── convert.py                 # 格式转换
│   ├── update_readme.py           # README 统计更新
│   └── utils.py                   # 工具函数
├── output/                        # 生成的规则文件
│   ├── domain/                    # .list 域名规则
│   ├── ip/                        # .list IP 规则
│   ├── yaml/                      # .yaml 格式
│   ├── mrs/                       # .mrs 二进制格式
│   ├── rule-providers.yaml        # mihomo rule-providers 配置
│   └── stats.json                 # 统计信息
├── requirements.txt
└── README.md
```

## License

MIT

<!-- STATS:START -->
## 📊 规则统计

> 最后更新: 2026-07-11 09:03:27 | 总规则数: 741377 | MRS 总大小: 0.00 KB

### 域名规则

| 规则 | 条数 | 更新日期 | .list | .yaml | .mrs |
|------|------|----------|-------|-------|------|
| ads | 342909 | 2026.07.11 | [.list](../../output/domain/ads.list) | [.yaml](../../output/yaml/domain/ads.yaml) | [.mrs](../../output/mrs/domain/ads.mrs) |
| ai | 176 | 2026.07.11 | [.list](../../output/domain/ai.list) | [.yaml](../../output/yaml/domain/ai.yaml) | [.mrs](../../output/mrs/domain/ai.mrs) |
| cn | 113823 | 2026.07.11 | [.list](../../output/domain/cn.list) | [.yaml](../../output/yaml/domain/cn.yaml) | [.mrs](../../output/mrs/domain/cn.mrs) |
| direct | 114113 | 2026.07.11 | [.list](../../output/domain/direct.list) | [.yaml](../../output/yaml/domain/direct.yaml) | [.mrs](../../output/mrs/domain/direct.mrs) |
| direct-lite | 112171 | 2026.07.11 | [.list](../../output/domain/direct-lite.list) | [.yaml](../../output/yaml/domain/direct-lite.yaml) | [.mrs](../../output/mrs/domain/direct-lite.mrs) |
| download | 13 | 2026.07.11 | [.list](../../output/domain/download.list) | [.yaml](../../output/yaml/domain/download.yaml) | [.mrs](../../output/mrs/domain/download.mrs) |
| google | 627 | 2026.07.11 | [.list](../../output/domain/google.list) | [.yaml](../../output/yaml/domain/google.yaml) | [.mrs](../../output/mrs/domain/google.mrs) |
| media | 1773 | 2026.07.11 | [.list](../../output/domain/media.list) | [.yaml](../../output/yaml/domain/media.yaml) | [.mrs](../../output/mrs/domain/media.mrs) |
| proxy | 20006 | 2026.07.11 | [.list](../../output/domain/proxy.list) | [.yaml](../../output/yaml/domain/proxy.yaml) | [.mrs](../../output/mrs/domain/proxy.mrs) |
| proxy-lite | 18404 | 2026.07.11 | [.list](../../output/domain/proxy-lite.list) | [.yaml](../../output/yaml/domain/proxy-lite.yaml) | [.mrs](../../output/mrs/domain/proxy-lite.mrs) |
| safe | 1091 | 2026.07.11 | [.list](../../output/domain/safe.list) | [.yaml](../../output/yaml/domain/safe.yaml) | [.mrs](../../output/mrs/domain/safe.mrs) |
| telegram | 21 | 2026.07.11 | [.list](../../output/domain/telegram.list) | [.yaml](../../output/yaml/domain/telegram.yaml) | [.mrs](../../output/mrs/domain/telegram.mrs) |


### IP 规则

| 规则 | 条数 | 更新日期 | .list | .yaml | .mrs |
|------|------|----------|-------|-------|------|
| cn | 8013 | 2026.07.11 | [.list](../../output/ip/cn.list) | [.yaml](../../output/yaml/ip/cn.yaml) | [.mrs](../../output/mrs/ip/cn.mrs) |
| direct | 8031 | 2026.07.11 | [.list](../../output/ip/direct.list) | [.yaml](../../output/yaml/ip/direct.yaml) | [.mrs](../../output/mrs/ip/direct.mrs) |
| google | 112 | 2026.07.11 | [.list](../../output/ip/google.list) | [.yaml](../../output/yaml/ip/google.yaml) | [.mrs](../../output/mrs/ip/google.mrs) |
| media | 83 | 2026.07.11 | [.list](../../output/ip/media.list) | [.yaml](../../output/yaml/ip/media.yaml) | [.mrs](../../output/mrs/ip/media.mrs) |
| telegram | 11 | 2026.07.11 | [.list](../../output/ip/telegram.list) | [.yaml](../../output/yaml/ip/telegram.yaml) | [.mrs](../../output/mrs/ip/telegram.mrs) |

<!-- STATS:END -->
