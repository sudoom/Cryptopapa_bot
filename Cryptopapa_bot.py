import json
import requests
import telegram
import datetime
from pymongo import MongoClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Filters, BaseFilter, Updater,
                          MessageHandler, CommandHandler, CallbackQueryHandler)

updater = Updater(token="")

uri = "mongodb://user:pass@host:port/db"
client = MongoClient(uri)
db = client["db"]
mongo_coll = db["collection"]
satoshi = 0.00000001
gb = 1024**3
vol = 10**-18
ud = updater.dispatcher


############################### ERROR ###############################
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


def err_keyboard():
    keyboard = [
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


############################### DB ###############################
def get_user(usr_id):
    user = mongo_coll.find_one({"user_id": usr_id})
    return user


def get_addr_btc(usr_id):
    user = get_user(usr_id)
    address = user["wallets"]["btc"]
    return address


def find_addr_btc(addr, usr_id):
    address = mongo_coll.find_one({"user_id": usr_id, "wallets.btc": addr})
    return address


def get_addr_eth(usr_id):
    user = get_user(usr_id)
    address = user["wallets"]["eth"]
    return address


def find_addr_eth(addr, usr_id):
    address = mongo_coll.find_one({"user_id": usr_id, "wallets.eth": addr})
    return address


############################### KEYBOARDS ###############################
########################## MAIN MENU ##########################
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Bitcoin", callback_data="btc")],
        [InlineKeyboardButton("Ethereum", callback_data="eth")]
    ]
    return InlineKeyboardMarkup(keyboard)


def main_menu(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Choose crypto, Hamster",
        reply_markup=main_keyboard()
    )


def startCommandText(bot, update):
    usr_name = update.message.from_user.first_name
    usr_id = update.message.from_user.id
    usr_username = update.message.from_user.username
    usr_lng = update.message.from_user.language_code
    if update.message.from_user.last_name:
        usr_name += ' ' + update.message.from_user.last_name
    usr_obj = get_user(usr_id)
    if not usr_obj:
        add_user = mongo_coll.insert_one(
            {
                "user_name": usr_name,
                "user_id": usr_id,
                "user_username": usr_username,
                "user_language": usr_lng,
                "wallets": {
                    "btc": [],
                    "eth": []
                },
                "auth": datetime.datetime.utcnow()
            }
        )
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Hello, " + usr_name + ". Take your seat and we are going to the moon!\n",
        reply_markup=main_keyboard()
    )


