import telebot
from telebot import types
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot import custom_filters

state_storage = StateMemoryStorage() # для хранения состояния пользователей

API_TOKEN = '' # токен, который выдается на бота

bot = telebot.TeleBot(API_TOKEN, state_storage=state_storage)

def is_float(element: any) -> bool:
    """
    Проверка на ввод вещественного числа
    """

    if element is None: 
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False
    
class UserStates(StatesGroup):
    """
    Enum для отслеживания на какой стадии находится пользователь в текущем сеансе
    """
    body_mass = State() # Вес
    body_height = State() # Рост
    systolic_blood_pressure = State()  # Изменение систолического артериального давления
    heart_rate = State()  # Изменение частоты сердечных сокращений
    respiratory_rate = State()  # Изменение частоты дыхательных движений
    diuresis = State()  # Диурез
    first_scale_end = State()  # Окончание работы
    second_scale_end = State()  # Окончание работы

class UserScale:
    """
    Адаптер для изменения состояния пользователя в текущем сеансе
    """
    def __init__(self, scale_states):
        self.scale_states = scale_states
        self.current_state = 0

    def next(self):
        self.current_state += 1
        return self.scale_states[self.current_state - 1]

    def current(self):
        return self.scale_states[self.current_state]

    def prev(self):
        return self.scale_states[self.current_state - 1]
    
class UserData:
    # TODO коммент и заполнить данные
    def __init__(self):
        self.body_mass = None
        self.body_height = None
        self.systolic_blood_pressure = None
        self.heart_rate = None
        self.respiratory_rate = None
        self.diures = None
#
# Настройка всех возможных кнопок в приложении
# TODO перенести сюда кнопки для выбора шкалы
#

# Кнопка САД
systolic_blood_pressure_buttons = [
            [types.InlineKeyboardButton(text="Значения в пределах нормы", callback_data="CAD_NORM")],
            [types.InlineKeyboardButton(text="Снижение САД на 20-50 мм.рт.ст. ", callback_data="CAD_1")],
            [types.InlineKeyboardButton(text="Снижение САД на 50-80 мм.рт.ст. ", callback_data="CAD_2")],
            [types.InlineKeyboardButton(text="Снижение САД на более 80 мм.рт.ст. ", callback_data="CAD_3")],
            [types.InlineKeyboardButton(text="Начать заново", callback_data="START")]
        ]
systolic_blood_pressure_keyboard = types.InlineKeyboardMarkup(systolic_blood_pressure_buttons)

# Кнопка ЧСС
heart_rate_buttons = [
    [types.InlineKeyboardButton(text="Значения в пределах нормы (менее 100-110 уд/мин.):", callback_data="HR_NORM")],
    [types.InlineKeyboardButton(text="Повышение ЧСС на 1-20 уд/мин. (110-130 уд/мин.): ", callback_data="HR_1")],
    [types.InlineKeyboardButton(text="Повышение ЧСС на 20-40 уд/мин. (130-150 уд/мин.): ", callback_data="HR_2")],
    [types.InlineKeyboardButton(text="Повышение ЧСС на более 40 уд/мин. (более 150 уд/мин.): ", callback_data="HR_3")],
    [types.InlineKeyboardButton(text="Начать заново", callback_data="START")]
]
heart_rate_buttons_keyboard = types.InlineKeyboardMarkup(heart_rate_buttons)

# Кнопка ЧДД
respiratory_rate_buttons = [
        [types.InlineKeyboardButton(text="ЧДД менее 26/мин",        callback_data="BR_1")],
        [types.InlineKeyboardButton(text="ЧДД 26-30/мин",           callback_data="BR_2")],
        [types.InlineKeyboardButton(text="ЧДД более 30/мин",        callback_data="BR_3")],
        [types.InlineKeyboardButton(text="Начать заново", callback_data="START")]
    ]
respiratory_rate_keyboard = types.InlineKeyboardMarkup(respiratory_rate_buttons)

