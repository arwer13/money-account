#!/usr/bin/env python3
import os
import sys
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import dropbox_stuff
import money
import config


dropbox_token = None
"""Dropbox token, should be loaded at startup time."""


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def handle_record(bot, update):
    text = update.message.text
    logging.info("Got message: {}".format(text))
    text_lines = text.splitlines()
    record_date = update.message.date if update.message.forward_date is None\
        else update.message.forward_date

    def message_line_to_txt_line(msg):
        categories = []
        money = 0
        for arg in filter(None, msg.replace(",", " ").split(" ")):
            try:
                float(arg)
                money = arg
            except ValueError:
                categories.append(arg)
        return "{} {} {}\n".format(record_date.strftime("%Y.%m.%d"), ", ".join(categories), money)

    data = dropbox_stuff.get_money_txt(dropbox_token)
    if data[-1] not in ["\r", "\n"]:
        data += "\n"
    for line in text_lines:
        data += message_line_to_txt_line(line)
    dropbox_stuff.set_money_txt(dropbox_token, data)


def error(bot, update, error):
    logging.error('Update "%s" caused error "%s"' % (update, error))


def start_bot(token):
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler([Filters.text], handle_record))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    logging.info("start polling")
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


def main():
    global dropbox_token
    print("STARTED")
    log_file = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".log"
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s",
                        datefmt="%Y.%m.%d %I:%M:%S")
    logging.info("Started")
    token = os.environ["MONEY_TXT_TELEGRAM_BOT_TOKEN"].strip('"')
    logging.info("Telegram token is found")
    dropbox_token = os.environ["MONEY_TXT_DROPBOX_TOKEN"]
    logging.info("Dropbox token is found")

    start_bot(token)


if __name__ == '__main__':
    main()
