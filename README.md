# Slack ピン留めボット

## 概要
- Slackに投稿されたメッセージ内に指定した語句が含まれていた場合、そのメッセージをピン留めするボットです。

## ボットの権限
- Bot Token Scopesとして下記の権限が必要
  - channels:history
  - chat:write
  - files:read
  - files:write
  - groups:history
  - im:history
  - mpim:history
  - pins:write

## 使い方
- `.env`に環境変数としてトークンやDB名を記入
- ボットの起動
```sh
# .venv の作成
python -m venv .venv

# activate
source .venv/bin/activate

# モジュールのインストール
pip install -r requirements.txt

# 実行
python app.py
```

- ピン留め条件の更新方法
  - `ピン留め条件`とメッセージを送るとボットから下記が返されるので、ここからピン留め条件の追加や削除を行う
  <img width="549" alt="image" src="https://github.com/koooommmm/kakeibo-app/assets/124126985/697b5467-2d4e-4144-9092-fd5d343e76e0">