# Кнопка диуреза
diuresis_buttons = [
    [types.InlineKeyboardButton(text="Значения в пределах нормы", callback_data="DIURES_NORM")],
    [types.InlineKeyboardButton(text="Диурез более 20-30 мл/ч", callback_data="DIURES_1")],
    [types.InlineKeyboardButton(text="Диурез 5-20 мл/ч", callback_data="DIURES_2")],
    [types.InlineKeyboardButton(text="Анурия", callback_data="DIURES_3")],
    [types.InlineKeyboardButton(text="Начать заново", callback_data="START")]
]
diuresis_keyboard = types.InlineKeyboardMarkup(diuresis_buttons)

# Кнопка выбора шкалы
scale_buttons = [
    [types.InlineKeyboardButton(text="Шкала 1", callback_data="first_scale")],]
scale_keyboard = types.InlineKeyboardMarkup(scale_buttons)

# Кнопка начала работы
start_buttons = [
        [types.InlineKeyboardButton(
            text="Начать", callback_data="START")],
    ]

start_keyboard = types.InlineKeyboardMarkup(start_buttons)

# Кнопка перезапуска
again_buttons = [
        [types.InlineKeyboardButton(
            text="Начать заново", callback_data="START")],
    ]

again_keyboard = types.InlineKeyboardMarkup(again_buttons)

# 
# Перечисление всех возможных сценариев работы
# Каждый элемент в кортеже является кортежем с типами:
# UserState: хранит стадию, которую нужно обработать,
# string: сообщение, которое будет выведено при переходе к данному состоянию,
# reply__markup: кнопки, которые должны появиться при выборе текущего состояния

# Шкала с диурезом
FIRST_SCALE_STATES = ((UserStates.body_mass, 'Введите массу (в кг) тела пациентки по примеру: 60.5', None),
                      (UserStates.body_height, 'Введите рост (в метрах) пациентки по примеру: 1.78 ', None),
                      (UserStates.systolic_blood_pressure, 'Изменение систолического артериального давления (САД)\n\nИли по копке можете вернуться в главное меню', systolic_blood_pressure_keyboard),
                      (UserStates.heart_rate, 'Изменение частоты сердечных сокращений(ЧСС)\n\nИли по копке можете вернуться в главное меню', heart_rate_buttons_keyboard),
                      (UserStates.respiratory_rate, 'Изменение частоты дыхательных движений(ЧДД)\n\nИли по копке можете вернуться в главное меню', respiratory_rate_keyboard),
                      (UserStates.diuresis, 'Диурез (мл/ч)\n\nИли по копке можете вернуться в главное меню', diuresis_keyboard),
                      (UserStates.first_scale_end, '', None))


users_scale = {} # Хранит какую шкалу использует пользователь в текущем сеансе
users_data = {}  # Хранит введенные данные пользователя в текущем сеансе

# Нужно ли выводить ИМТ
is_print_mass_body_index = True

def next_state(id, state, text, keyboard):
    """
    Обработчик при переходе к слеующему состоянию
    """

    if state == UserStates.first_scale_end:
        # Обработка результатов первой шкалы с диурезом

        result = users_data[id].systolic_blood_pressure + users_data[id].heart_rate + users_data[id].respiratory_rate + users_data[id].diures 

        text = ''

        if 0 <= result <= 3:
            Vkp = (0, users_data[id].body_mass * 10)
            text = f'Физиологическая кровопотеря в размере 0-10%;\nДля данной пациентки Vкп (мл) составляет: ({Vkp[0]:.0f}, {Vkp[1]:.0f});\nПри ИМТ в пределах нормы, составляет 0-600 мл.'
        elif 4 <= result <= 8:
            Vkp = (users_data[id].body_mass * 11, users_data[id].body_mass * 30)
            text = f'''Физиологическая кровопотеря в размере 11-30%;\nДля данной пациентки Vкп (мл) составляет: ({Vkp[0]:.0f}, {Vkp[1]:.0f});\nПри ИМТ в пределах нормы, составляет 0-600 мл.
            '''
        elif 9 <= result <= 14:
            Vkp = (users_data[id].body_mass * 31, users_data[id].body_mass * 100)
            text = f'''Массивная кровопотеря в размере 31% ОЦК и более;\nДля данной пациентки Vкп (мл) составляет: ({Vkp[0]:.0f}, {Vkp[1]:.0f});\nПри ИМТ в пределах нормы, составляет более 1800 мл.
            '''
        else:
            raise Exception('Неверная логика работы программы при разбаловке первой шкалы')

        bot.send_message(id, text=text, reply_markup=keyboard)

    else:
        # Если не конец, то выводим сообщение, затем переход к следующему состоянию

        bot.send_message(id, text=text, reply_markup=keyboard)
        bot.set_state(id, state, id)

    # Если следующее состояние - конец, то удаляем все данные сеанса
    if state == UserStates.first_scale_end:
        users_scale.pop(id)
        users_data.pop(id)
        bot.delete_state(id, id)

        bot.send_message(id, text=f'Чтобы начать новый сеанс нажмите на кнопку. ', reply_markup=start_keyboard)

        

