# ns-play-history

让你的 AI 助手看到你的 Nintendo Switch 游玩记录——和 Nintendo Store app 里显示的是同一份数据：每个玩过的游戏的累计时长、游玩天数、第一次 / 最后一次游玩时间，以及最近一周按天的明细。卡带、数字版都算，Switch 和 Switch 2 都有。

**说明页：https://sibylsea-hub.github.io/ns-play-history/**

## 发给你的 agent

> 请按 https://sibylsea-hub.github.io/ns-play-history/llms.txt 的说明，帮我导出我的 Switch 游玩记录。需要我登录的时候告诉我。

[`llms.txt`](llms.txt) 是写给 AI 读的步骤说明。你只需要做一件事：在浏览器里打开 agent 给你的任天堂登录链接，登录后在「Select this account / 选择此人」按钮上**右键 → 复制链接地址**（不要点按钮），然后告诉 agent「好了」。之后约两年内不用再登录。

## agent 用到的命令

```bash
python3 ns_play_history.py auth-url                  # 打印任天堂官方登录链接
pbpaste | python3 ns_play_history.py auth-finish     # 读入用户复制的授权链接，保存登录凭证
python3 ns_play_history.py fetch                     # 导出全部游玩记录 → play_histories.json
```

只用 Python 3 标准库，无需安装依赖。自己动手的话：`python3 ns_play_history.py login`（交互式）然后 `fetch`。

## 原理

```
POST https://accounts.nintendo.com/connect/1.0.0/api/session_token   # 授权码 → 登录凭证（约两年）
POST https://accounts.nintendo.com/connect/1.0.0/api/token           # 登录凭证 → 访问凭证（约 15 分钟）
GET  https://app-api.znej.nintendo.com/api/v2.0/users/me/play_histories
     Authorization: Bearer <access_token>
     gentry-locale: en-US        # 必填，决定游戏名语言
```

登录用的是 Nintendo Store app 的入口（`client_id=5c38e31cd085304b`），所以确认页会显示「关联到 Nintendo Store」。登录、确认都在任天堂官方页面完成，脚本和 agent 都拿不到你的密码；脚本只读，不修改账号里的任何东西。

## 说明

- 这个接口没有公开文档，任天堂可能随时调整。请只用于查看你自己的账号。
- 登录凭证保存在 `~/.ns-play-history/`（仅你可读），等同账号凭证，请勿外传；不用了删掉该文件夹即可。
- 游玩时长是私人数据：`llms.txt` 要求 agent 只在你要求时读取，对外转述前先问你。
- 实测澳洲区账号可用，其他地区欢迎反馈。

## 致谢

新地址最早见于 [Gamer1ce/my-game-vault](https://github.com/Gamer1ce/my-game-vault)；[wolveix/nintendo-go](https://github.com/wolveix/nintendo-go) 也整理了同一接口。登录流程参考了 [NSPlayTime](https://github.com/CafeAuLait-CC/NSPlayTime) 与 Raycast 的 [Switch Game Play History](https://www.raycast.com/kvdo2/switch-game-play-history)。本仓库代码为独立编写。

## 许可证

[MIT](LICENSE)。

与任天堂无关联。Nintendo Switch 为任天堂的商标。
