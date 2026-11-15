# Shopify 托管店机器人流量审计 Skill

<!-- hupishushu:links:start -->
[虎皮叔叔 · hupishushu.com](https://hupishushu.com/) · [项目介绍](https://hupishushu.com/projects/shopify-bot-traffic-audit-skill/) · [使用指南](https://hupishushu.com/skills/shopify-bot-traffic-audit/)
<!-- hupishushu:links:end -->

一个面向标准 Shopify-hosted Online Store 的只读审计 Skill，用来区分：

- Shopify 已分类的机器人会话
- 疑似自动化流量
- GA4、像素或同意机制导致的追踪缺口
- 广告流量质量问题
- 已由广告平台确认或抵扣的无效流量

它不会把“跳出率高、停留时间短、没有订单”直接当成广告欺诈，也不会修改店铺、广告账户或 DNS。

## 为什么不依赖 Cloudflare 日志

Shopify 托管店的 CDN 和服务器由 Shopify 管理，商家通常拿不到原始 HTTP 或 Cloudflare 请求日志。Shopify 也明确不支持商家在店铺前增加 Cloudflare 橙云代理或 O2O。

因此本 Skill 默认使用以下证据闭环：

1. Shopify Analytics 的 `Human or bot session`
2. GA4 或现有 BigQuery Export
3. Meta Ads / Google Ads 只读报表
4. Microsoft Clarity 行为证据
5. Shopify 付费非测试订单和收入

相关官方说明：

- [Shopify 机器人流量过滤](https://help.shopify.com/en/manual/intro-to-shopify/bots/bot-filtering)
- [Shopify 不支持第三方 Cloudflare 代理](https://help.shopify.com/en/manual/domains/troubleshoot-issues-with-domains)
- [Cloudflare DNS-only 不提供 HTTP 分析](https://developers.cloudflare.com/dns/proxy-status/)

## 两种运行方式

### 1. 报表导出模式

向 Agent 提供 Shopify、GA4、Clarity 和广告平台的当前窗口 CSV 或截图。该模式最容易复核。

### 2. 浏览器授权只读模式

Agent 可以通过可用的 Computer Use 功能读取已经授权的 Shopify Admin、GA4、Meta Ads 和 Google Ads 页面。

- 密码、MFA、Passkey 由用户接管完成
- Meta 建议使用广告账户分析员权限
- Google Ads 建议使用 `Read only` 权限
- 不保存自定义报表，不修改预算、投放、归因、像素或版位
- 不打开客户资料，不采集 IP、Cookie 或个人信息

Computer Use 只是访问方式，不会提升证据本身的置信度；不可用时可退回报表导出模式，Skill 不依赖其他 Skill 才能运行。

## 安装

```bash
git clone https://github.com/owensky-dev/shopify-bot-traffic-audit-skill.git
mkdir -p ~/.codex/skills
cp -R shopify-bot-traffic-audit-skill/shopify-bot-traffic-audit ~/.codex/skills/
```

## 使用

```text
Use $shopify-bot-traffic-audit to audit suspicious paid traffic on my Shopify-hosted store through browser-authorized read-only access.
```

运行时需要明确：

- 店铺域名和主要市场
- 带数字时区偏移的起止时间
- Shopify 报告时区
- 怀疑的渠道、广告系列、版位、国家、设备或落地页
- 当前实际能读取的数据源

Skill 会生成并校验 `audit-manifest.json`，再按证据覆盖返回：

- `ready`：托管店审计证据已形成交叉闭环
- `partial`：只能回答部分问题
- `not_ready`：没有可用的当前窗口证据
- `unsupported_scope`：不是 Shopify 托管的 Online Store

即使状态为 `ready`，也不代表已经获得单次 HTTP 请求级取证。广告欺诈只有在广告平台确认或抵扣后才会标记为 `confirmed_invalid_traffic`。

## 验证

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py shopify-bot-traffic-audit
python3 shopify-bot-traffic-audit/scripts/validate_audit_manifest.py \
  shopify-bot-traffic-audit/references/manifest-example.json
```

## 许可证

[MIT](LICENSE)

## 关注公众号

更多 Shopify 独立站增长、数据分析与 AI 实操，微信搜索：**虎皮叔叔聊跨境独立站**。

![虎皮叔叔聊跨境独立站](assets/wechat-qr.png)
