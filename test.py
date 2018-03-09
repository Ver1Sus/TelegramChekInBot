import sys
import time
from unittest import result

import telepot
import json
import actions
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

'''
Using callback_query you cam get fast answer without web-hook.
But question - is fast the working the script in the bot with this method?

'''


###TODO:  1 - add deleting from json when change role
#TODO      2 - add when choose role Manager
#todo: 3 - add good list for managers with @userNames and First_names


##- when comming any chat word or text - show the Inline buttons
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)


    employee = json.load(open('employee.json'))
    print employee

    if 'text' in msg and msg['text'] == '/chooserole':
        actions.deleteUser(chat_id)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Be worker', callback_data='be_worker')],
            [InlineKeyboardButton(text='Be manager', callback_data='be_manager')],
        ])
        bot.sendMessage(chat_id, 'Choose your\'s Role:', reply_markup=keyboard)

    elif 'text' in msg and msg['text'] == '/updates':
        from updates import updatesText
        bot.sendMessage(chat_id, updatesText)

    elif 'text' in msg and msg['text'] == '/info':
        text = "Hello! This is 'CheckIn' bot. \n\n" \
               "How it works:\n" \
               "    1. If you first here - choose your's role (MANAGER - head of group, can look how much workers checked today. WORKER - choose the ID's of Manager and can checked everyday). " \
               "If you want change role, send /chooserole (Warning - if you will be manager - all list of workers in group will be deleted)\n" \
               "    2.1 If you MANAGER - send /help and get your's ID. Send this ID to yours worker - when they registered on the bot to choose you as a his manager\n" \
               "    2.2 You can send /start and get list of all workers on group and his activity\n" \
               "    3.1 If you WORKER - ask your Manager his ID and choose it when bot get you all list of Managers.\n" \
               "    3.2 Send /start to send message and checked that you coming.\n\n" \
               "Contact with @Ver1Sus if you get error."
        bot.sendMessage(chat_id, text)

    elif 'text' in msg and msg['text'] == '/help':
        bot.sendMessage(chat_id, "Hi, yor ID = {}".format(chat_id))

    elif str(chat_id) in employee['workers2']:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Check In', callback_data='worker')],
        ])
        bot.sendMessage(chat_id, 'Information: ', reply_markup=keyboard)

    elif chat_id in employee['managers']:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Show list of Workers', callback_data='manager')],
        ])
        bot.sendMessage(chat_id, 'Information: ', reply_markup=keyboard)

    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Be worker', callback_data='be_worker')],
            [InlineKeyboardButton(text='Be manager', callback_data='be_manager')],
        ])

        bot.sendMessage(chat_id, 'Choose your\'s Role:', reply_markup=keyboard)




##--- When pressing the Inline buttons - get chat_id, text of button and do something logic
def on_callback_query(msg):
    # print msg
    chat_id = msg['message']['chat']['id']

    ### --- get information about callback
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data, chat_id )


    try:
        ###-- Checkin today
        if query_data == 'worker':
            bot.answerCallbackQuery(query_id, text='Working with query...')
            result = actions.checkInToday(chat_id)

            if result == 1:
                text="You have no group selected"
            elif result == 2:
                text = "You already checked today before"
            elif result == 3:
                text = "User {} habe no attribute 'Active'. Contact admin".format(chat_id)
            elif result == 5:
                text = "Try add users to today's group. Can't find group in emplee List"
            elif result == 0:
                text = 'Note added!'
            else:
                text = "Hm.... Answer is {}. Contact with admin.".format(result)
            bot.sendMessage(chat_id, text)

        ##--- show list of all checked workers today
        elif  query_data == 'manager':
            bot.answerCallbackQuery(query_id, text='Working with query...')
            result = actions.getCheckedWorkerList(chat_id)
            if result == 1:
                text = "Have no group with managerId {}".format(chat_id)
            elif result == 2:
                text = "Group is empty"
            else:
                text = "List today: \n"
                text += actions.parseWorkerList(result)

            bot.sendMessage(chat_id, text)

        ##---- Choose be a worker
        if query_data == "be_worker":
            ##-- write your name in list
            username = ""
            first_name = ""
            keyboard = []
            try:
                username = msg['message']['chat']['username']
            except:
                pass
            try:
                first_name = msg['message']['chat']['first_name']
            except:
                pass

            ###--- add new worker and process result
            result = actions.addNewWorker(chat_id, username, first_name)

            if result == 0:
                text = "You are worker!"
                ##-- and choose your manager
                inline_key = actions.parseGroupToButtons(actions.getGroupList())
                keyboard = InlineKeyboardMarkup(inline_keyboard=inline_key)

            elif result == 1:
                text = "User already in Workers. Send /chooserole to set your's new manager"
            elif result == 2:
                text = "You already in Manager. Send /chooserole to change you role and delete your group"
            else:
                text = "Hm.. can't add. Result {}".format(result)

            bot.sendMessage(chat_id, text)

            if keyboard != []:
                bot.sendMessage(chat_id, 'Choose your\'s Manager:', reply_markup=keyboard)


        ###---- choose be  a manager
        if query_data == 'be_manager':
            result = actions.addNewMnager(chat_id)
            if result == 0:
                text = "You are Manager!"
            elif result == 1:
                text = "You already Worker! Send /chooserole to cahnge your role"
            elif result == 2:
                text = "You already manager! Send /chooserole to delete all you group and start again"
            else:
                text = "Unknow result {}".format(result)

            bot.sendMessage(chat_id, text)

        ###--- choose your manager
        elif '_manager_' in query_data:
            managerId = query_data.split(':')[1]
            print  "{} to group with manager {}".format(chat_id, managerId)
            result = actions.connectWorkerToManager(chat_id, managerId)
            if result == 0:
                text = "User add to group {}".format(managerId)
            elif result == 1:
                text = "there is no group {}".format(managerId)
            elif result == 2:
                text = "There is no user {} in workers".format(chat_id)
            elif 'group:' in result:
                text = "User already in group {}".format(result.split(":")[1])
            else:
                text = "Unrecognize result {}".format(result)

            bot.sendMessage(chat_id, text)

        else:
            bot.answerCallbackQuery(query_id, text='You press something another...')

    except Exception as error:
        bot.sendMessage(chat_id, 'ERROR: {}\n Please, try again'.format(error))

    except:
        bot.sendMessage(chat_id, 'Unknown ERROR. Please, try again')





TOKEN = 'YOUR TOKEN'  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)