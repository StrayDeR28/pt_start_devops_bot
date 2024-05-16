import logging, re, paramiko, os, psycopg2

from psycopg2 import Error
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True, verbose=True)

TOKEN = os.getenv('TOKEN')
rm_host = os.getenv('RM_HOST')
rm_port = os.getenv('RM_PORT')
rm_user = os.getenv('RM_USER')
rm_password = os.getenv('RM_PASSWORD')

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_database = os.getenv('DB_DATABASE')

db_repl_user = os.getenv('DB_REPL_USER')
db_repl_password = os.getenv('DB_REPL_PASSWORD')
db_repl_host = os.getenv('DB_REPL_HOST')
db_repl_port = os.getenv('DB_REPL_PORT')


connection = None

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8"
)
#отключение логирования
#logging.disable(logging.CRITICAL)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('''Список команд:\n 
    /find_phone_number; /find_email; /verify_password;\n 
    /get_release; /get_uname; /get_uptime;\n 
    /get_df; /get_free; /get_mpstat;\n 
    /get_w; /get_auths; /get_critical;\n 
    /get_ps; /get_ss; /get_apt_list;\n 
    /get_services; /get_repl_logs; /get_emails; \n 
    /get_phone_numbers; ''')


def find_phone_numberCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'
def find_emailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email адресса: ')

    return 'find_email'
def verify_passwordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки его надежности: ')

    return 'verify_password'
def get_apt_listCommand(update: Update, context):
    update.message.reply_text('Введите "all", чтобы узнать о всех установленных пакетах на устройстве, или введите название интересующего пакета: ')

    return 'get_apt_list'


def find_phone_number (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:\+7|8)[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{2}[ -]?\d{2}') # формат 8 (000) 000-00-00  r'((\+7|8) \(\d{3}\) \d{3}-\d{2}-\d{2})'

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        logging.info(f'Номера телефона не найдены') # логирую номера телефонов
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END # Завершаем работу обработчика диалога
    
    context.user_data['phoneNumberList'] = phoneNumberList

    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        logging.info(f'Номера телефона найдены. {i+1}) {phoneNumberList[i]}') # логирую номера телефонов
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер
        
    update.message.reply_text(f'Были найдены номера телефона:\n {phoneNumbers}') # Отправляем сообщение пользователю
    update.message.reply_text(f'Хотите записать их в базу данных? (да/нет)') # Отправляем сообщение пользователю
    
    return 'upload_phone_number'
    
def upload_phone_number(update: Update, context):
    logging.info(f'Зашел в загрузку') # логирую номера телефонов
    user_input = update.message.text.strip().lower()
    phoneNumberList = context.user_data.get("phoneNumberList", [])
    if user_input == 'да':
        try:
            connection = psycopg2.connect(user=db_user,
                                password=db_password,
                                host=db_host,
                                port=db_port, 
                                database=db_database)

            cursor = connection.cursor()
            for el in phoneNumberList:
                cursor.execute(f"INSERT INTO PhoneNumbers (PhoneNumber) VALUES ('{el}');")
                connection.commit()
            logging.info("Команда успешно выполнена")
            update.message.reply_text(f'Номер записан в базу данных') # Отправляем сообщение пользователю
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text(f'Произошла ошибка, телефон не записан') # Отправляем сообщение пользователю
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")

        return ConversationHandler.END
    else: return ConversationHandler.END

def find_email (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) email

    emailRegex = re.compile(r'[A-Za-z0-9._-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}') 

    emailList = emailRegex.findall(user_input) # Ищем email

    if not emailList: # Обрабатываем случай, когда emailв нет
        logging.info(f'Email не найдены') # логирую email
        update.message.reply_text('Email не найдены')
        return # Завершаем выполнение функции
    
    context.user_data['emailList'] = emailList

    emails = '' # Создаем строку, в которую будем записывать emailRegex
    for i in range(len(emailList)):
        logging.info(f'Email найдены. {i+1}) {emailList[i]}') # логирую email
        emails += f'{i+1}. {emailList[i]}\n' # Записываем очередной email
        
    update.message.reply_text(f'Были найдены электронные адресса:\n {emails}') # Отправляем сообщение пользователю
    update.message.reply_text(f'Хотите записать их в базу данных? (да/нет)') # Отправляем сообщение пользователю

    return 'upload_email'

def upload_email(update: Update, context):
    logging.info(f'Зашел в загрузку') # логирую номера телефонов
    user_input = update.message.text.strip().lower()
    emailList = context.user_data.get("emailList", [])
    if user_input == 'да':
        try:
            connection = psycopg2.connect(user=db_user,
                                password=db_password,
                                host=db_host,
                                port=db_port, 
                                database=db_database)

            cursor = connection.cursor()
            for el in emailList:
                cursor.execute(f"INSERT INTO Emails (Email) VALUES ('{el}');")
                connection.commit()
            logging.info("Команда успешно выполнена")
            update.message.reply_text(f'Адрес записан в базу данных') # Отправляем сообщение пользователю
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text(f'Произошла ошибка, адрес не записан') # Отправляем сообщение пользователю
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")

        return ConversationHandler.END
    else: return ConversationHandler.END

def verify_password (update: Update, context):
    user_input = update.message.text 

    if len(user_input) == 0: 
        logging.info(f'Введен пустой пароль') 
        update.message.reply_text('Вы ввели пустой пароль')
        return # Завершаем выполнение функции
    elif len(user_input) < 8:
        logging.info(f'Введен пароль из менее 8-ми символов') 
        update.message.reply_text('Пароль простой (длина меньше 8)')
        return # Завершаем выполнение функции

    passwordRegexNegative = re.compile(r'[^a-zA-Z0-9!@#$%^&*()]')
    passwordRegexLowercase = re.compile(r'[a-z]')
    passwordRegexUppercase = re.compile(r'[A-Z]') 
    passwordRegexDigit = re.compile(r'[0-9]') 
    passwordRegexSpecial = re.compile(r'[!@#$%^&*()]') 

    if passwordRegexNegative.search(user_input):
        logging.info(f'В пароле неучтенные символы') 
        update.message.reply_text('Вы ввели пароль с неизвестными символами')
        return 
    
    if not re.search(passwordRegexUppercase, user_input):
        logging.info(f'Введен пароль без заглавных') 
        update.message.reply_text('Пароль простой (без заглавных)')
        return 

    # Проверяем наличие хотя бы одной строчной буквы
    if not re.search(passwordRegexLowercase, user_input):
        logging.info(f'Введен пароль без строчных')
        update.message.reply_text('Пароль простой (без строчных)')
        return 

    # Проверяем наличие хотя бы одной цифры
    if not re.search(passwordRegexDigit, user_input):
        logging.info(f'Введен пароль без цифр') 
        update.message.reply_text('Пароль простой (без цифр)')
        return 

    # Проверяем наличие хотя бы одного специального символа
    if not re.search(passwordRegexSpecial, user_input):
        logging.info(f'Введен пароль без спец. символов')
        update.message.reply_text('Пароль простой (без спец. символов)')
        return 

    logging.info(f'Введен сложный пароль: {user_input}') 
    update.message.reply_text('Пароль сложный')
    return ConversationHandler.END 

def get_release (update: Update, context):
    
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}') 

    stdin, stdout, stderr = client.exec_command('cat /etc/*-release')

    release_info = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(release_info) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_uname (update: Update, context):
    
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}') 

    stdin, stdout, stderr = client.exec_command('uname -a')

    uname_info = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(uname_info) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_uptime (update: Update, context):
    
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}, uptime') 

    stdin, stdout, stderr = client.exec_command('uptime')

    uptime_info = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(uptime_info) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_df (update: Update, context):
    
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}, get_df') 

    stdin, stdout, stderr = client.exec_command('df -h')

    df_info = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(df_info) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_free (update: Update, context):
    
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}, get_df') 

    stdin, stdout, stderr = client.exec_command('free -m')

    freeMem_info = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(freeMem_info) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_mpstat (update: Update, context):
    
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}, get_mpstat') 

    stdin, stdout, stderr = client.exec_command('mpstat')

    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_w (update: Update, context):
    
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}, get_w') 

    stdin, stdout, stderr = client.exec_command('w')

    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_auths (update: Update, context):
    
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}, get_auths') 

    stdin, stdout, stderr = client.exec_command('last -n 10')

    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_critical (update: Update, context):
    
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}, get_critical') 

    stdin, stdout, stderr = client.exec_command('tail -n 5 /var/log/syslog')#если не будет critical - вывести все

    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_ps (update: Update, context):
    
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}, get_ps') 

    stdin, stdout, stderr = client.exec_command('ps aux | tail')

    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_ss (update: Update, context):
    
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}, get_ss') 

    stdin, stdout, stderr = client.exec_command('ss -tuln')

    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_apt_list (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий тип запроса
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}, {rm_user}, {rm_password}, {rm_port} get_apt_list') 


    if user_input == 'all':
      stdin, stdout, stderr = client.exec_command("dpkg --get-selections | grep 'install$' | head -n 10")
    else:
      stdin, stdout, stderr = client.exec_command(f"dpkg --get-selections | grep '{user_input}' | grep 'install$' | head -n 10")

    tmp = stdout.read().decode('utf-8')

    if tmp:# проверка на пустоту строки, чтобы не крашится на несуществующем пакете
      data = tmp
    else: 
      logging.info(f'Пакет: {user_input} не найден') # логирую email
      update.message.reply_text(f'Пакет: {user_input} не найден')
      return # Завершаем выполнение функции
    
    client.close()
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_services (update: Update, context):
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=rm_host, username=rm_user, password=rm_password, port=rm_port)

    logging.info(f'Подключились по ssh к {rm_host}, get_services') 

    stdin, stdout, stderr = client.exec_command('systemctl list-units --type=service --state=running | head -n 10')

    data = stdout.read().decode('utf-8')

    client.close()
    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_repl_logs (update: Update, context):
    
    try:
        connection = psycopg2.connect(user=db_user,
                                password=db_password,
                                host=db_host,
                                port=db_port, 
                                database=db_database)

        cursor = connection.cursor()
        cursor.execute("SELECT pg_read_file('/var/log/postgresql/postgres.log') LIMIT 1;")
        
        data = cursor.fetchone()[0]
        if len(data) > 3000:
            data = data[-3000:]
        lines = data.split('\n')
        if len(lines) > 20:
            data = '\n'.join(lines[-20:])
	    
        logging.info("Команда get_repl_logs успешно выполнена")
        update.message.reply_text(str(data))
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        update.message.reply_text(f'Произошла ошибка{error}') # Отправляем сообщение пользователю
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_emails (update: Update, context):

    try:
        connection = psycopg2.connect(user=db_user,
                                password=db_password,
                                host=db_host,
                                port=db_port, 
                                database=db_database)

        cursor = connection.cursor()
        cursor.execute("SELECT email FROM Emails;")
        data = cursor.fetchall() 
        logging.info("Команда get_emails успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        update.message.reply_text(f'Произошла ошибка{error}') # Отправляем сообщение пользователю
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_phone_numbers (update: Update, context):

    try:
        connection = psycopg2.connect(user=db_user,
                                password=db_password,
                                host=db_host,
                                port=db_port, 
                                database=db_database)

        cursor = connection.cursor()
        cursor.execute("SELECT PhoneNumber FROM PhoneNumbers;")
        data = cursor.fetchall() 
        logging.info("Команда get_phone_numbers успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        update.message.reply_text(f'Произошла ошибка{error}') # Отправляем сообщение пользователю
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    update.message.reply_text(data) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerfind_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_numberCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'upload_phone_number': [MessageHandler(Filters.text & ~Filters.command, upload_phone_number)],
        },
        fallbacks=[]
    )
    convHandlerfind_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_emailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'upload_email': [MessageHandler(Filters.text & ~Filters.command, upload_email)],
        },
        fallbacks=[]
    )
    convHandlerverify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )
    convHandlerget_release = ConversationHandler(
        entry_points=[CommandHandler('get_release', get_release)],
        states={
            'get_release': [MessageHandler(Filters.text & ~Filters.command, get_release)],
        },
        fallbacks=[]
    )
    convHandlerget_uname = ConversationHandler(
        entry_points=[CommandHandler('get_uname', get_uname)],
        states={
            'get_uname': [MessageHandler(Filters.text & ~Filters.command, get_uname)],
        },
        fallbacks=[]
    )
    convHandlerget_uptime = ConversationHandler(
        entry_points=[CommandHandler('get_uptime', get_uptime)],
        states={
            'get_uptime': [MessageHandler(Filters.text & ~Filters.command, get_uptime)],
        },
        fallbacks=[]
    )
    convHandlerget_df = ConversationHandler(
        entry_points=[CommandHandler('get_df', get_df)],
        states={
            'get_df': [MessageHandler(Filters.text & ~Filters.command, get_df)],
        },
        fallbacks=[]
    )
    convHandlerget_free = ConversationHandler(
        entry_points=[CommandHandler('get_free', get_free)],
        states={
            'get_free': [MessageHandler(Filters.text & ~Filters.command, get_free)],
        },
        fallbacks=[]
    )
    convHandlerget_mpstat = ConversationHandler(
        entry_points=[CommandHandler('get_mpstat', get_mpstat)],
        states={
            'get_mpstat': [MessageHandler(Filters.text & ~Filters.command, get_mpstat)],
        },
        fallbacks=[]
    )
    convHandlerget_w = ConversationHandler(
        entry_points=[CommandHandler('get_w', get_w)],
        states={
            'get_w': [MessageHandler(Filters.text & ~Filters.command, get_w)],
        },
        fallbacks=[]
    )
    convHandlerget_auths = ConversationHandler(
        entry_points=[CommandHandler('get_auths', get_auths)],
        states={
            'get_auths': [MessageHandler(Filters.text & ~Filters.command, get_auths)],
        },
        fallbacks=[]
    )
    convHandlerget_critical = ConversationHandler(
        entry_points=[CommandHandler('get_critical', get_critical)],
        states={
            'get_critical': [MessageHandler(Filters.text & ~Filters.command, get_critical)],
        },
        fallbacks=[]
    )
    convHandlerget_ps = ConversationHandler(
        entry_points=[CommandHandler('get_ps', get_ps)],
        states={
            'get_ps': [MessageHandler(Filters.text & ~Filters.command, get_ps)],
        },
        fallbacks=[]
    )
    convHandlerget_ss = ConversationHandler(
        entry_points=[CommandHandler('get_ss', get_ss)],
        states={
            'get_ss': [MessageHandler(Filters.text & ~Filters.command, get_ss)],
        },
        fallbacks=[]
    )
    convHandlerget_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )
    convHandlerget_services = ConversationHandler(
        entry_points=[CommandHandler('get_services', get_services)],
        states={
            'get_services': [MessageHandler(Filters.text & ~Filters.command, get_services)],
        },
        fallbacks=[]
    )
    convHandlerget_repl_logs = ConversationHandler(
        entry_points=[CommandHandler('get_repl_logs', get_repl_logs)],
        states={
            'get_repl_logs': [MessageHandler(Filters.text & ~Filters.command, get_repl_logs)],
        },
        fallbacks=[]
    )
    convHandlerget_emails = ConversationHandler(
        entry_points=[CommandHandler('get_emails', get_emails)],
        states={
            'get_emails': [MessageHandler(Filters.text & ~Filters.command, get_emails)],
        },
        fallbacks=[]
    )
    convHandlerget_phone_numbers = ConversationHandler(
        entry_points=[CommandHandler('get_phone_numbers', get_phone_numbers)],
        states={
            'get_phone_numbers': [MessageHandler(Filters.text & ~Filters.command, get_phone_numbers)],
        },
        fallbacks=[]
    )
		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerfind_phone_number)
    dp.add_handler(convHandlerfind_email)
    dp.add_handler(convHandlerverify_password)
    dp.add_handler(convHandlerget_release)
    dp.add_handler(convHandlerget_uname)
    dp.add_handler(convHandlerget_uptime)
    dp.add_handler(convHandlerget_df)
    dp.add_handler(convHandlerget_free)
    dp.add_handler(convHandlerget_mpstat)
    dp.add_handler(convHandlerget_w)
    dp.add_handler(convHandlerget_auths)
    dp.add_handler(convHandlerget_critical)
    dp.add_handler(convHandlerget_ps)
    dp.add_handler(convHandlerget_ss)
    dp.add_handler(convHandlerget_apt_list)
    dp.add_handler(convHandlerget_services)
    dp.add_handler(convHandlerget_repl_logs)
    dp.add_handler(convHandlerget_emails)
    dp.add_handler(convHandlerget_phone_numbers)


		
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
