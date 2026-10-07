# ns-play-history

查看你自己的 Nintendo Switch 游玩记录——和 Nintendo Store app 里显示的是同一份数据：每个玩过的游戏的累计时长、游玩天数、第一次 / 最后一次游玩时间，以及最近一周按天的明细。卡带、数字版都算，Switch 和 Switch 2 都有。

**完整说明（带图解）：https://sibylsea-hub.github.io/ns-play-history/**

```bash
python3 ns_play_history.py login   # 一次性：在浏览器登录任天堂账号，粘贴授权链接（约两年有效）
python3 ns_play_history.py fetch   # 导出全部游玩记录 → play_histories.json
```

只用 Python 3 标准库，无需安装依赖。登录在任天堂官方页面完成，脚本拿不到你的密码，也不会修改账号里的任何东西。

登录时出现「Select this account / 选择此人」页面，**不要点按钮**，在按钮上右键复制链接地址（或在 F12 控制台执行 `copy(document.getElementById('authorize-switch-approval-link').href)`），粘贴回脚本即可。

## 原理

```
POST https://accounts.nintendo.com/connect/1.0.0/api/session_token   # 授权码 → 登录凭证（约两年）
POST https://accounts.nintendo.com/connect/1.0.0/api/token           # 登录凭证 → 访问凭证（约 15 分钟）
GET  https://app-api.znej.nintendo.com/api/v2.0/users/me/play_histories
     Authorization: Bearer <access_token>
     gentry-locale: en-US        # 必填，决定游戏名语言
```

登录用的是 Nintendo Store app 的入口（`client_id=5c38e31cd085304b`），所以确认页会显示「关联到 Nintendo Store」。

## 说明

- 这个接口没有公开文档，任天堂可能随时调整。请只用于查看你自己的账号。
- 登录凭证保存在 `~/.ns-play-history/`（仅你可读），等同账号凭证，请勿外传；不用了删掉该文件夹即可。
- 实测澳洲区账号可用，其他地区欢迎反馈。

## 致谢

新地址最早见于 [Gamer1ce/my-game-vault](https://github.com/Gamer1ce/my-game-vault)；[wolveix/nintendo-go](https://github.com/wolveix/nintendo-go) 也整理了同一接口。登录流程参考了 [NSPlayTime](https://github.com/CafeAuLait-CC/NSPlayTime) 与 Raycast 的 [Switch Game Play History](https://www.raycast.com/kvdo2/switch-game-play-history)。本仓库代码为独立编写。

## 许可证

[MIT](LICENSE)。

与任天堂无关联。Nintendo Switch 为任天堂的商标。
