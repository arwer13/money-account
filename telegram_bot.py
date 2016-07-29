#!/usr/bin/env python3
import os
import sys
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import dropbox_stuff




# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi!')


def echo(bot, update):
    logging.info("Got message: {}".format(update.message.text))

    def msg_to_line(msg):
        categories = []
        money = 0
        for arg in filter(None, msg.text.split()):
            try:
                float(arg)
                money = arg
            except ValueError:
                categories.append(arg)
        record_date = msg.date if msg.forward_date is None else msg.forward_date
        return "{} {} {}\n".format(record_date.strftime("%Y.%m.%d"), ", ".join(categories), money)

    data = dropbox_stuff.get_money_txt(dropbox_token)
    if data[-1] not in ["\r", "\n"]:
        data += "\n"
    data += msg_to_line(update.message)
    dropbox_stuff.set_money_txt(dropbox_token, data)

    bot.sendMessage(update.message.chat_id, text=update.message.text)


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
    dp.add_handler(MessageHandler([Filters.text], echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    logging.info("start polling")
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    log_file = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".log"
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y.%m.%d %I:%M:%S")
    token = os.environ["MONEY_TXT_TELEGRAM_BOT_TOKEN"].strip('"')

    dropbox_token = os.environ["MONEY_TXT_DROPBOX_TOKEN"]

    start_bot(token)
