# -*- coding: utf8 -*-
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
import sys
import keyboard
import logging
from telethon.sync import TelegramClient
import re
from datetime import datetime, timedelta, timezone
import statistics
import time
import keep_alive

keep_alive.keep_alive()


#Раскомментировать перед отправкой в продкашен
phone = os.environ['PHONE']
api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
botkey = os.environ['BOTKEY']


storage = MemoryStorage()  # FOR FSM
bot = Bot(token=botkey, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)


class UserState(StatesGroup):
  name = State()
  address = State()


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
  level=logging.INFO,
)

chats = [["Типичный программист", "https://t.me/tproger_official"],
         ["IT Юмор", "https://t.me/ithumor"],
         ["Представляешь", "https://t.me/your_tech"],
         ["Веб-страница", "https://t.me/tproger_web"],
         ["Zen of Python", "https://t.me/zen_of_python"],
         ["Мобильная разработка", "https://t.me/mobi_dev"],
         ["Точка входа в программирование", "https://t.me/prog_point"],
         ["GameDev: раз,работка игр", "https://t.me/make_game"],
         ["Soft Skillz", "https://t.me/soft_skillz"],
         ["Нейроканал", "https://t.me/neuro_channel"],
         ["Java", "https://t.me/a_cup_of_java"],
         ["Сохранёнки программиста", "https://t.me/prog_stuff"],
         ["Книги по программированию", "https://t.me/devs_books"],
         ["Python: задачки и вопросы", "https://t.me/quiz_python"],
         ["Инструменты программиста", "https://t.me/prog_tools"],
         ["DevOps для ДевоПсов", "https://t.me/devo_pes"],
         ["Типичный QA", "https://t.me/typical_qa"],
         ["Go in Action", "https://t.me/go_in_action"],
         ["Linux и Линус", "https://t.me/linux_n_linus"],
         ["Data Analysis / Big Data", "https://t.me/big_data_analysis"],
         ["DATABASE DESIGN", "https://t.me/database_design"],
         ["Django Unleashed Framework", "https://t.me/django_prog"],
         [".NET / C#", "https://t.me/dot_net_c_sharp"]]

#список стоп-слов для рекламы
ad1 = "Реклама"
ad2 = "#партнёрский"
ad3 = "партнерский"
ad4 = "ивент"
ad5 = "вакансии"
ad6 = "Рекламодатель"

client = TelegramClient(phone, api_id, api_hash)
client.start()


@dp.message_handler(Command("start"), state=None)
async def welcome(message):

  await bot.send_message(
    message.chat.id,
    f"Привет, {message.from_user.first_name}! Нажмите кнопку «Собрать статистику», чтобы начать :)",
    reply_markup=keyboard.start,
    parse_mode='Markdown')


@dp.message_handler(content_types=['text'])
async def user_register(msg: types.Message):
  if msg.text == "Собрать статистику":
    n = 0
    msgChannels = "<b>Введите номер канала (только цифру):</b>\n\n"
    for strChannel in chats:
      n += 1
      msgChannels += str(n) + ".  " + strChannel[0] + "\n"
    await bot.send_message(msg.from_user.id, msgChannels)
    await UserState.name.set()
  else:
    await msg.answer("Cначала нажмите кнопку «Собрать статистику»")


@dp.message_handler(state=UserState.name)
async def get_username(msg: types.Message, state: FSMContext):
  try:
    await state.update_data(username=msg.text)
    #Присваиваем даты
    weekday = int(datetime.today().isoweekday())
    if weekday >= 3:
      startDate = datetime.now() - timedelta(days=datetime.today().weekday() +
                                             7)
      endDate = datetime.now() - timedelta(days=datetime.today().weekday())
    else:
      startDate = datetime.now() - timedelta(days=datetime.today().weekday() +
                                             14)
      endDate = datetime.now() - timedelta(days=datetime.today().weekday() + 7)

    #Присваиваем таймзону, чтобы не было проблем при сравнении с message.date
    startDate = startDate.replace(hour=0, minute=0, second=0, microsecond=0)
    endDate = endDate.replace(hour=0,
                              minute=0,
                              second=0,
                              microsecond=0,
                              tzinfo=timezone.utc)

    chat = chats[int(msg.text) - 1]
    chat = chat[1]

    msgDateInfo = "<b>Вы выбрали канал: " + chat + "</b>\n\n— Собираем статистику по постам от понедельника <b>" + str(
      startDate.strftime('%d.%m.%Y')
    ) + "</b> (включительно) и до понедельника <b>" + str(
      endDate.strftime('%d.%m.%Y')
    ) + "</b> (не включительно).\n— Подписки и отписки собираются со сдвигом в три дня вперёд: со среды по среду.\n— Кол-во подписчиков — во вторник.\n\nCтатистика за предыдущую неделю собирается только со среды текущей недели. В понедельник и вторник вы получите старую статистику.\n\nЕсли всё ок, введите 1."
    await bot.send_message(msg.from_user.id,
                           msgDateInfo,
                           disable_web_page_preview=True)
    await UserState.address.set()
  except Exception as e:
    errorMsg = "Произошла ошибка: " + str(
      e) + "\n\nПопробуйте заново. Нажмите «Собрать статистику»"
    await bot.send_message(msg.from_user.id, errorMsg)
    await state.finish()


