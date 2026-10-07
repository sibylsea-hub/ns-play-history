# ns-play-history

让小机知道你在 Switch 上玩了什么——接上 Nintendo Store app 里的那份游玩记录：你玩过的每个游戏、玩了多久、第一次和最近一次是哪天，还有最近一周每天玩了什么。卡带、数字版都算，Switch 和 Switch 2 都有。

接上之后，小机能自然地问你「昨晚打到哪了」，卡关时直接帮你查攻略，陪你聊剧情、一起吐槽。

**说明页：https://sibylsea-hub.github.io/ns-play-history/**

## 发给你的小机

> 我想让你知道我平时在 Switch 上玩什么～请按 https://sibylsea-hub.github.io/ns-play-history/llms.txt 的说明接上我的游玩记录，需要我登录的时候叫我。

[`llms.txt`](llms.txt) 是写给小机看的步骤说明。你只需要做一件事：在浏览器里打开小机给你的任天堂登录链接，登录后在「Select this account / 选择此人」按钮上**右键 → 复制链接地址**（先别点按钮），然后跟小机说「好了」。之后约两年内不用再登录。

## 小机用到的命令

```bash
python3 ns_play_history.py auth-url                  # 打印任天堂官方登录链接
pbpaste | python3 ns_play_history.py auth-finish     # 读入你复制的授权链接，保存登录凭证
python3 ns_play_history.py fetch                     # 导出全部游玩记录 → play_histories.json
```

只用 Python 3 标准库，无需安装依赖。想自己动手：`python3 ns_play_history.py login`（交互式）然后 `fetch`。

按天的记录只保留最近一周。想让小机一直知道你每天玩了什么，就让 ta 每天或每次聊天前 `fetch` 一次。

## 原理

```
POST https://accounts.nintendo.com/connect/1.0.0/api/session_token   # 授权码 → 登录凭证（约两年）
POST https://accounts.nintendo.com/connect/1.0.0/api/token           # 登录凭证 → 访问凭证（约 15 分钟）
GET  https://app-api.znej.nintendo.com/api/v2.0/users/me/play_histories
     Authorization: Bearer <access_token>
     gentry-locale: en-US        # 必填，决定游戏名语言
```

登录用的是 Nintendo Store app 的入口（`client_id=5c38e31cd085304b`），所以确认页会显示「关联到 Nintendo Store」。登录、确认都在任天堂官方页面完成，脚本和小机都拿不到你的密码；脚本只读，不修改账号里的任何东西。

## 说明

- 这个接口没有公开文档，任天堂可能随时调整。请只用于查看你自己的账号。
- 登录凭证保存在 `~/.ns-play-history/`（仅你可读），等同账号凭证，请勿外传；不用了删掉该文件夹即可。
- 游玩记录是你的私人生活：`llms.txt` 请小机只在你愿意时看，要往外说之前先问你。
- 实测澳洲区账号可用，其他地区欢迎反馈。

## 致谢

新地址最早见于 [Gamer1ce/my-game-vault](https://github.com/Gamer1ce/my-game-vault)；[wolveix/nintendo-go](https://github.com/wolveix/nintendo-go) 也整理了同一接口。登录流程参考了 [NSPlayTime](https://github.com/CafeAuLait-CC/NSPlayTime) 与 Raycast 的 [Switch Game Play History](https://www.raycast.com/kvdo2/switch-game-play-history)。本仓库代码为独立编写。

## 许可证

[MIT](LICENSE)。

与任天堂无关联。Nintendo Switch 为任天堂的商标。
