# -*- coding: utf-8 -*-

import vkontakte
import vk_auth
import codecs
import sys
import time
import datetime

#############################

# vk login/password
login = 'example@example.com'
password = 'password'

# ID of the interlocutor
dialogue_id = 11111111

#############################
try:
    (token, user_id) = vk_auth.auth(login,
                                    password,
                                    '3842229',
                                    'messages')
except RuntimeError:
    sys.exit("Incorrect login/password. Please check it.")

vk = vkontakte.API(token=token)

print "vk autorized"

messages = vk.messages.getHistory(uid=dialogue_id)

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
human_details = vk.users.get(uids=','.join(str(v) for v in human_uids))


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
            message_part = vk.messages.getHistory(uid=dialogue_id,
                                                  offset=mess,
                                                  count=max_part,
                                                  rev=1)
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
