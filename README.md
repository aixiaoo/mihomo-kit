# mihomo-kit 规则集

> 自动同步 · 合并去重 · 失效检测 | 更新于 2026-07-24 04:08:45

> 总规则数: 618,922 | MRS 总大小: 5034.04 KB


## 规则列表

| 规则 | 说明 | 类型 | 条数 | .list | .yaml | .mrs |
|------|------|------|------|-------|-------|------|
| advertising | 广告拦截（metacubex + blackmatrix7 + 自定义白名单） | 域名 | 436,459 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/advertising/advertising.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/advertising/advertising.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/advertising/advertising.mrs) |
| ai | AI 服务非中国（metacubex category-ai-!cn） | 域名 | 179 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/ai/ai.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/ai/ai.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/ai/ai.mrs) |
| ai | AI 服务 IP 段（占位,缺上游） | IP | 4 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/ai/ai-ip.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/ai/ai-ip.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/ai/ai-ip.mrs) |
| apple | Apple 排除中国区（metacubex apple - apple@cn） | 域名 | 1,485 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/apple/apple.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/apple/apple.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/apple/apple.mrs) |
| china | 中国域名（metacubex cn + DustinWin + Loyalsoldier） | 域名 | 113,834 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/china/china.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/china/china.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/china/china.mrs) |
| china | 中国 IP 段（metacubex + 多源补全） | IP | 8,068 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/china/china-ip.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/china/china-ip.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/china/china-ip.mrs) |
| crypto | 加密货币（metacubex category-cryptocurrency） | 域名 | 232 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/crypto/crypto.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/crypto/crypto.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/crypto/crypto.mrs) |
| dev | 开发服务（metacubex category-dev） | 域名 | 613 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/dev/dev.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/dev/dev.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/dev/dev.mrs) |
| disney | Disney+ | 域名 | 327 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/disney/disney.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/disney/disney.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/disney/disney.mrs) |
| emby | Emby 媒体服务器（metacubex category-emby） | 域名 | 216 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/emby/emby.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/emby/emby.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/emby/emby.mrs) |
| emby | Emby 服务器 IP 段（占位,自部署） | IP | 9 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/emby/emby-ip.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/emby/emby-ip.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/emby/emby-ip.mrs) |
| facebook | Facebook | 域名 | 395 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/facebook/facebook.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/facebook/facebook.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/facebook/facebook.mrs) |
| fakeip_filter |  | 域名 | 207 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/fakeip_filter/fakeip_filter.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/fakeip_filter/fakeip_filter.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/fakeip_filter/fakeip_filter.mrs) |
| games | 游戏平台非中国（metacubex category-games-!cn） | 域名 | 800 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/games/games.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/games/games.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/games/games.mrs) |
| google | Google 排除中国区（metacubex google@!cn） | 域名 | 656 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/google/google.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/google/google.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/google/google.mrs) |
| google | Google IP 段（metacubex + 官方 goog.txt） | IP | 7,398 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/google/google-ip.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/google/google-ip.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/google/google-ip.mrs) |
| instagram |  | 域名 | 72 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/instagram/instagram.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/instagram/instagram.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/instagram/instagram.mrs) |
| microsoft | Microsoft 排除中国区（metacubex microsoft - microsoft@cn） | 域名 | 506 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/microsoft/microsoft.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/microsoft/microsoft.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/microsoft/microsoft.mrs) |
| netflix | Netflix | 域名 | 24 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/netflix/netflix.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/netflix/netflix.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/netflix/netflix.mrs) |
| netflix | Netflix IP 段 | IP | 108 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/netflix/netflix-ip.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/netflix/netflix-ip.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/netflix/netflix-ip.mrs) |
| private | 私有/内网域名（blackmatrix7 Lan + DustinWin） | 域名 | 139 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/private/private.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/private/private.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/private/private.mrs) |
| private | 私有 IP 段（blackmatrix7 Lan + DustinWin + metacubex） | IP | 18 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/private/private-ip.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/private/private-ip.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/private/private-ip.mrs) |
| proxy | 代理兜底（metacubex gfw + 自定义） | 域名 | 4,330 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/proxy/proxy.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/proxy/proxy.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/proxy/proxy.mrs) |
| socialmedia | 社交媒体非中国（metacubex category-social-media-!cn） | 域名 | 604 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/socialmedia/socialmedia.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/socialmedia/socialmedia.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/socialmedia/socialmedia.mrs) |
| socialmedia | 社交媒体 IP 段（metacubex twitter + facebook） | IP | 139 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/socialmedia/socialmedia-ip.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/socialmedia/socialmedia-ip.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/socialmedia/socialmedia-ip.mrs) |
| speedtest | Speedtest 测速（metacubex category-speedtest） | 域名 | 75 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/speedtest/speedtest.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/speedtest/speedtest.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/speedtest/speedtest.mrs) |
| spotify | Spotify | 域名 | 25 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/spotify/spotify.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/spotify/spotify.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/spotify/spotify.mrs) |
| streaming | 国际流媒体总集（metacubex category-media 减 CN） | 域名 | 1,573 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/streaming/streaming.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/streaming/streaming.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/streaming/streaming.mrs) |
| streaming | 流媒体 IP 段（metacubex netflix） | IP | 108 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/streaming/streaming-ip.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/streaming/streaming-ip.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/streaming/streaming-ip.mrs) |
| telegram | Telegram | 域名 | 21 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/telegram/telegram.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/telegram/telegram.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/telegram/telegram.mrs) |
| telegram | Telegram IP 段（metacubex + 官方 CIDR） | IP | 12 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/telegram/telegram-ip.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/telegram/telegram-ip.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/telegram/telegram-ip.mrs) |
| tm | 即时通讯（metacubex category-communication） | 域名 | 149 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/tm/tm.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/tm/tm.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/tm/tm.mrs) |
| tracking | 追踪/埋点（blackmatrix7 Privacy） | 域名 | 39,916 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/tracking/tracking.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/tracking/tracking.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/tracking/tracking.mrs) |
| twitter |  | 域名 | 24 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/twitter/twitter.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/twitter/twitter.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/twitter/twitter.mrs) |
| twitter |  | IP | 20 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/twitter/twitter-ip.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/twitter/twitter-ip.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/twitter/twitter-ip.mrs) |
| youtube | YouTube | 域名 | 177 | [list](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/youtube/youtube.list) | [yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/youtube/youtube.yaml) | [mrs](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/youtube/youtube.mrs) |

## rule-providers 配置

完整配置文件: [rule-providers.yaml](https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/rule-providers.yaml)

```yaml
rule-providers:
  proxy:
    type: http
    behavior: domain
    format: text
    url: https://raw.githubusercontent.com/aixiaoo/mihomo-kit/rules/proxy/proxy.list
    path: ./ruleset/proxy.list
    interval: 86400
```
