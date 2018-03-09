#Simple CheckIn Telegram bot

This bot help workers on group marking your arrival.

Managers on group can check everyday who is arrived, and who still not. 

First of all, bot ask who you are - Manager or worker:
 - If you manager, you can get yout ID, using /help.
 - If you worker - you need choose your manager - but before it, you need ask ID of your manager to choose correctly.
 
 Then, everyday, when you send on bot random symbol - he return you callback button:
  - For Workers this buton be "CheckIn" - check that you comming today.
  - For manager button is "Show List" - show all you group with parametr 1 or 0.


My TelegramBot (may be disabled): @CheckInIvcBot

Sample:
 <img src="https://github.com/Ver1Sus/TelegramChekInBot/edit/master/sample.png"></img>

#TODO:
 1. Get server with SSL sertificate to get working bot with web-hook. 
 2. Update function which is return list of workers with using UserName and First_Name.