@bot.message_handler(commands=['start'])
def start(message):
    """
    Начало диалога с ботом
    """

    bot.send_message(
        message.chat.id,
        text=f'Привет, {message.from_user.first_name}, я бот для оценки риска развития и степени тяжести кровотечений '
             f'в родах. Используется госпитальная шкала оценки тяжести акушерских кровотечений.\n\n Нажми кнопку, чтобы начать.',
        reply_markup=start_keyboard)

    
@bot.callback_query_handler(func=lambda call: call.data.startswith('START'))
def new_bleeding(call):
    """
    Обнуляет предыдущий сеанс и начинает заново диалог с выбором шкалы
    """
    # Удаляем сеанс с текущим пользователем, если он существует
    users_scale.pop(call.message.chat.id, None)
    users_data.pop(call.message.chat.id, None)

    # Добавляем в словарь сеанс с данными пользователя
    users_data[call.message.chat.id] = UserData()
    # Выбираем сценарий первой шкалы
    users_scale[call.message.chat.id] = UserScale(FIRST_SCALE_STATES)

    state, text, keyboard = users_scale[call.message.chat.id].next()
    next_state(call.message.chat.id, state, text, keyboard)

#
# Функции для обработки текстовых сообщений
#

@bot.message_handler(state=UserStates.body_mass)
def ask_body_mass(message):
    """
    Обработка введения массы
    """
    # Ожиданием ввод данных от пользователя
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        # Проверяем корректно ли введены данные, если нет
        if not is_float(message.text):
            bot.send_message(message.chat.id, text='Данные введены неверно, попробуйте еще раз')
            return
        
        users_data[message.chat.id].body_mass = float(message.text)
    
    # Переход в следующее состояние
    state, text, keyboard = users_scale[message.chat.id].next()
    next_state(message.chat.id, state, text, keyboard)


@bot.message_handler(state=UserStates.body_height)
def ask_body_height(message):
    """
    Обработка введения роста
    """

    # Ожиданием ввод данных от пользователя
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        # Проверяем корректно ли введены данные, если нет
        if not is_float(message.text):
            bot.send_message(message.chat.id, text='Данные введены неверно, попробуйте еще раз')
            return
        users_data[message.chat.id].body_height = float(message.text)
    id = message.chat.id

    # Вывод индекса массы тела
    if (users_data[id].body_mass and users_data[id].body_height and is_print_mass_body_index):
        mass_body_index = users_data[id].body_mass / users_data[id].body_height / users_data[id].body_height
        if (16 <= mass_body_index <= 18.4):
            bot.send_message(id, text=f'Индекс массы тела: дефицит массы тела')
        elif (18.4 < mass_body_index <= 24.9):
            bot.send_message(id, text=f'Индекс массы тела: норма')
        elif (24.9 < mass_body_index <= 29.9):
            bot.send_message(id, text=f'Индекс массы тела: избыточная масса тела')
        elif (29.9 < mass_body_index <= 34.9):
            bot.send_message(id, text=f'Индекс массы тела: ожирение 1 степени')
        elif (mass_body_index < 16):
            bot.send_message(id, text=f'Индекс массы тела: выраженный дефицит массы тела')
        elif (34.9 < mass_body_index <= 39.9):
            bot.send_message(id, text=f'Индекс массы тела: ожирение 2 степени')
        elif (39.9 < mass_body_index <= 44.9):
            bot.send_message(id, text=f'Индекс массы тела: ожирение 3 степени')
        elif (44.9 < mass_body_index):
            bot.send_message(id, text=f'Индекс массы тела: ожирение 4 степени')

    # Переход в следующее состояние
    state, text, keyboard = users_scale[message.chat.id].next()
    next_state(message.chat.id, state, text, keyboard)


