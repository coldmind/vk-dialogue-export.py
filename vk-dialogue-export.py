# -*- coding: utf-8 -*-

import vk_auth

import json
import urllib2
from urllib import urlencode

import codecs
import sys
import time
import datetime


#############################

# vk login/password
login = 'example@yandex.com'
password = 'password'

# ID of the interlocutor
dialogue_id = 11111111

#############################


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

messages = api("messages.getHistory", [("uid", dialogue_id)], token)

cnt = messages[0]
print "Count of messages: %s" % cnt
time.sleep(1)

out = codecs.open('vk_exported_dialogue_ui%s.txt' % dialogue_id, "w+", "utf-8")

human_uids = []
human_uids.append(messages[1]["uid"])

# Export uids from dialogue.
# Due to vk.api, start from 1.
for i in range(1, 100):
    try:
        if messages[i]["uid"] != human_uids[0]:
            human_uids.append(messages[i]["uid"])
            break
    except IndexError:
        pass

# Export details from uids
human_details = api("users.get",
                    [("uids", ','.join(str(v) for v in human_uids))],
                    token)


def write_message(who, to_write):
    date = datetime.datetime.fromtimestamp(
        int(to_write["date"])).strftime('%Y-%m-%d %H:%M:%S')
    out.write("[" + date + "] " +
              human_details[who]["first_name"] +
              " " +
              human_details[who]["last_name"] +
              ":\n" +
              to_write["body"].replace('<br>', '\n') +
              '\n\n\n')

mess = 0
max_part = 200  # Due to vk.api
while mess != cnt:
    # Try to retrieve info anyway
    while True:
        try:
            message_part = api("messages.getHistory",
                               [("uid", dialogue_id),
                                ("offset", mess),
                                ("count", max_part),
                                ("rev", 1)],
                               token)
        except:
            continue
        break

    try:
        for i in range(1, 201):
            if message_part[i]["uid"] == human_uids[0]:
                write_message(0, message_part[i])
            else:
                write_message(1, message_part[i])
    except IndexError:
        break

    result = mess + max_part
    if result > cnt:
        result = (mess - cnt) + mess
    mess = result
    print "Exported %s messages of %s" % (mess, cnt)

out.close()
print "Export done!"
