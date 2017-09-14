# coding=utf-8
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, Job, CallbackQueryHandler
import logging
import random
import json
import datetime, time

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

with open('fooddata.json', 'r') as f:
    fooddata = json.load(f)

wishlist = fooddata['wishlist']
eatlist = fooddata['eatlist']


def start(bot, update):
    update.message.reply_text('114514')


def help(bot, update):
    update.message.reply_text('/list: show current lists\n' +
                              '/eatwut: food for today\n' +
                              '/add: add an option\n' +
                              '/remove: delete an option\n' +
                              '/list: show current lists\n' +
                              '/coin: flip a coin'
                              )


def list(bot, update):
    wish = ''
    eat = ''

    for x in wishlist:
        wish += (x + ' ')
    update.message.reply_text('wish list: ' + wish)
    for y in eatlist:
        eat += (y + ' ')
    update.message.reply_text('eat list: ' + eat)


def coin(bot, update):
    cases = ['正面', '反面']
    result = random.choice(cases)
    update.message.reply_text('%s 朝上' % result)


def eatwut(bot, update):
    id = str(update.message.chat_id)
    keyboard = [InlineKeyboardButton("eat out", callback_data='w ' + id),
                InlineKeyboardButton("eat nearby", callback_data='e ' + id)]
    reply_markup = InlineKeyboardMarkup([keyboard])
    update.message.reply_text('Choose range:', reply_markup=reply_markup)


def add(bot, update, args):
    newopt = args[0]
    logger.warning(args)
    id = str(update.message.chat_id)
    keyboard = [InlineKeyboardButton("wishlist", callback_data='wishlist ' + newopt + ' ' + id),
                InlineKeyboardButton("eatlist", callback_data='eatlist ' + newopt + ' ' + id)]
    reply_markup = InlineKeyboardMarkup([keyboard])
    update.message.reply_text('Choose target:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    if len(query.data.split(' ', 1)[0]) == 1:
        target, id = query.data.split(' ')
        id = int(id)
        if target == 'w':
            food = random.choice(wishlist)
        else:
            food = random.choice(eatlist)

        bot.send_message(chat_id=id, text='吃 %s' % food)
    else:
        target, newopt, id = query.data.split(' ')
        id = int(id)

        def opr(l):
            if newopt not in l:
                l.append(newopt)
                bot.send_message(chat_id=id, text='New one added!')
                renew('fooddata.json')
            else:
                bot.send_message(chat_id=id, text='Duplicate!')

        if target == 'wishlist':
            opr(wishlist)
        elif target == 'eatlist':
            opr(eatlist)


def remove(bot, update, args):
    todel = args[0]
    if todel in wishlist:
        wishlist.remove(todel)
        update.message.reply_text('Wish deleted!')
    elif todel in eatlist:
        eatlist.remove(todel)
        update.message.reply_text('Eat option deleted!')
    else:
        update.message.reply_text('Option not found')

    renew('fooddata.json')


def eat_alert(bot, job):
    curtime = time.gmtime().tm_hour
    if curtime in [0, 4, 10]:
        bot.send_message(chat_id=job.context, text='Time for eating!')


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def renew(output_json):
    fooddata = {
        'wishlist': wishlist,
        'eatlist': eatlist
    }
    with open(output_json, 'w') as f:
        json.dump(fooddata, f)


def main():
    updater = Updater(token='TOKEN')
    dp = updater.dispatcher
    j = updater.job_queue

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('coin', coin))
    dp.add_handler(CommandHandler('list', list))
    dp.add_handler(CommandHandler('eatwut', eatwut))
    dp.add_handler(CommandHandler('add', add, pass_args=True))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler('remove', remove, pass_args=True))
    dp.add_error_handler(error)

    job_mealy = Job(eat_alert, 600)
    j.put(job_mealy, next_t=0.0)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
