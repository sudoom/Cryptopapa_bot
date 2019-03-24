import json
import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Filters, BaseFilter, Updater,
                          MessageHandler, CommandHandler, CallbackQueryHandler)

updater = Updater(token="")
satoshi = 0.00000001
gb = 1024**3
vol = 10**-18
ud = updater.dispatcher


class Filter_error(BaseFilter):
    def filter(self, message):
        return len(message.text) != 34, 42, 64, 66


_filter_error = Filter_error()


def fil_err(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="This is not a valid format of address or a transaction hash, check if it's correct.\n",
        reply_markup=err_keyboard()
    )

############################### KEYBOARDS ###############################


def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Bitcoin", callback_data="btc")],
        [InlineKeyboardButton("Ethereum", callback_data="eth")]
    ]
    return InlineKeyboardMarkup(keyboard)


def eth_keyboard():
    keyboard = [
        [InlineKeyboardButton("Price", callback_data="price_eth")],
        [InlineKeyboardButton("Blockchain status", callback_data="block_eth")],
        [InlineKeyboardButton("Check Transaction", callback_data="tran_eth")],
        [InlineKeyboardButton("Check Address", callback_data="addr_eth")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def sub_btc_keyboard():
    keyboard = [
        [InlineKeyboardButton("Back to Bitcoin Menu", callback_data="btc")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def sub_eth_keyboard():
    keyboard = [
        [InlineKeyboardButton("Back to Ethereum Menu", callback_data="eth")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def err_keyboard():
    keyboard = [
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def btc_keyboard():
    keyboard = [
        [InlineKeyboardButton("Price", callback_data="price_btc")],
        [InlineKeyboardButton("Blockchain status", callback_data="block_btc")],
        [InlineKeyboardButton("Check Transaction", callback_data="tran_btc")],
        [InlineKeyboardButton("Check Address", callback_data="addr_btc")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def startCommandText(bot, update):
    usr_name = update.message.from_user.first_name
    if update.message.from_user.last_name:
        usr_name += ' ' + update.message.from_user.last_name
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Hello, " + usr_name + ". Take your seat and we are going to the moon!\n",
        reply_markup=main_keyboard()
    )


def main_menu(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=main_menu_message(),
        reply_markup=main_keyboard()
    )


def main_menu_message():
    return "Choose crypto, Hamster"


def btc_menu(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=btc_menu_message(),
        reply_markup=btc_keyboard()
    )


def btc_menu_message():
    return "Choose Bitcoin operations"


def eth_menu(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=eth_menu_message(),
        reply_markup=eth_keyboard()
    )


def eth_menu_message():
    return "Choose Ethereum operations"
############################### BTC CHECK ###############################


def price_BTC(bot, update):
    query = update.callback_query
    link = 'https://api.blockchair.com/bitcoin/stats'
    get = requests.get(link)
    to_json = get.json()
    mpu = round(to_json["data"]["market_price_usd"], 2)
    mpu24hc = round(
        to_json["data"]["market_price_usd_change_24h_percentage"], 2)
    mcu = str("{:,}").format((to_json["data"]["market_cap_usd"]))
    mdp = to_json["data"]["market_dominance_percentage"]
    atfu = round(to_json["data"]["average_transaction_fee_usd_24h"], 2)
    volume_24h = str("{:,}").format(
        round((satoshi*(float(to_json["data"]["volume_24h"]))*mpu), 2))
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"<b>Market price:</b> <code>{mpu} USD</code>" + "\n"
        f"<b>Market price USD 24h change:</b> <code>{mpu24hc}%</code>" + "\n"
        f"<b>Market cap:</b> <code>{mcu} USD</code>" + "\n"
        f"<b>Market dominance:</b> <code>{mdp}%</code>" + "\n"
        f"<b>Average transaction fee:</b> <code>{atfu} USD</code>" + "\n"
        f"<b>Volume 24h:</b> <code>{volume_24h} USD</code>",
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=sub_btc_keyboard()
    )


def blockchain_status_BTC(bot, update):
    query = update.callback_query
    link = 'https://api.blockchair.com/bitcoin/stats'
    get = requests.get(link)
    to_json = get.json()
    block_24 = to_json["data"]["blocks_24h"]
    trans_24 = to_json["data"]["transactions_24h"]
    lbf = to_json["data"]["best_block_time"]
    mempool_trans = to_json["data"]["mempool_transactions"]
    mptfu = round(to_json["data"]["mempool_total_fee_usd"], 2)
    cs = str("{:,}").format(
        round(satoshi*(float(to_json["data"]["circulation"])), 2))
    nodes = to_json["data"]["nodes"]
    bc_size = round((int(to_json["data"]["blockchain_size"])/gb), 2)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"<b>Block 24h:</b> <code>{block_24}</code>" + "\n"
        f"<b>Transaction 24h:</b> <code>{trans_24}</code>" + "\n"
        f"<b>Last block found:</b> <code>{lbf} UTC</code>" + "\n"
        f"<b>Mempool transaction:</b> <code>{mempool_trans}</code>" + "\n"
        f"<b>Mempool total fee:</b> <code>{mptfu} USD</code>" + "\n"
        f"<b>Circulation supply:</b> <code>{cs} / 21,000,000 BTC</code>" + "\n"
        f"<b>Nodes:</b> <code>{nodes}</code>" + "\n"
        f"<b>Blockchain size:</b> <code>{bc_size} GB</code>",
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=sub_btc_keyboard()
    )


def address_BTC(bot, update):
    address = update.message.text
    link = "https://api.blockchair.com/bitcoin/dashboards/address/"
    get_address = requests.get(link+address)
    to_json = get_address.json()
    if type(to_json["data"][address]["address"]["type"]) != str:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Wow, such empty from address btc",
            reply_markup=sub_btc_keyboard()
        )
    else:
        conv = to_json["data"][address]["address"]["balance"]
        final = satoshi*float(conv)
        rec = to_json["data"][address]["address"]["received_usd"]
        bal = to_json["data"][address]["address"]["balance_usd"]
        spen = to_json["data"][address]["address"]["spent_usd"]
        tbbtc = str("{:,}").format(round(final, 8))
        tbusd = str("{:,}").format(round(bal, 2))
        trusd = str("{:,}").format(round(rec, 2))
        tsusd = str("{:,}").format(round(spen, 2))
        t = to_json["data"][address]["address"]["transaction_count"]
        profit = round((((spen-rec+bal)/rec)*100), 3)
        lt = to_json["data"][address]["transactions"][0]
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"<b>Total Balance:</b> <code>{tbbtc} BTC</code>" + "\n"
            f"<b>Total Balance:</b> <code>{tbusd} USD</code>" + "\n"
            f"<b>Total Recieved:</b> <code>{trusd} USD</code>" + "\n"
            f"<b>Total Spend:</b> <code>{tsusd} USD</code>" + "\n"
            f"<b>Transactions:</b> <code>{t}</code>" + "\n"
            f"<b>Last transaction:</b> <code>{lt}</code>" + "\n"
            f"<b>Profit:</b> <code>{profit}%</code>",
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=sub_btc_keyboard()
        )


def tran_BTC(bot, update):
    tran = update.message.text
    link = "https://api.blockchair.com/bitcoin/dashboards/transaction/"
    get_tran = requests.get(link+tran)
    to_json = get_tran.json()
    if type(to_json["data"]) != dict:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Wow, such empty in transaction btc",
            reply_markup=sub_btc_keyboard()
        )
    else:
        block = to_json["data"][tran]["transaction"]["block_id"]
        time = to_json["data"][tran]["transaction"]["time"]
        con_state = to_json["context"]["state"]
        conf = con_state - block
        size = (to_json["data"][tran]["transaction"]["size"])/1000
        itu = str("{:,}").format(to_json["data"]
                                 [tran]["transaction"]["input_total_usd"])
        otu = str("{:,}").format(to_json["data"]
                                 [tran]["transaction"]["output_total_usd"])
        fee = to_json["data"][tran]["transaction"]["fee_usd"]
        feep = round((fee/(to_json["data"][tran]["transaction"]
                           ["input_total_usd"])) * 100, 4)
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"<b>Block:</b> <code>{block}</code>" + "\n"
            f"<b>Time:</b> <code>{time} UTC</code>" + "\n"
            f"<code>{conf}</code> <b>Confiramations</b>" + "\n"
            f"<b>Size:</b> <code>{size} Bytes</code>" + "\n"
            f"<b>Total input:</b> <code>{itu} USD</code>" + "\n"
            f"<b>Total output:</b> <code>{otu} USD</code>" + "\n"
            f"<b>Fee:</b> <code>{fee} USD</code>" + "\n"
            f"<b>Fee/Input:</b> <code>{feep} %</code>",
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=sub_btc_keyboard()
        )


def check_address_BTC(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Send me the Bitcoin address for check the balance",
        reply_markup=sub_btc_keyboard()
    )


def check_transaction_BTC(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Send me the Bitcoin transaction",
        reply_markup=sub_btc_keyboard()
    )

############################### ETH CHECk ###############################


def price_ETH(bot, update):
    query = update.callback_query
    link = 'https://api.blockchair.com/ethereum/stats'
    get = requests.get(link)
    to_json = get.json()
    mpu = round(to_json["data"]["market_price_usd"], 2)
    mpu24hc = round(
        to_json["data"]["market_price_usd_change_24h_percentage"], 2)
    mcu = str("{:,}").format((to_json["data"]["market_cap_usd"]))
    mdp = to_json["data"]["market_dominance_percentage"]
    atfu = round(to_json["data"]["average_transaction_fee_usd_24h"], 2)
    volume_24h = str("{:,}").format(
        round((vol*(float(to_json["data"]["volume_24h_approximate"]))*mpu), 2))
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"<b>Market price:</b> <code>{mpu} USD</code>" + "\n"
        f"<b>Market price USD 24h change:</b> <code>{mpu24hc}%</code>" + "\n"
        f"<b>Market cap:</b> <code>{mcu} USD</code>" + "\n"
        f"<b>Market dominance:</b> <code>{mdp}%</code>" + "\n"
        f"<b>Average transaction fee:</b> <code>{atfu} USD</code>" + "\n"
        f"<b>Volume 24h:</b> <code>{volume_24h} USD</code>",
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=sub_eth_keyboard()
    )


def blockchain_status_ETH(bot, update):
    query = update.callback_query
    link = 'https://api.blockchair.com/ethereum/stats'
    get = requests.get(link)
    to_json = get.json()
    block_24 = str(to_json["data"]["blocks_24h"])
    trans_24 = str(to_json["data"]["transactions_24h"])
    lbf = str(to_json["data"]["best_block_time"])
    mempool_trans = str(to_json["data"]["mempool_transactions"])
    bc_size = str(round((int(to_json["data"]["blockchain_size"])/gb), 2))
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"<b>Block 24h:</b> <code>{block_24}</code>" + "\n"
        f"<b>Transaction 24h:</b> <code>{trans_24}</code>" + "\n"
        f"<b>Last block found:</b> <code>{lbf} UTC</code>" + "\n"
        f"<b>Mempool transaction:</b> <code>{mempool_trans}</code>" + "\n"
        f"<b>Blockchain size:</b> <code>{bc_size} GB</code>",
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=sub_eth_keyboard()
    )