########################## BTC MENU ##########################
def btc_keyboard():
    keyboard = [
        [InlineKeyboardButton("Price", callback_data="price_btc")],
        [InlineKeyboardButton("Blockchain status", callback_data="block_btc")],
        [InlineKeyboardButton("Check Transaction", callback_data="tran_btc")],
        [InlineKeyboardButton("Address operations", callback_data="addr_btc")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def btc_menu(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Choose Bitcoin operations",
        reply_markup=btc_keyboard()
    )


def sub_btc_keyboard():
    keyboard = [
        [InlineKeyboardButton("Back to Bitcoin Menu", callback_data="btc")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


##################### BTC ADDRESS MENU #####################
def btc_addr_keyboard():
    keyboard = [
        [InlineKeyboardButton("Add Address", callback_data="btc_add_addr")],
        [InlineKeyboardButton(
            "Check Address", callback_data="btc_check_addr")],
        [InlineKeyboardButton("Delete Address", callback_data="btc_del_addr")],
        [InlineKeyboardButton("Back to Bitcoin Menu", callback_data="btc")]
    ]
    return InlineKeyboardMarkup(keyboard)


def btc_addr_menu(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Choose Address operation",
        reply_markup=btc_addr_keyboard()
    )


def sub_btc_addr_keyboard():
    keyboard = [
        [InlineKeyboardButton("Back to Bitcoin Address Menu",
                              callback_data='addr_btc')],
        [InlineKeyboardButton("Back to Bitcoin Menu", callback_data="btc")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


########################## ETH MENU ##########################
def eth_keyboard():
    keyboard = [
        [InlineKeyboardButton("Price", callback_data="price_eth")],
        [InlineKeyboardButton("Blockchain status", callback_data="block_eth")],
        [InlineKeyboardButton("Check Transaction", callback_data="tran_eth")],
        [InlineKeyboardButton("Address operations", callback_data="addr_eth")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def eth_menu(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Choose Ethereum operations",
        reply_markup=eth_keyboard()
    )


def sub_eth_keyboard():
    keyboard = [
        [InlineKeyboardButton("Back to Ethereum Menu", callback_data="eth")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


##################### ETH ADDRESS MENU #####################
def eth_addr_keyboard():
    keyboard = [
        [InlineKeyboardButton("Add Address", callback_data="eth_add_addr")],
        [InlineKeyboardButton(
            "Check Address", callback_data="eth_check_addr")],
        [InlineKeyboardButton("Delete Address", callback_data="eth_del_addr")],
        [InlineKeyboardButton("Back to Ethereum Menu", callback_data="eth")]
    ]
    return InlineKeyboardMarkup(keyboard)


def eth_addr_menu(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Choose Address operation",
        reply_markup=eth_addr_keyboard()
    )


def sub_eth_addr_keyboard():
    keyboard = [
        [InlineKeyboardButton("Back to Ethereum Address Menu",
                              callback_data='addr_eth')],
        [InlineKeyboardButton("Back to Ethereum Menu", callback_data="eth")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main")]
    ]
    return InlineKeyboardMarkup(keyboard)


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


def add_addr_BTC(bot, update):
    text = update.message.text
    usr_id = update.message.from_user.id
    link = "https://api.blockchair.com/bitcoin/dashboards/address/"
    get_addr = requests.get(link+text)
    to_json = get_addr.json()
    if type(to_json["data"][text]["address"]["type"]) != str:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="You write wrong address, please check it",
            reply_markup=sub_btc_addr_keyboard()
        )
    else:
        if not find_addr_btc(text, usr_id):
            edit_user = mongo_coll.update_one(
                {
                    "user_id": usr_id
                },
                {
                    '$addToSet': {
                        "wallets.btc": text
                    }
                }
            )
            bot.send_message(
                chat_id=update.message.chat_id,
                text=f"Address <code>{text}</code> succesfully update",
                parse_mode=telegram.ParseMode.HTML,
                reply_markup=sub_btc_addr_keyboard()
            )
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="This Address has been already added earlier",
                reply_markup=sub_btc_addr_keyboard()
            )


def check_addr_BTC(bot, update):
    query = update.callback_query
    usr_id = query.from_user.id
    all_addr = get_addr_btc(usr_id)
    if all_addr == []:
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Please add bitcoin address first",
            reply_markup=sub_btc_addr_keyboard()
        )
    else:
        keyboard = []
        i = 0
        for db_addd in get_addr_btc(usr_id):
            keyboard.append(
                [InlineKeyboardButton(db_addd, callback_data="check_btc_"+db_addd)])
            i += 1
        keyboard.append(
            [InlineKeyboardButton("Back to Bitcoin Address Menu",
                                  callback_data='addr_btc')])
        markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Choose your address",
            reply_markup=markup
        )


def print_addr_BTC(bot, update):
    query = update.callback_query
    addr = query.data[10:]
    link = "https://api.blockchair.com/bitcoin/dashboards/address/"
    get_addr = requests.get(link+addr)
    to_json = get_addr.json()
    conv = to_json["data"][addr]["address"]["balance"]
    final = satoshi*float(conv)
    rec = to_json["data"][addr]["address"]["received_usd"]
    bal = to_json["data"][addr]["address"]["balance_usd"]
    spen = to_json["data"][addr]["address"]["spent_usd"]
    tbbtc = str("{:,}").format(round(final, 8))
    tbusd = str("{:,}").format(round(bal, 2))
    trusd = str("{:,}").format(round(rec, 2))
    tsusd = str("{:,}").format(round(spen, 2))
    t = to_json["data"][addr]["address"]["transaction_count"]
    profit = round((((spen-rec+bal)/rec)*100), 3)
    lt = to_json["data"][addr]["transactions"][0]
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"<b>Total Balance:</b> <code>{tbbtc} BTC</code>" + "\n"
        f"<b>Total Balance:</b> <code>{tbusd} USD</code>" + "\n"
        f"<b>Total Recieved:</b> <code>{trusd} USD</code>" + "\n"
        f"<b>Total Spend:</b> <code>{tsusd} USD</code>" + "\n"
        f"<b>Transactions:</b> <code>{t}</code>" + "\n"
        f"<b>Last transaction:</b> <code>{lt}</code>" + "\n"
        f"<b>Profit:</b> <code>{profit}%</code>",
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=sub_btc_addr_keyboard()
    )


def delete_addr_BTC(bot, update):
    query = update.callback_query
    usr_id = query.from_user.id
    all_addr = get_addr_btc(usr_id)
    if not all_addr == []:
        keyboard = []
        i = 0
        for db_addd in get_addr_btc(usr_id):
            keyboard.append(
                [InlineKeyboardButton(db_addd, callback_data="del_btc_" + db_addd)])
            i += 1
        keyboard.append(
            [InlineKeyboardButton("Back to Bitcoin Address Menu",
                                  callback_data='addr_btc')])
        markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Choose your address",
            reply_markup=markup
        )
    else:
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Your Address list was empty",
            reply_markup=sub_btc_addr_keyboard()
        )


def show_del_addr_BTC(bot, update):
    query = update.callback_query
    usr_id = query.from_user.id
    addr = query.data[8:]
    edit_user = mongo_coll.update_one(
        {
            "user_id": usr_id
        },
        {
            '$pull': {
                "wallets.btc": addr
            }
        }
    )
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f'Address <code>{addr}</code> succesfully delete',
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=sub_btc_addr_keyboard()
    )


def tran_BTC(bot, update):
    tran = update.message.text
    link = "https://api.blockchair.com/bitcoin/dashboards/transaction/"
    get_tran = requests.get(link+tran)
    to_json = get_tran.json()
    if type(to_json["data"]) != dict:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="You write wrong transaction, please check it",
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


def add_addr_BTC_message(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Send me the Bitcoin address for check the balance",
        reply_markup=sub_btc_addr_keyboard()
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


def add_addr_ETH(bot, update):
    text = update.message.text
    l_text = text.lower()
    usr_id = update.message.from_user.id
    addr = get_addr_eth(usr_id)
    l_addr = []
    for all_addr in addr:
        l_addr.append(all_addr.lower())
    link = "https://api.blockchair.com/ethereum/dashboards/address/"
    get_addr = requests.get(link+text)
    to_json = get_addr.json()
    if type(to_json["data"][l_text]["address"]["type"]) != str:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="You write wrong address, please check it",
            reply_markup=sub_eth_addr_keyboard()
        )
    elif l_text in l_addr:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="This Address has been already added earlier",
            reply_markup=sub_eth_addr_keyboard()
        )
    elif not find_addr_eth(text, usr_id):
        edit_user = mongo_coll.update_one(
            {
                "user_id": usr_id
            },
            {
                '$addToSet': {
                    "wallets.eth": text
                }
            }
        )
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Address <code>{text}</code> succesfully update",
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=sub_eth_addr_keyboard()
        )


def check_addr_ETH(bot, update):
    query = update.callback_query
    usr_id = query.from_user.id
    all_addr = get_addr_eth(usr_id)
    if all_addr == []:
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Please add Ethereum address first",
            reply_markup=sub_eth_addr_keyboard()
        )
    else:
        keyboard = []
        i = 0
        for db_addd in get_addr_eth(usr_id):
            keyboard.append(
                [InlineKeyboardButton(db_addd, callback_data="check_eth_"+db_addd)])
            i += 1
        keyboard.append(
            [InlineKeyboardButton("Back to Ethereum Address Menu",
                                  callback_data='addr_eth')])
        markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Choose your address",
            reply_markup=markup
        )


