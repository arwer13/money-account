#!/usr/bin/env python3
import os
import sys
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import config
import money


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
        description_delimiter = 4 * " "
        parts = list(filter(None, msg.split(description_delimiter)))
        print(parts)
        description = parts[1].strip() if len(parts) > 1 else ""
        msg_without_description = parts[0]
        for arg in filter(None,
                          msg_without_description.replace(",", " ")
                          .split(" ")):
            try:
                float(arg)
                money = arg
            except ValueError:
                categories.append(arg)
        return "{} {} {} {}\n".format(
            record_date.strftime("%Y.%m.%d"),
            ", ".join(categories),
            money,
            description).strip()

    data = money.load_money_txt()
    if data[-1] not in ["\r", "\n"]:
        data += "\n"
    for line in text_lines:
        data += message_line_to_txt_line(line)
    money.save_money_txt(data)


def handle_last(bot, update):
    """Handle command "last" to show last records (default 10)."""
    logging.info('Got command "last"')
    data = money.load_money_txt()
    num_last_records = 10
    reply = "\n".join(list(filter(None, data.splitlines()))[-num_last_records:])
    bot.sendMessage(update.message.chat_id, text=reply)


def handle_info(bot, update):
    """Handle command "info" to show brief information."""
    logging.info('Got command "info"')
    df = money.load_df()
    value = money.get_total(df)
    reply = "Current value: {:.0f}".format(value)
    bot.sendMessage(update.message.chat_id, text=reply)


def handle_error(bot, update, error):
    logging.error('Update "%s" caused error "%s"' % (update, error))


def start_bot(token):
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("last", handle_last))
    dp.add_handler(CommandHandler("info", handle_info))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler([Filters.text], handle_record))

    # log all errors
    dp.add_error_handler(handle_error)

    # Start the Bot
    logging.info("start polling")
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


def main():
    # Logging setup.
    log_file_path = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".log"
    logging.basicConfig(filename=log_file_path, level=logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s",
                        datefmt="%Y.%m.%d %I:%M:%S")

    logging.info("Started")
    if config.telegram_bot_token is None:
        logging.error("Telegram token is not set up.")
    if config.dropbox_token is None:
        logging.error("Dropbox token is not set up.")
    start_bot(config.telegram_bot_token)


if __name__ == '__main__':
    main()