#
# Функции для обработки нажатий но кнопки
#


@bot.callback_query_handler(func=lambda call: call.data in ('CAD_NORM', 'CAD_1', 'CAD_2', 'CAD_3'))
def cad_query(call):
    """
    Обрабатывает callback на выбор САД
    """

    # В зависимости от ответа задаем разбаловку
    if call.data == 'CAD_NORM':
        users_data[call.message.chat.id].systolic_blood_pressure = 0
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Снижение САД на 1-20 мм.рт.ст')
    elif call.data == 'CAD_1':
        users_data[call.message.chat.id].systolic_blood_pressure = 1
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Снижение САД на 20-50 мм.рт.ст.')
    elif call.data == 'CAD_2':
        users_data[call.message.chat.id].systolic_blood_pressure = 2
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Снижение САД на 50-80 мм.рт.ст.')
    elif call.data == 'CAD_3':
        users_data[call.message.chat.id].systolic_blood_pressure = 3
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Снижение САД на более 80 мм.рт.ст.')

    # Меняем текущее состояние сеанса на следующее
    state, text, keyboard = users_scale[call.message.chat.id].next()
    next_state(call.message.chat.id, state, text, keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ('HR_NORM', 'HR_1', 'HR_2', 'HR_3'))
def hr_query(call):
    """
    Обрабатывает callback на выбор ЧСС
    """

    # В зависимости от ответа задаем разбаловку
    if call.data == 'HR_NORM':
        users_data[call.message.chat.id].heart_rate = 0
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='значения в пределах нормы ')
    elif call.data == 'HR_1':
        users_data[call.message.chat.id].heart_rate = 1
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Повышение ЧСС на 1-20 уд/мин.')
    elif call.data == 'HR_2':
        users_data[call.message.chat.id].heart_rate = 2
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Повышение ЧСС на 20-40 уд/мин. ')
    elif call.data == 'HR_3':
        users_data[call.message.chat.id].heart_rate = 3
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Повышение ЧСС на более 40 уд/мин.')

    # Меняем текущее состояние сеанса на следующее
    state, text, keyboard = users_scale[call.message.chat.id].next()
    next_state(call.message.chat.id, state, text, keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ('BR_1', 'BR_2', 'BR_3'))
def br_query(call):
    """
    Обрабатывает callback на выбор ЧДД
    """
    # В зависимости от ответа задаем разбаловку
    if call.data == 'BR_1':
        users_data[call.message.chat.id].respiratory_rate = 0
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='ЧДД менее 26/мин.')
    elif call.data == 'BR_2':
        users_data[call.message.chat.id].respiratory_rate = 1
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='ЧДД 26-30/мин. ')
    elif call.data == 'BR_3':
        users_data[call.message.chat.id].respiratory_rate = 2
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='ЧДД более 30/мин. ')

    # Меняем текущее состояние сеанса на следующее
    state, text, keyboard = users_scale[call.message.chat.id].next()
    next_state(call.message.chat.id, state, text, keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ('DIURES_NORM', 'DIURES_1', 'DIURES_2', 'DIURES_3'))
def diures_query(call):
    """
    Обрабатывает callback на выбор диуреза
    """

    # В зависимости от ответа задаем разбаловку
    if call.data == 'DIURES_NORM':
        users_data[call.message.chat.id].diures = 0
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Значения в пределах нормы')
    elif call.data == 'DIURES_1':
        users_data[call.message.chat.id].diures = 1
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Диурез более 20-30 мл/ч.')
    elif call.data == 'DIURES_2':
        users_data[call.message.chat.id].diures = 2
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Диурез 5-20 мл/ч.')
    elif call.data == 'DIURES_3':
        users_data[call.message.chat.id].diures = 3
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Анурия. ')

    # Меняем текущее состояние сеанса на следующее
    state, text, keyboard = users_scale[call.message.chat.id].next()
    next_state(call.message.chat.id, state, text, keyboard)

@bot.message_handler(state="*", commands=['cancel'])
def any_state(message):
    """
    Cancel state
    """
    bot.send_message(message.chat.id, "Ошибка. Обратитесь к администратору бота. Начните работу с ботом заново командой /start")
    bot.delete_state(message.from_user.id, message.chat.id)

bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)