def print_addr_ETH(bot, update):
    query = update.callback_query
    addr = query.data[10:].lower()
    link = "https://api.blockchair.com/ethereum/dashboards/address/"
    get_addr = requests.get(link+addr)
    to_json = get_addr.json()
    conv = to_json["data"][addr]["address"]["balance"]
    final = vol*float(conv)
    rec = to_json["data"][addr]["address"]["received_usd"]
    bal = to_json["data"][addr]["address"]["balance_usd"]
    spen = to_json["data"][addr]["address"]["spent_usd"]
    tbeth = str("{:,}").format(round(final, 3))
    tbusd = str("{:,}").format(round(bal, 2))
    trusd = str("{:,}").format(round(rec, 2))
    tsusd = str("{:,}").format(round(spen, 2))
    t = to_json["data"][addr]["address"]["transaction_count"]
    profit = round((((spen-rec+bal)/rec)*100), 3)
    lt = to_json["data"][addr]["calls"][0]["transaction_hash"]
    ltv_1 = to_json["data"][addr]["calls"][0]["value"]
    ltv_2 = vol * float(ltv_1)
    ltv = str("{:,}").format(round(ltv_2, 4))
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"<b>Total Balance:</b> <code>{tbeth} ETH</code>" + "\n"
        f"<b>Total Balance:</b> <code>{tbusd} USD</code>" + "\n"
        f"<b>Total Recieved:</b> <code>{trusd} USD</code>" + "\n"
        f"<b>Total Spend:</b> <code>{tsusd} USD</code>" + "\n"
        f"<b>Transactions:</b> <code>{t}</code>" + "\n"
        f"<b>Last transaction:</b> <code>{lt}</code>" + "\n"
        f"<b>Last transaction value:</b> <code>{ltv} ETH</code>" + "\n"
        f"<b>Profit:</b> <code>{profit}%</code>",
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=sub_eth_addr_keyboard()
    )


