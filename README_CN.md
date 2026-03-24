# Awesome VPN 🌍

**免费代理节点，每日自动更新。无需配置，复制即用。**

🌐 **一键复制：** https://awesome-vpn.github.io/

<div align="center">

[![English](https://img.shields.io/badge/English-Switch-blue?style=for-the-badge&logo=markdown)](README.md)
[![简体中文](https://img.shields.io/badge/简体中文-当前-green?style=for-the-badge&logo=markdown)](README_CN.md)

</div>

---

## 🚀 30秒快速上手

### 第一步：复制订阅链接

右键点击链接 → "复制链接地址"：

| 格式 | 订阅链接 | 适用客户端 |
|------|----------|-----------|
| **Base64 列表** | [`https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all`](https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all) | v2rayN、v2rayNG、Streisand |
| **Sing-box JSON** | [`https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/sing-box.json`](https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/sing-box.json) | Sing-box |
| **Clash YAML** | [`https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/clash.yaml`](https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/clash.yaml) | Clash Verge Rev、ClashX |

<details>
<summary><b>📋 复制全部链接（手动）</b></summary>

```
https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all
https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/sing-box.json
https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/clash.yaml
```

</details>

> 💡 **不知道选哪个？** 用**Base64 列表**，大多数软件都支持。

### 第二步：下载客户端软件

| 系统 | 推荐软件 | 下载地址 |
|------|---------|----------|
| **Windows** | v2rayN / Clash Verge Rev | [v2rayN下载](https://github.com/2dust/v2rayN/releases) / [Clash Verge Rev下载](https://github.com/clash-verge-rev/clash-verge-rev/releases) |
| **macOS** | Clash Verge Rev | [Clash Verge Rev下载](https://github.com/clash-verge-rev/clash-verge-rev/releases) |
| **Linux** | v2rayA / Clash Verge Rev | [v2rayA下载](https://github.com/v2rayA/v2rayA/releases) / [Clash Verge Rev下载](https://github.com/clash-verge-rev/clash-verge-rev/releases) |
| **iOS (免费)** | Streisand | [GitHub](https://github.com/MatsuriDayo/Streisand) |
| **安卓** | v2rayNG / Sing-box | [v2rayNG下载](https://github.com/2dust/v2rayNG/releases) / [Sing-box下载](https://github.com/SagerNet/sing-box/releases) |

### 第三步：粘贴使用

1. 打开客户端软件
2. 找到「订阅」或「导入」按钮
3. 粘贴第一步复制的链接
4. 点击「更新」或「下载」
5. 选择一个服务器，点击「连接」

---

## 📥 订阅链接（镜像加速）

如果 GitHub 访问慢，试试这些镜像：

| 镜像 | 链接 | 位置 |
|------|------|------|
| **KKGitHub** | `https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all` | 香港 |
| **GHProxy** | `https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all` | 日本 |

---

## ❓ 常见问题

### Q：这是免费的吗？
**是的。** 所有节点都是从公开渠道收集的，无需付费。

### Q：为什么连不上？
可能原因：
- **节点过期**：等待下次自动更新（每天 UTC 00:00）
- **网络被墙**：试试上面的镜像链接
- **格式不对**：确认你用的格式（通用/Sing-box/Clash）和软件匹配

### Q：安全吗？
- 这些是**公共节点**，来自互联网公开渠道
- **不要用于敏感操作**（网银、私人账号等）
- 我们不记录你的流量，但公共节点可能会

### Q：多久更新一次？
**每天 UTC 00:00 自动更新**（北京时间早上8点）

### Q：我应该用哪种格式？
| 如果你的软件是... | 用这个格式 |
|------------------|-----------|
| v2rayN、v2rayNG、v2rayA、Streisand | **Base64 列表** |
| Clash Verge Rev、ClashX | **Clash YAML** |
| Sing-box | **Sing-box JSON** |

---

## 🛠️ 故障排除

**"获取订阅失败"**
→ 试试上面的镜像链接，或者先在客户端里开启「系统代理」再试。

**"连接成功但上不了网"**
→ 节点可能失效了。点击「更新订阅」获取最新节点，或换个服务器试试。

**"速度很慢"**
→ 公共节点用的人比较多。多试几个服务器，找到速度快的。

---

## 📱 客户端使用教程

<details>
<summary><b>v2rayN（Windows）</b></summary>

1. 从 [GitHub](https://github.com/2dust/v2rayN/releases) 下载并解压
2. 运行 `v2rayN.exe`
3. 点击 **订阅** → **订阅设置**
4. 粘贴Base64 列表链接，点击 **添加** → **确定**
5. 点击 **订阅** → **更新订阅**
6. 右键选择一个服务器 → **设为活动服务器**
7. 点击 **系统代理** → **自动配置系统代理**
</details>

<details>
<summary><b>v2rayNG（安卓）</b></summary>

1. 从 [GitHub](https://github.com/2dust/v2rayNG/releases) 下载安装
2. 点击右上角 **+** → **从剪贴板导入**（或「从URL导入」）
3. 粘贴Base64 列表链接，点击 **导入**
4. 点击右上角菜单（⋮）→ **更新订阅**
5. 点击选择一个服务器
6. 点击底部 **V** 按钮连接
</details>

<details>
<summary><b>Shadowrocket（iOS）</b></summary>

1. 在 App Store 购买 Shadowrocket（约¥20）
2. 点击右上角 **+** → **类型选择「Subscribe」**
3. 在 **URL** 栏粘贴Base64 列表链接
4. 点击 **保存**，然后点击订阅更新
5. 选择服务器，点击连接按钮
</details>

<details>
<summary><b>Sing-box（安卓）</b></summary>

1. 从 [GitHub](https://github.com/SagerNet/sing-box/releases) 下载
2. 点击 **配置** → **+** → **远程配置**
3. 粘贴 **Sing-box** 格式的链接
4. 点击 **创建** → **连接**
</details>

---

## 🔄 更新时间表

| 更新类型 | UTC时间 | 北京时间 |
|---------|---------|---------|
| 自动更新 | 每天 00:00 | 每天 08:00 |
| 手动触发 | 随时 | 随时（通过 GitHub Actions） |

---

## ⚖️ 免责声明

- 本项目聚合**互联网公开的**代理节点
- **仅供学习研究使用**
- 请遵守当地法律法规
- **不保证可用性** - 节点随时可能失效
- 我们不拥有或控制这些节点

---

## 🌟 Star 趋势

如果这个项目帮到了你，请点个 ⭐ 支持一下！

[![Star History Chart](https://api.star-history.com/svg?repos=awesome-vpn/awesome-vpn&type=Date)](https://star-history.com/#awesome-vpn/awesome-vpn&Date)

---

<p align="center">
  <b>人人享有自由互联网 🌐</b>
</p>
