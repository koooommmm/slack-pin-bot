import argparse
import os
import re
import sqlite3

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()
app = App(token=os.environ["SLACK_BOT_TOKEN"])
DB_NAME = os.environ["DB_NAME"]

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file")


def init_db(init_keywords):
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS keywords(keyword text unique)")

        cur.executemany(
            "INSERT OR IGNORE INTO keywords VALUES (?)", init_keywords
        )
        con.commit()


def get_regexp_keywords():
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        res = cur.execute("SELECT keyword FROM keywords")

    keywords = list(map(lambda keyword: keyword[0], res.fetchall()))

    return "|".join(keywords) if keywords else "[]"


@app.event("message")
def handle_message_events(body, say, client):
    text = body["event"]["text"]
    channel = body["event"]["channel"]
    timestamp = body["event"]["ts"]
    regexp_keywords = get_regexp_keywords()
    if text == "ピン留め条件":
        config_target_words(say)
    elif regexp_keywords != "[]" and re.findall(
        re.compile(regexp_keywords, re.IGNORECASE), text
    ):
        client.pins_add(channel=channel, timestamp=timestamp)


def config_target_words(say):
    regexp_keywords = get_regexp_keywords()

    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*現在のピン留め条件*\n```{regexp_keywords}\n```",
                },
            },
            {
                "dispatch_action": True,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "add_keyword",
                },
                "label": {
                    "type": "plain_text",
                    "text": "ピン留め条件を追加",
                },
            },
            {
                "dispatch_action": True,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "delete_keyword",
                },
                "label": {
                    "type": "plain_text",
                    "text": "ピン留め条件を削除",
                },
            },
        ],
        text="test",
    )


@app.action("add_keyword")
def add_keyword(ack, payload, say):
    ack()

    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO keywords VALUES (?)", (payload["value"],)
        )
        con.commit()

    regexp_keywords = get_regexp_keywords()

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"ピン留め条件を更新しました。\n```\n{regexp_keywords}\n```",
            },
        }
    ]
    say(blocks=blocks, text="ピン留め条件を更新しました。")


@app.action("delete_keyword")
def delete_keyword(ack, payload, say):
    ack()

    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute(
            "DELETE FROM keywords WHERE keyword = ?", (payload["value"],)
        )
        con.commit()

    regexp_keywords = get_regexp_keywords()

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"ピン留め条件を更新しました。\n```\n{regexp_keywords}\n```",
            },
        }
    ]
    say(blocks=blocks, text="ピン留め条件を更新しました。")


# アプリを起動します
if __name__ == "__main__":
    args = parser.parse_args()
    init_keywords = []

    if args.file:
        with open(args.file, "r") as f:
            init_keywords = list(
                map(lambda keyword: (keyword,), f.read().split())
            )

    init_db(init_keywords)
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