def delete_addr_ETH(bot, update):
    query = update.callback_query
    usr_id = query.from_user.id
    all_addr = get_addr_eth(usr_id)
    if not all_addr == []:
        keyboard = []
        i = 0
        for db_addd in get_addr_eth(usr_id):
            keyboard.append(
                [InlineKeyboardButton(db_addd, callback_data="del_eth_" + db_addd)])
            i += 1
        keyboard.append(
            [InlineKeyboardButton("Back to Ethereum Address Menu",
                                  callback_data='addr_eth')])
        markup = InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Choose your address",
            reply_markup=markup
        )
    else:
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Your Address list was empty",
            reply_markup=sub_eth_addr_keyboard()
        )


def show_del_addr_ETH(bot, update):
    query = update.callback_query
    usr_id = query.from_user.id
    addr = query.data[8:]
    edit_user = mongo_coll.update_one(
        {
            "user_id": usr_id
        },
        {
            '$pull': {
                "wallets.eth": addr
            }
        }
    )
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f'Address <code>{addr}</code> succesfully delete',
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=sub_eth_addr_keyboard()
    )


def tran_ETH(bot, update):
    tran = update.message.text
    link = "https://api.blockchair.com/ethereum/dashboards/transaction/"
    get_tran = requests.get(link+tran)
    to_json = get_tran.json()
    if type(to_json["data"]) != dict:
        bot.send_message(
            chat_id=update.message.chat_id,
            text="You write wrong transaction, please check it",
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


def add_addr_ETH_message(bot, update):
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
########################## MESSAGE HANDLERS ##########################
ud.add_handler(MessageHandler(Filters.regex('^0x[0-9a-z]{64}$'), tran_ETH))
ud.add_handler(MessageHandler(Filters.regex(
    '^0x[0-9A-Fa-f]{40}$'), add_addr_ETH))


########################## KEYBOARD HANDLERS ##########################
ud.add_handler(CallbackQueryHandler(eth_menu, pattern='^eth$'))
ud.add_handler(CallbackQueryHandler(price_ETH, pattern='^price_eth$'))
ud.add_handler(CallbackQueryHandler(
    blockchain_status_ETH, pattern='^block_eth$'))
ud.add_handler(CallbackQueryHandler(
    check_transaction_ETH, pattern='^tran_eth$'))
ud.add_handler(CallbackQueryHandler(eth_addr_menu, pattern='^addr_eth$'))
ud.add_handler(CallbackQueryHandler(
    add_addr_ETH_message, pattern='^eth_add_addr$'))
ud.add_handler(CallbackQueryHandler(
    check_addr_ETH, pattern='^eth_check_addr$'))
ud.add_handler(CallbackQueryHandler(print_addr_ETH, pattern='^check_eth_'))
ud.add_handler(CallbackQueryHandler(delete_addr_ETH, pattern='^eth_del_addr$'))
ud.add_handler(CallbackQueryHandler(show_del_addr_ETH, pattern='^del_eth_'))


############################### BTC HANDLER ###############################
########################## MESSAGE HANDLERS ##########################
ud.add_handler(MessageHandler(Filters.regex('^[0-9a-z]{64}$'), tran_BTC))
ud.add_handler(MessageHandler(Filters.regex(
    '(^3\w{33}$|^1\w{33}$)'), add_addr_BTC))


########################## KEYBOARD HANDLERS ##########################
ud.add_handler(CallbackQueryHandler(btc_menu, pattern='^btc$'))
ud.add_handler(CallbackQueryHandler(price_BTC, pattern='^price_btc$'))
ud.add_handler(CallbackQueryHandler(
    blockchain_status_BTC, pattern='^block_btc$'))
ud.add_handler(CallbackQueryHandler(
    check_transaction_BTC, pattern='^tran_btc$'))
ud.add_handler(CallbackQueryHandler(btc_addr_menu, pattern='^addr_btc$'))
ud.add_handler(CallbackQueryHandler(
    add_addr_BTC_message, pattern='^btc_add_addr$'))
ud.add_handler(CallbackQueryHandler(
    check_addr_BTC, pattern='^btc_check_addr$'))
ud.add_handler(CallbackQueryHandler(print_addr_BTC, pattern='^check_btc_'))
ud.add_handler(CallbackQueryHandler(delete_addr_BTC, pattern='^btc_del_addr$'))
ud.add_handler(CallbackQueryHandler(show_del_addr_BTC, pattern='^del_btc_'))


############################### UTILS HANDLER ###############################
ud.add_handler(CommandHandler('start', startCommandText))
ud.add_handler(CallbackQueryHandler(main_menu, pattern='^main$'))

ud.add_handler(MessageHandler(_filter_error, fil_err))
updater.start_polling()
updater.idle()