def address_ETH(bot, update):
    address = update.message.text
    link = "https://api.blockchair.com/ethereum/dashboards/address/"
    get_address = requests.get(link+address)
    to_json = get_address.json()
    if type(to_json["data"][address]["address"]["type"]) != str:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Wow, such empty in address ETH",
            reply_markup=sub_eth_keyboard()
        )
    else:
        conv = to_json["data"][address]["address"]["balance"]
        final = vol*float(conv)
        rec = to_json["data"][address]["address"]["received_usd"]
        bal = to_json["data"][address]["address"]["balance_usd"]
        spen = to_json["data"][address]["address"]["spent_usd"]
        tbltc = str("{:,}").format(round(final, 3))
        tbusd = str("{:,}").format(round(bal, 2))
        trusd = str("{:,}").format(round(rec, 2))
        tsusd = str("{:,}").format(round(spen, 2))
        t = to_json["data"][address]["address"]["transaction_count"]
        profit = round((((spen-rec+bal)/rec)*100), 3)
        lt = to_json["data"][address]["calls"][0]["transaction_hash"]
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"<b>Total Balance:</b> <code>{tbltc} ETH</code>" + "\n"
            f"<b>Total Balance:</b> <code>{tbusd} USD</code>" + "\n"
            f"<b>Total Recieved:</b> <code>{trusd} USD</code>" + "\n"
            f"<b>Total Spend:</b> <code>{tsusd} USD</code>" + "\n"
            f"<b>Transactions:</b> <code>{t}</code>" + "\n"
            f"<b>Last transaction:</b> <code>{lt}</code>" + "\n"
            f"<b>Profit:</b> <code>{profit}%</code>",
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=sub_eth_keyboard()
        )


