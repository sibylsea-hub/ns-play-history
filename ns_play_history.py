#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Sibyl (sibylsea-hub)
"""查看你自己的 Nintendo Switch 游玩记录（与 Nintendo Store app 里显示的是同一份数据）。

只用 Python 3 标准库，无需安装依赖。

  python3 ns_play_history.py login    # 一次性：在浏览器登录任天堂账号 → 粘贴授权链接 → 保存登录凭证（约两年有效）
  python3 ns_play_history.py fetch    # 读取全部游玩记录，存成 play_histories.json 并打印排行

登录凭证存在 ~/.ns-play-history/（目录 700、文件 600），等同于账号凭证，请勿外传。
该接口没有公开文档，可能随时变化；请只用于查看你自己的账号。
"""

import base64
import getpass
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# 任天堂账号登录：使用 Nintendo Store app 的登录入口，所以授权页会显示「关联到 Nintendo Store」
CLIENT_ID = "5c38e31cd085304b"
REDIRECT_URI = f"npf{CLIENT_ID}://auth"
SCOPE = "openid user user.mii user.email user.links[].id"
ACCOUNTS = "https://accounts.nintendo.com/connect/1.0.0"

# Nintendo Store app 读取游玩记录的接口；gentry-locale 头必填（决定游戏名的语言）
API = "https://app-api.znej.nintendo.com/api/v2.0/users/me/play_histories"
LOCALE = os.environ.get("NS_LOCALE", "en-US")
USER_AGENT = "ns-play-history/1.0"

HOME = Path.home() / ".ns-play-history"


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def save_secret(name: str, obj: dict) -> None:
    HOME.mkdir(mode=0o700, exist_ok=True)
    fd = os.open(HOME / name, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f)


def load_secret(name: str):
    p = HOME / name
    return json.loads(p.read_text()) if p.exists() else None


def request(method: str, url: str, headers: dict, body: bytes = None):
    req = urllib.request.Request(url, data=body, method=method, headers={"User-Agent": USER_AGENT, **headers})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def login() -> None:
    verifier = b64url(os.urandom(32))
    state = b64url(os.urandom(36))
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    url = f"{ACCOUNTS}/authorize?" + urllib.parse.urlencode({
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "response_type": "session_token_code",
        "session_token_code_challenge": challenge,
        "session_token_code_challenge_method": "S256",
    })
    print("1) 用浏览器打开下面的链接，登录你的任天堂账号：\n")
    print(url)
    print("\n2) 出现「Select this account / 选择此人」时【不要点按钮】。")
    print("   在按钮上右键 → 复制链接地址；或按 F12 打开控制台，执行：")
    print("   copy(document.getElementById('authorize-switch-approval-link').href)")
    print(f"   复制到的应以 {REDIRECT_URI}# 开头。\n")
    link = getpass.getpass("3) 粘贴授权链接（输入不回显）：").strip()

    if not link.startswith(REDIRECT_URI + "#"):
        sys.exit("这不是授权链接：应以 " + REDIRECT_URI + "# 开头（别复制成地址栏）")
    frag = urllib.parse.parse_qs(link.split("#", 1)[1])
    if frag.get("state", [None])[0] != state:
        sys.exit("state 不匹配：请用本次打印的链接重新登录")
    code = frag["session_token_code"][0]

    status, body = request("POST", f"{ACCOUNTS}/api/session_token", {
        "Content-Type": "application/x-www-form-urlencoded",
    }, urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "session_token_code": code,
        "session_token_code_verifier": verifier,
    }).encode())
    if status != 200:
        sys.exit(f"保存登录失败：HTTP {status} {body[:200]!r}")
    save_secret("session.json", {"session_token": json.loads(body)["session_token"]})
    print(f"\n✅ 登录完成，凭证已存到 {HOME}/session.json（约两年有效）。接下来运行：python3 {sys.argv[0]} fetch")


def access_token() -> str:
    cached = load_secret("access.json")
    if cached and cached["expires_at"] > time.time() + 60:
        return cached["token"]
    session = load_secret("session.json")
    if not session:
        sys.exit("还没登录：先运行 login")
    status, body = request("POST", f"{ACCOUNTS}/api/token", {
        "Content-Type": "application/json; charset=utf-8",
    }, json.dumps({
        "client_id": CLIENT_ID,
        "session_token": session["session_token"],
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer-session-token",
    }).encode())
    if status != 200:
        sys.exit(f"获取访问凭证失败：HTTP {status} {body[:200]!r}（登录过期的话重新 login）")
    data = json.loads(body)
    save_secret("access.json", {"token": data["access_token"], "expires_at": time.time() + data.get("expires_in", 900)})
    return data["access_token"]


def fetch() -> None:
    status, body = request("GET", API, {
        "Authorization": f"Bearer {access_token()}",
        "Accept": "application/json",
        "gentry-locale": LOCALE,
    })
    if status != 200:
        sys.exit(f"HTTP {status} {body[:300]!r}")
    Path("play_histories.json").write_bytes(body)
    data = json.loads(body)
    games = sorted(data.get("playHistories", []), key=lambda g: -g.get("totalPlayedMinutes", 0))
    print(f"共 {len(games)} 个游戏，已保存到 play_histories.json\n")
    for i, g in enumerate(games[:20], 1):
        print(f"{i:>3}. {g['totalPlayedMinutes'] / 60:7.1f} h  {g['totalPlayedDays']:>4} 天  "
              f"{g['firstPlayedAt'][:10]} → {g['lastPlayedAt'][:10]}  {g['titleName']}")


if __name__ == "__main__":
    {"login": login, "fetch": fetch}.get((sys.argv[1:] or [""])[0], lambda: sys.exit(__doc__))()
