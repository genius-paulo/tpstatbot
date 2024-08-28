from PIL import Image
import os
from os import environ as env
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

async def get_screenshot(er_list):

  screenshots = []

  # Задаем параметры окна браузера
  options = Options()
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-gpu')
  options.add_argument('--disable-dev-shm-usage')
  options.add_argument('--headless')
  options.add_argument('--start-maximized')
  
  try:
    # Активируем драйвер браузера
    driver = webdriver.Chrome(options=options)

    # Проходимся по каждому посту из списка
    for post_url in er_list:
      # Добавляем приставку, чтобы открыть пост без iframe и получить его реальные размеры
      post_url = post_url + '?embed=1&mode=tme'

      # Открываем пост
      driver.get(post_url)

      # Находим класс элемента поста
      ele = driver.find_element(By.CLASS_NAME, 'tgme_widget_message_bubble')

      # Определяем размеры элемента
      size = ele.size
      w, h = size['width'], size['height']
      print(f'Размеры элемента: {w}, {h}')

      # Подгоняем окно под высота поста, чтобы он влез полностью, и получаем скриншот
      driver.set_window_size(1920, h)
      png = driver.get_screenshot_as_png()

      # Рассчитываем границы поста и обрезаем пикчу по ним
      im = Image.open(BytesIO(png))
      w_im, h_im = im.size
      print(f'Размеры изображения: {w_im}, {h_im}')

      left = w_im/2 - w/2 + 10
      top = 0
      right = w_im/2 + w/2 + 20
      print(f'Размеры обрезки изображения: {left}, {right}')
      bottom = h_im
      im = im.crop((left, top, right, bottom))

      # Задаем имя и путь сохранения скриншота
      output_directory = post_url.replace("/","_") + '.png'
      print('Делаю скриншот: ' + output_directory)
      im.save(output_directory)

      # Добавляем путь до пикчи в список
      screenshots.append(output_directory)

  except Exception as e:
    print('Ошибка получения скриншотов из списка: ' + str(e))
  
  #  В любом случае закрываем драйвер браузера
  finally:
    driver.close()
    driver.quit()

  # Возвращаем список путей скриншотов
  return screenshots

async def create_visionboard(er_worst, er_bad, er_good, er_great):
  
  # Определяем координаты постов на части вижнборда
  x_screenshot, y_screenshot = 10, 10
  dict_screen_coordinats = {0: [370, 70],
                    1: [370, 540],
                    2: [1000, 70],
                    3: [1000, 540],
                    4: [1700, 320]}
  # Список частей вижнборда
  visionboards_part_list = ['worst',
                            'bad',
                            'good',
                            'great']
  
  # Задаем вводные вижнборда: входной путь, координаты, выходной путь
  img_visionboard_template = Image.open('visionboard_template.png')
  y_visionboard_part = 0
  x_visionboard_part = 0
  output_visionboard = 'visionboard.png'

  #Здесь мы проходимся по четырем спискам и используем четыре
  #разные картинки для вижнборда. Поэтому используем eval и part.
  #Пока это самое элегантное решение, которое я смог придумать.
  for part in visionboards_part_list:
    # Преобразуем строку part в переменную списка постов с помощью eval
    er_list = eval('er_' + part)
    print('\nПрохожу список er_' + part + ': ' + str(er_list))

    # Открываем нужную часть вижнборда
    img_visionboards_part = Image.open('visionboard_' + part + '.png')
    
    # Объявляем переменную для прохода по словарю координат
    n_dict = 0

    # Получаем скриншоты
    print('\nДелаю скриншоты постов из списка: ' + str(er_list))
    screenshots = await get_screenshot(er_list)

    # Проходимся по каждому посту в списке скришотов
    print('\nВставляю скриншоты на вижнборд и удаляю их.')
    for screenshot in screenshots:

      # Открываем скриншот и уменьшаем с двух сторон: какая достигнется первой
      img_screenshot = Image.open(screenshot)
      img_screenshot.thumbnail(size=(430, 600))

      # Открываем скриншот и задаем координаты вставки на часть вижнборда
      y_screenshot = dict_screen_coordinats[n_dict][0]
      x_screenshot = dict_screen_coordinats[n_dict][1]

      # Вставляем скриншот на часть вижнборда
      img_visionboards_part.paste(img_screenshot, (x_screenshot, y_screenshot), mask=img_screenshot)

      # Удаляем скриншот
      try:
        os.remove(screenshot)
        print('Удаляю скриншот: ' + screenshot)
      except OSError: await print("Почему-то не получилось удалить файл с сервера: " + screenshot)

      # Сохраняем часть вижнборда и открываем ее заново
      img_visionboards_part.save('visionboard_' + part + '_edit.png')
      img_visionboards_part = Image.open('visionboard_' + part + '_edit.png')
      
      # Переходим к следующему пункту словаря с координатами
      n_dict += 1
    
    # Объединяем части вижнборда
    img_visionboard_template.paste(img_visionboards_part, (x_visionboard_part, y_visionboard_part))
    x_visionboard_part += 1020

  # Добавляем на вижнборд шапку с пояснениями
  img_visionboards_header = Image.open('visionboard_header.png')
  img_visionboard_template.paste(img_visionboards_header, (0, 0))

  # Сохраняем вижнборд
  img_visionboard_template.save(output_visionboard)
  
  return output_visionboard