def tran_ETH(bot, update):
    tran = update.message.text
    link = "https://api.blockchair.com/ethereum/dashboards/transaction/"
    get_tran = requests.get(link+tran)
    to_json = get_tran.json()
    if type(to_json["data"]) != dict:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Wow, such empty in transaction ETH",
            reply_markup=sub_eth_keyboard()
        )
    else:
        ivu = round(to_json["data"][tran]["transaction"]
                    ["internal_value_usd"], 2)
        block = to_json["data"][tran]["transaction"]["block_id"]
        time = to_json["data"][tran]["transaction"]["time"]
        con_state = to_json["context"]["state"]
        conf = con_state - block
        itu = str("{:,}").format(ivu)
        fee = round(to_json["data"][tran]["transaction"]["fee_usd"], 2)
        feep = round((fee/ivu) * 100, 4)
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"<b>Block:</b> <code>{block}</code>" + "\n"
            f"<b>Time:</b> <code>{time} UTC</code>" + "\n"
            f"<code>{conf}</code> <b>Confiramations</b>" + "\n"
            f"<b>Total input:</b> <code>{itu} USD</code>" + "\n"
            f"<b>Fee:</b> <code>{fee} USD</code>" + "\n"
            f"<b>Fee/Input:</b> <code>{feep} %</code>",
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=sub_eth_keyboard()
        )


