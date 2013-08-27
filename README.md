# vk-dialogue-export.py
## VKontakte Dialogue Exporter

A tool to export dialogue with specific interlocutor.

## USAGE

Install requirements from requirements.txt

Edit vk-dialogue-export.py file and run.
At the top of script:

	#############################

	# vk login/password
	login = 'example@yandex.com'
	password = 'password'

	# ID of the interlocutor
	dialog_id = 111111111

	#############################


### NOTES

Script uses [https://github.com/dzhioev/vk_api_auth](https://github.com/dzhioev/vk_api_auth) to simplify business with OAuth.