async def sort_vision_board(dict_posts_er, er_s):

  # Сортируем посты для вижнборда
  er_worst = []
  er_bad = []
  er_good = []
  er_great = []

  # Распределяем посты по количеству реакций на 4 группы
  for key, value in dict_posts_er.items():

    er_post = value[0]

    if er_post <= (er_s * 0.8):
      er_worst.append(key)
    elif er_post > (er_s * 0.8) and er_post < er_s:
      er_bad.append(key)
    elif er_post >= er_s and er_post < (er_s * 1.2):
      er_good.append(key)
    elif er_post >= (er_s * 1.2):
      er_great.append(key)
    else:
      print('Почему-то пост не попал никуда: ', er_post)

  # Обрезаем списки до 5 постов
  er_worst = er_worst[:5]
  er_bad = er_bad[:5]
  er_good = er_good[:5]
  er_great = er_great[:5]

  return er_worst, er_bad, er_good, er_great

async def send_pre_visionboard_message(bot, msg, startDate, endDate, chat):
  # Отправляем сообщение перед составлением вижнборда с пояснениями
  message_text = ("<b>Выбранный канал: " +
                 chat + "</b>\n\nСоздаём вижнборд по постам предыдущего месяца <b>(" +
                 str(startDate.strftime('%d.%m.%Y')) + " — " +
                 str(endDate.strftime('%d.%m.%Y')) + ")</b>." + 
         		 "\n\nПосты распределяются на зоны в cравнении со средним количеством реакций (ER):" +
                 "\n— В красную 🟥 попадают посты с количеством реакций сильно ниже среднего." +
                 "\n— В желтую 🟨 и зелёную 🟩 — посты со средними показателями." +
                 "\n— В сине-зелёную 🟦 — посты с аномально высокими показателями." +
                 "\n— Максимум по 5 постов, чтобы не переборщить :)" +
                 "\n\n<b>Бот начал анализировать посты. Это займёт около 3-5 минут.</b>")
  await bot.send_message(msg.from_user.id, message_text, disable_web_page_preview=True)

async def send_all_reactions(bot, msg, dict_posts_er, er_worst, er_bad, er_good, er_great):
  # Отправляем сообщение с подробными реакциями по каждому посту из вижнборда
  try:
    message_text = '\n<b>ER поста меньше среднего ER * 0,8:</b>\n'
    for key in er_worst:
      post = dict_posts_er[key]
      post_reactions = post[1]
      post_reactions = post_reactions[:-1]
      message_text += '— ' + post_reactions

    message_text += '\n<b>ER поста больше среднего ER * 0.8, но меньше среднего ER:</b>\n'
    for key in er_bad:
      post = dict_posts_er[key]
      post_reactions = post[1]
      post_reactions = post_reactions[:-1]
      message_text += '— ' + post_reactions
    
    message_text += '\n<b>ER поста больше или равен среднему ER, но меньше среднего ER * 1.2:</b>\n'
    for key in er_good:
      post = dict_posts_er[key]
      post_reactions = post[1]
      post_reactions = post_reactions[:-1]
      message_text += '— ' + post_reactions
    
    message_text += '\n<b>ER поста больше среднего ER * 1.2:</b>\n'
    for key in er_great:
      post = dict_posts_er[key]
      post_reactions = post[1]
      post_reactions = post_reactions[:-1]
      message_text += '— ' + post_reactions
    
    message_text += '\n<b>Бот подготавливает вижнборд, минуточку...</b>\n'

    await bot.send_message(msg.from_user.id, message_text, disable_web_page_preview=True)
  except Exception as e: print(e)


async def send_after_visionboard_message(bot, msg):
  # Отправляем сообщение после отправки вижнборда с рекомендациями
  message_text = ("<b>Вижнборд готов! Что делать дальше?</b>"\
                "\n\n<b>1. Перенесите изображение в Miro или просто откройте блокнот и запишите свои наблюдения:</b>"\
				"\n— Какие есть различия между областями?"\
				"\n— Что меняется по мере роста ER?"\
				"\n— Почему зашли посты с высоким ER и не зашли с маленьким?"\
				"\n— Как реакции пользователей связаны между собой?"\
				"\n— Что общего в постах каждой области? Например, дизайн, подача, темы, длина текстов или формат."\
				"\n\n<b>2. Выберите самые адекватные гипотезы, достаточно 3-5 штук:</b>"\
				"\n— Убедитесь, что гипотеза повторяется много раз и дополняется на разных стикерах."\
				" Например, ЦА хорошо реагирует на посты с задачами."\
				"\n— Сосредоточьтесь на том, что вы отмечаете на практике и во что больше верите."\
				"Например, лучше работают визуалы с якорным объектом, без большого количества ярких деталей."\
				"\n\n<b>3. Проверьте гипотезы в течение месяца и посмотрите, как изменится ситуация через месяц :)</b>")
  await bot.send_message(msg.from_user.id, message_text, disable_web_page_preview=True)