def check_address_ETH(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Send me the Ethereum address for check the balance",
        reply_markup=sub_eth_keyboard()
    )


def check_transaction_ETH(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Send me the Ethereum transaction",
        reply_markup=sub_eth_keyboard()
    )


############################### ETH HANDLER ###############################
############################### MESSAGE HANDLERS ###############################
ud.add_handler(MessageHandler(Filters.regex('^0x[0-9a-z]{64}$'), tran_ETH))
ud.add_handler(MessageHandler(Filters.regex('^0x[0-9a-z]{40}$'), address_ETH))


############################### KEYBOARD HANDLERS ###############################
ud.add_handler(CallbackQueryHandler(eth_menu, pattern='^eth$'))
ud.add_handler(CallbackQueryHandler(price_ETH, pattern='^price_eth$'))
ud.add_handler(CallbackQueryHandler(
    blockchain_status_ETH, pattern='^block_eth$'))
ud.add_handler(CallbackQueryHandler(check_address_ETH, pattern='^addr_eth$'))
ud.add_handler(CallbackQueryHandler(
    check_transaction_ETH, pattern='^tran_eth$'))


############################### BTC HANDLER ###############################
############################### MESSAGE HANDLERS ###############################
ud.add_handler(MessageHandler(Filters.regex('^[0-9a-z]{64}$'), tran_BTC))
ud.add_handler(MessageHandler(Filters.regex(
    '(^3\w{33}$|^1\w{33}$)'), address_BTC))


############################### KEYBOARD HANDLERS ###############################
ud.add_handler(CallbackQueryHandler(btc_menu, pattern='^btc$'))
ud.add_handler(CallbackQueryHandler(price_BTC, pattern='^price_btc$'))
ud.add_handler(CallbackQueryHandler(
    blockchain_status_BTC, pattern='^block_btc$'))
ud.add_handler(CallbackQueryHandler(check_address_BTC, pattern='^addr_btc$'))
ud.add_handler(CallbackQueryHandler(
    check_transaction_BTC, pattern='^tran_btc$'))


############################### UTILS HANDLER ###############################
ud.add_handler(CommandHandler('start', startCommandText))
ud.add_handler(CallbackQueryHandler(main_menu, pattern='^main$'))
ud.add_handler(MessageHandler(_filter_error, fil_err))
updater.start_polling()
updater.idle()
