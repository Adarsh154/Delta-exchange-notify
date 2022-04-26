import os
from datetime import datetime
import requests
from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters

token = os.getenv("ttoken")
updater = Updater(token,
                  use_context=True)
sticker_id = "CAACAgUAAxkBAAETZyJiaC5D_9ue30Ae6sHQ1SogU5s7fgACGQEAAqP7yVR9wpCHJCufxiQE"


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello sir, Welcome to the Bot.Please write help to see the commands available.")


def get_processes(update: Update, context: CallbackContext):
    running_process = os.popen("ps -aef | grep -i 'python3' | grep -v 'grep'").read().strip().split('\n')
    if not len(running_process) == 5:
        update.message.reply_text("Something not right, check processes---> Contact AJ")
        for process in running_process:
            update.message.reply_text(process)
    else:
        update.message.reply_text("ALL GOOD")
        url = "https://api.telegram.org/bot{}/sendSticker?chat_id={}&sticker={}".format(
            token, update.message.chat.id, sticker_id)
        _ = requests.get(url)


def check_processes(update: Update, context: CallbackContext):
    running_process = os.popen("ps -aef | grep -i 'python3' | grep -v 'grep'").read().strip().split('\n')
    for process in running_process:
        update.message.reply_text(process)


def get_logs(update: Update, context: CallbackContext):
    log_file_name = str(datetime.utcnow().strftime('%d_%m_%Y')) + '.log'
    chat_id = update.message.chat_id
    document = open(log_file_name, 'rb')
    context.bot.send_document(chat_id, document)


def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)


def unknown_text(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry I can't recognize you , you said '%s'" % update.message.text)


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('pp', get_processes))
updater.dispatcher.add_handler(CommandHandler('cp', check_processes))
updater.dispatcher.add_handler(CommandHandler('logs', get_logs))
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(
    Filters.command, unknown))  # Filters out unknown commands

# Filters out unknown messages.
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown_text))

updater.start_polling()