@dp.message_handler(state=UserState.address)
async def get_address(msg: types.Message, state: FSMContext):
  await state.update_data(address=msg.text)
  data = await state.get_data()
  if data['address'] == "1":
    #Присваиваем даты
    weekday = int(datetime.today().isoweekday())
    if weekday >= 3:
      startDate = datetime.now() - timedelta(days=datetime.today().weekday() +
                                             7)
      endDate = datetime.now() - timedelta(days=datetime.today().weekday())
    else:
      startDate = datetime.now() - timedelta(days=datetime.today().weekday() +
                                             14)
      endDate = datetime.now() - timedelta(days=datetime.today().weekday() + 7)
    #Присваиваем таймзону, чтобы не было проблем при сравнении с message.date
    startDate = startDate.replace(hour=0, minute=0, second=0, microsecond=0)
    endDate = endDate.replace(hour=0,
                              minute=0,
                              second=0,
                              microsecond=0,
                              tzinfo=timezone.utc)
  else:
    await bot.send_message(
      msg.from_user.id,
      "Бот пока не умеет работать с другими датами. Поэтому помчитает так :)")
    #Присваиваем даты
    weekday = int(datetime.today().isoweekday())
    if weekday >= 3:
      startDate = datetime.now() - timedelta(days=datetime.today().weekday() +
                                             7)
      endDate = datetime.now() - timedelta(days=datetime.today().weekday())
    else:
      startDate = datetime.now() - timedelta(days=datetime.today().weekday() +
                                             14)
      endDate = datetime.now() - timedelta(days=datetime.today().weekday() + 7)
    #Присваиваем таймзону, чтобы не было проблем при сравнении с message.date
    startDate = startDate.replace(hour=0, minute=0, second=0, microsecond=0)
    endDate = endDate.replace(hour=0,
                              minute=0,
                              second=0,
                              microsecond=0,
                              tzinfo=timezone.utc)

  prvGroupID = 0
  allReactions = []
  countViews = []

  statPost = ""
  chat = chats[int(data['username']) - 1]
  chat = chat[1]
  #собираем в список id постов, которые попадают под нужные даты

  await bot.send_message(
    msg.from_user.id,
    "Бот начал собирать статистику. Это займёт не больше минуты.")

  #получаем стату и обрезаем её
  channelFullInfo = await client.get_stats(chat)
  memberСountGraph = channelFullInfo.followers_graph
  followerCountGraph = channelFullInfo.growth_graph
  membersStr = str(memberСountGraph)
  followerStr = str(followerCountGraph)

  #забираем столбец с отписками
  start = membersStr.find('"y1",') + 5
  end = membersStr.find(']', start)
  unsubMembersList = [int(i) for i in membersStr[start:end].split(',')]
  weekday = int(datetime.today().isoweekday())
  startIndexOfMemberList = 0
  endIndexOfMemberList = 0

  #со среды у нас всё ок со счётом. А вот во вт-пн надо считать прерыдущую неделю
  if weekday >= 3:
    startIndexOfMemberList = 0 - (weekday - 2)
    endIndexOfMemberList = startIndexOfMemberList - 7
  else:
    startIndexOfMemberList = 0 - (weekday + 5)
    endIndexOfMemberList = startIndexOfMemberList - 7

  sumUnsubMembers = sum(list(
    map(int, unsubMembersList[endIndexOfMemberList:startIndexOfMemberList])))

  #забираем столбец с подписками
  start = membersStr.find('"y0",') + 5
  end = membersStr.find(']', start)
  joinedMembersList = [int(i) for i in membersStr[start:end].split(',')]
  weekday = int(datetime.today().isoweekday())
  startIndexOfMemberList = 0
  endIndexOfMemberList = 0
  #со среды у нас всё ок со счётом. А вот во вт-пн надо считать прерыдущую неделю
  if weekday >= 3:
    startIndexOfMemberList = 0 - (weekday - 2)
    endIndexOfMemberList = startIndexOfMemberList - 7
  else:
    startIndexOfMemberList = 0 - (weekday + 5)
    endIndexOfMemberList = startIndexOfMemberList - 7
  sumJoinedMembers = list(
    map(int, joinedMembersList[endIndexOfMemberList:startIndexOfMemberList]))
  sumJoinedMembers = sum(sumJoinedMembers)

  #забираем столбец с общим числом подписчиков
  start = followerStr.find('"y0",') + 5
  end = followerStr.find(']', start)
  allMembersList = [int(i) for i in followerStr[start:end].split(',')]
  weekday = int(datetime.today().isoweekday())
  startIndexOfMemberList = 0
  endIndexOfMemberList = 0
  #со среды у нас всё ок со счётом. А вот во вт-пн надо считать прерыдущую неделю
  if weekday >= 3:
    startIndexOfMemberList = 0 - (weekday - 2)
    endIndexOfMemberList = startIndexOfMemberList - 7
  else:
    startIndexOfMemberList = 0 - (weekday + 5)
    endIndexOfMemberList = startIndexOfMemberList - 7
  sumAllMembers = list(
    map(int, allMembersList[endIndexOfMemberList:startIndexOfMemberList]))
  sumAllMembers = sumAllMembers[-1]
  
  #считаем реакции
  try:
    async for message in client.iter_messages(chat,
                                              reverse=True,
                                              offset_date=startDate):

      time.sleep(0.1)
      if (message.date <= endDate):
        i = message.id

        #переменная для общего числа реакций
        countAllReactMP = 0
        countForOnP = 0
        countReactOnP = 0
        countComOnP = 0
        countReactOnK = 0
        countReactOnKFinal = 0

        #если слова есть в посте, значит, это реклама, выпёздываемся
        if ((ad1 in message.message) or (ad2 in message.message)
            or (ad3 in message.message) or (ad4 in message.message)
            or (ad5 in message.message) or (ad6 in message.message)):
          print("В посте " + str(i) + " есть рекламная метка.")
          #проверяем, есть ли у поста медиа и grouped_id, если да, дальше будет группа картинок
          if (message.media and message.grouped_id):
            #если prvGroupID совпадает с айдишником поста,
            #значит это группа и первый пост замеряли, выходим из итерации цикла
            if prvGroupID == message.grouped_id:
              continue
            #если айди разные, значит это первый пост из группы, запоминаем айди
            else:
              prvGroupID = message.grouped_id
          continue

        #проверяем, есть ли у поста медиа и grouped_id, если да, дальше будет группа картинок
        if (message.media and message.grouped_id):
          #если prvGroupID совпадает с айдишником поста,
          #значит это группа и первый пост замеряли, выходим из итерации цикла
          if prvGroupID == message.grouped_id:
            continue
            #если айди разные, значит это первый пост из группы, запоминаем айди
          else:
            prvGroupID = message.grouped_id

        #забираем количество репостов
        reactStr = str(message)
        regex_num = re.compile('forwards=\d+,')
        numForStr = ""
        regex_count = re.compile('\d+')
        countForOnP = regex_count.findall(
          numForStr.join(regex_num.findall(reactStr)))
        countForOnP = list(map(int, countForOnP))
        countForOnP = sum(countForOnP)

        #забираем количество реакций
        reactStr = str(message.reactions)
        regex_num = re.compile('count=\d+,')
        numReactStr = ""
        regex_count = re.compile('\d+')
        countReactOnP = regex_count.findall(
          numReactStr.join(regex_num.findall(reactStr)))
        countReactOnP = list(map(int, countReactOnP))
        countReactOnP = sum(countReactOnP)

        print("\n\nПросмотров у поста: " + str(message.views))
        countViews.append(int(message.views))

        #Пробуем зайти в комменты
        try:
          async for message in client.iter_messages(chat, reply_to=i, reverse=True):
            countComOnP += 1
            if isinstance(message.sender, types.User):
              #print(message.date, message.sender.first_name, ':', message.text)
              if message.reactions != None:
                reactStr = str(message.reactions)
                regex_num = re.compile('count=\d+,')
                numReactStr = ""
                regex_count = re.compile('\d+')
                countReactOnK = regex_count.findall(
                  numReactStr.join(regex_num.findall(reactStr)))
                countReactOnK = list(map(int, countReactOnK))
                countReactOnK = sum(countReactOnK)
                countReactOnKFinal += countReactOnK
                countReactOnK = 0
            else:
              if message.reactions != None:
                reactStr = str(message.reactions)
                regex_num = re.compile('count=\d+,')
                numReactStr = ""
                regex_count = re.compile('\d+')
                countReactOnK = regex_count.findall(
                  numReactStr.join(regex_num.findall(reactStr)))
                countReactOnK = list(map(int, countReactOnK))
                countReactOnK = sum(countReactOnK)
                countReactOnKFinal += countReactOnK
                countReactOnK = 0
        except Exception as e:
          errorMsg = "Почему-то не получилось собрать комменты и лайки на них. Пост:" + chat + "/" + str(
            i) + ". Ошибка: " + str(e)
          await bot.send_message(msg.from_user.id, errorMsg)

        countAllReactMP = int(countForOnP) + int(countReactOnP) + int(
          countComOnP) + int(countReactOnKFinal)
        statPost += chat + "/" + str(i) + "\n"
        statPost += str(countForOnP) + " 📢 + "
        statPost += str(countReactOnP) + " ❤️ + "
        statPost += str(countComOnP) + " 💬 + "
        statPost += str(countReactOnKFinal) + " ❤️💬 = " + str(
          countAllReactMP) + "\n\n"
        allReactions.append(int(countAllReactMP))

    try:
      #Присваиваем даты для подсчёта постов за месяц
      weekday = int(datetime.today().isoweekday())
      if weekday >= 3:
        startDate = datetime.now() - timedelta(days=datetime.today().weekday() +
                                              30)
        endDate = datetime.now() - timedelta(days=datetime.today().weekday())
        print("Сейчас среда, четверг, пятница, суббота или воскресенье. Считаем даты от " + str(startDate) + " и до " + str(endDate))
      else:
        startDate = datetime.now() - timedelta(days=datetime.today().weekday() +
                                              34)
        endDate = datetime.now() - timedelta(days=datetime.today().weekday() + 4)
        print("Сейчас понедельник или вторник. Считаем даты от " + str(startDate) + " и до " + str(endDate))

      #Присваиваем таймзону, чтобы не было проблем при сравнении с message.date
      startDate = startDate.replace(hour=0, minute=0, second=0, microsecond=0)
      endDate = endDate.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
      prvGroupID = 0

      try:
        async for message in client.iter_messages(chat, reverse=True,offset_date=startDate):
          if (message.date <= endDate):
              i = message.id
              print(i)
              """
              #если слова есть в посте, значит, это реклама, выпёздываемся
              if ((ad1 in message.message) or (ad2 in message.message)
                  or (ad3 in message.message) or (ad4 in message.message)
                  or (ad5 in message.message) or (ad6 in message.message)):
                print("В посте " + str(i) + " есть рекламная метка.")
              #проверяем, есть ли у поста медиа и grouped_id, если да, дальше будет группа картинок
                if (message.media and message.grouped_id):
                    #если prvGroupID совпадает с айдишником поста,
                    #значит это группа и первый пост замеряли, выходим из итерации цикла
                    if prvGroupID == message.grouped_id:
                      continue
                    #если айди разные, значит это первый пост из группы, запоминаем айди
                    else:
                      prvGroupID = message.grouped_id
                continue
              """
              #проверяем, есть ли у поста медиа и grouped_id, если да, дальше будет группа картинок
              if (message.media and message.grouped_id):
              #если prvGroupID совпадает с айдишником поста,
              #значит это группа и первый пост замеряли, выходим из итерации цикла
                if prvGroupID == message.grouped_id:
                    continue
                    #если айди разные, значит это первый пост из группы, запоминаем айди
                else:
                    prvGroupID = message.grouped_id
              countViews.append(int(message.views))
      
        countPostsForSrViews = len(countViews)
        print("\n\nКоличество контентных постов: " + str(countPostsForSrViews))
        countViewsSr = list(map(int, countViews))
        countViewsSr = sum(countViewsSr)
        print("Всего просмотров постов: " + str(countViewsSr))
        viewsSr = countViewsSr // countPostsForSrViews
        print("Среднее количество просмотров на пост: " + str(viewsSr))

      except Exception as e:
          errorMsg = "Почему-то не получилось собрать посты. Ошибка: " + str(e) + "\n\nError on line {}".format(sys.exc_info()[-1].tb_lineno)
          await bot.send_message(msg.from_user.id, errorMsg)
          await state.finish()
      
      print("Формирую финальное сообщение...")
      #считаем процент отписок и подписок и добавляем в сообщение
      msgJoined = "<b>Отписки: </b>" + str(sumUnsubMembers)
      msgJoined += "\n<b>Подписки: </b>" + str(sumJoinedMembers)
      procUnsubDay = round((sumUnsubMembers/sumAllMembers/7)*100, 2)
      msgJoined += "\n<b>Отписок в день: </b>" + str(procUnsubDay) + "%"
      procJoinedDay = round((sumJoinedMembers/sumAllMembers/7)*100, 2)
      msgJoined += "\n<b>Подписок в день: </b>" + str(procJoinedDay) + "%"

      #считаем долю активной аудитории
      msgJoined += "\n<b>Количество подписчиков: </b>" + str(sumAllMembers)
      msgJoined += "\n<b>Средний охват поста: </b>" + str(
        viewsSr)
      activeAudit = round((viewsSr/sumAllMembers)*100, 2)
      msgJoined += "\n<b>Доля активной аудитории: </b>" + str(
        activeAudit) + "%"
      
      #считаем долю вовлечённой аудитории
      msgJoined += "\n<b>Медиана реакций: </b>" + str(
          statistics.median(allReactions))
      engagedAudit = round((statistics.median(allReactions)/viewsSr)*100, 2)
      msgJoined += "\n<b>Доля вовлечённой аудтиории: </b>" + str(engagedAudit) + "%"
      
      statToPaste = "\n\n<b>Значения для вставки:</b>\n<code>" + str(sumUnsubMembers) + "\n" + str(sumJoinedMembers) + "\n" + str(procUnsubDay) + "%" + "\n" + str(procJoinedDay) + "%" + "\n" + str(sumAllMembers) + "\n" + str(viewsSr) + "\n" + str(activeAudit) + "%" + "\n" + str(
          statistics.median(allReactions)) + "\n" + str(engagedAudit) + "%</code>"

      statPostMed = "<b>Итоговая статистика</b>\n\n" + msgJoined + statToPaste
      
      print("Обрезаю сообщения, чтобы уместились в 4096 символов...")
      # режем сообщения больше 4096 символов, телеграм больше не примет
      if len(statPost) > 4096:
        for x in range(0, len(statPost), 4096):
          await bot.send_message(msg.from_user.id,
                                 statPost[x:x + 4096],
                                 disable_web_page_preview=True)
      else:
        await bot.send_message(msg.from_user.id,
                               statPost,
                               disable_web_page_preview=True)

      statPostMed += "\n\nБот пока не умеет считать опросы и реакции на inline-кнопках (как в канале с задачками по Python). Проверьте, что в постах совпадают даты, реакции и нет рекламы.\n\n<i>Если бот помог вам, не забудьте мысленно отправить плюсик в карму Паше Ф. ❤️</i>"
      await bot.send_message(msg.from_user.id, statPostMed)

    except Exception as e:
      statPostMed = "Почему-то не получилось собрать медиану\nОшибка: " + str(
        e) + "\n\nError on line {}".format(sys.exc_info()[-1].tb_lineno)
      if len(statPost) > 4096:
        for x in range(0, len(statPost), 4096):
          await bot.send_message(msg.from_user.id,
                                 statPost[x:x + 4096],
                                 disable_web_page_preview=True)
      else:
        await bot.send_message(msg.from_user.id,
                               statPost,
                               disable_web_page_preview=True)
      await bot.send_message(msg.from_user.id, statPostMed, parse_mode='html')

    await state.finish()

  except Exception as e:
    errorMsg = "Почему-то не получилось собрать посты. Ошибка: " + str(e)
    await bot.send_message(msg.from_user.id, errorMsg)
    await state.finish()


if __name__ == '__main__':
  print('Монстр пчелы запущен!'
        )  # ЧТОБЫ БОТ РАБОТАЛ ВСЕГДА с выводом в начале любого текста
executor.start_polling(dp)
