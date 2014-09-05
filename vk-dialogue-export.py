# -*- coding: utf-8 -*-

import vk_auth

import json
import urllib2
from urllib import urlencode

import codecs
import sys
import time
import datetime

import ConfigParser


Config = ConfigParser.ConfigParser()
Config.read("config.ini")

login = Config.get("auth", "username")
password = Config.get("auth", "password")
messages_id = Config.get("messages", "id")
messages_type = Config.get("messages", "type")

if messages_type == "interlocutor":
    is_chat = False
elif messages_type == "chat":
    is_chat = True
else:
    sys.exit("Messages type must be either interlocutor or chat.")

def api(method, params, token):
    params.append(("access_token", token))
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params))
    return json.loads(urllib2.urlopen(url).read())["response"]


try:
    (token, user_id) = vk_auth.auth(login,
                                    password,
                                    '3842229',
                                    'messages')
except RuntimeError:
    sys.exit("Incorrect login/password. Please check it.")

print "vk autorized"

selector = "uid" if not is_chat else "chat_id"
messages = api("messages.getHistory", [(selector, messages_id)], token)

cnt = messages[0]
print "Count of messages: %s" % cnt
time.sleep(1)

file_suffix = ('ui' if not is_chat else 'c')
filename = ('vk_exported_dialogue_' + file_suffix + "%s.txt") % messages_id
out = codecs.open(filename, "w+", "utf-8")

human_uids = []
human_uids.append(messages[1]["uid"])

# Export uids from dialogue.
# Due to vk.api, start from 1.
for i in range(1, 100):
    try:
        if messages[i]["uid"] != human_uids[0]:
            human_uids.append(messages[i]["uid"])
    except IndexError:
        pass

# Export details from uids
human_details = api("users.get",
                    [("uids", ','.join(str(v) for v in human_uids))],
                    token)
human_details_index = {}
for human_detail in human_details:
    human_details_index[human_detail["uid"]] = human_detail

def write_message(who, to_write):
    date = datetime.datetime.fromtimestamp(
        int(to_write["date"])).strftime('%Y-%m-%d %H:%M:%S')
    out.write("[" + date + "] " +
              human_details_index[who]["first_name"] +
              " " +
              human_details_index[who]["last_name"] +
              ":\n" +
              to_write["body"].replace('<br>', '\n') +
              '\n\n\n')

mess = 0
max_part = 200  # Due to vk.api
while mess != cnt:
    # Try to retrieve info anyway
    selector = "uid" if not is_chat else "chat_id"
    while True:
        try:
            message_part = api("messages.getHistory",
                               [(selector, messages_id),
                                ("offset", mess),
                                ("count", max_part),
                                ("rev", 1)],
                               token)
        except:
            continue
        break

    try:
        for i in range(1, 201):
            write_message(message_part[i]["uid"], message_part[i])
    except IndexError:
        break

    result = mess + max_part
    if result > cnt:
        result = (mess - cnt) + mess
    mess = result
    print "Exported %s messages of %s" % (mess, cnt)

out.close()
print "Export done!"
