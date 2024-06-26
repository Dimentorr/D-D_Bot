# D&D Bot
Данный бот предназначен для организации d&d сессий:
   - [x] Создание и хранение листов персонажей игроков
   - [x] Создание супер-групп, для общения игроков и мастера игры
   - [x] Привязка ранее созданых листов персонажей к игровой компании<br>
      (в супер-группе которой остальные участники компании могут получить доступ к нему) <br>
   - [ ] Напоминаний о времени проведения игры 
   - [ ] Личный кабинет (изменение логина, пароля, список персонажей)
   - [ ] Возможность генерации предыстории персонажа(возможно и сам лист персонажа) с помощью ChatGPT
###
Для запуска бота необходимо импортировать все фалы из репозитория, а так же создать в папке проекта дополнительные папки:
   - file/db
   - file/json
Так же необходимо переименовать файл .public_env -> .env и заменить временные значения переменных необходимыми значениями
   - TOKEN=Токен телеграм бота, при отсутствии необходимо создать бота и получить токен через @BotFather
   - BOT_NAME=@Имя_(пользователя)_бота 
   - ADMIN_USERNAME=@Имя_пользователя_администратора_бота
   - DB_host=127.0.0.1(заполнять при наличии MySQL базы, в ином случаи можно не трогать)
   - DB_port=3306(заполнять при наличии MySQL базы, в ином случаи можно не трогать)
   - DB_database=test(заполнять при наличии MySQL базы, в ином случаи можно не трогать)
   - DB_user=root(заполнять при наличии MySQL базы, в ином случаи можно не трогать)
   - DB_password=(заполнять при наличии MySQL базы, в ином случаи можно не трогать)
   - create_table=1/0 (1 - необходимо создать таблицы в базе данных/0 - пропустить шаг создания таблиц, при запуске бота)
   - api_id_pyrogram=(узнать можно перейдя по <a href="https://my.telegram.org/apps">ссылке</a>)
   - api_hash_pyrogram=(узнать можно перейдя по <a href="https://my.telegram.org/apps">ссылке</a>)
   - google_api_key=(необходимо авторизоваться и создать проект в <a href="https://console.cloud.google.com/">Google cloud</a>)
   - google_api_service_key=(необходимо авторизоваться и создать проект в <a href="https://console.cloud.google.com/">Google cloud</a>)
   - google_mail_sender=(email сервисного аккаунта в <a href="https://console.cloud.google.com/">Google cloud</a>)
   - google_api_client_secret=file/json/client_secret.json(после создания проекта в <a href="https://console.cloud.google.com/">Google cloud</a>) на вкладке Credentails создать OAuth 2.0 Client IDs)
   - google_api_path_credential=file/json/credential.json (после создания сервисного аккаунта переходим в его редактирование и во вкладке keys выбираем add key->json)
   - google_api_path_token=file/json/token.json (создастся, при отсутствии, но в этом случаи необходимо будет подтвердить это действие со своего браузера)
   - path_sqlite_db=file/db/bot_base.db (путь до SQLite базы)
   - YOOMONEY_CLIENT_ID=YOUR_CLIENT_ID
   - YOOMONEY_REDIRECT_URI=YOUR_REDIRECT_URI
   - YOOMONEY_TOKEN=YOUR_TOKEN
   - YOOMONEY_RECEIVER=YOUR_RECEIVER
####
> <a href="https://gist.github.com/br4instormer/23745134ea82e9ce0a96b173bd3f2e6e#get-keys">Инструкция как создать сервисный аккаунт и ключи для проекта Google Drive API</a>
####
> Для лучшего понимания где и как получить данные от Yoomoney рекомендую посетить <a href="https://github.com/AlekseyKorshuk/yoomoney-api/tree/master?tab=readme-ov-file#access-token">этот репозиторий</a>
> 
 Для запуска прокта потребуется:
 - Установить python и pip, если они не установлены
 - Рекомендуется создать виртуальное окружение и активировать его
> Убедитесь, что в момент ввода команд в терминал вы находитесь в том же каталоге с ботом
```
python -m venv venv
# для Linux
soutse venv/bin/activate
# для Windows
venv\Scripts\activate
```
- Установите зависимости проекта для разработки
```
pip install -r requirements.txt
```
- Теперь запустим pyro.py для создания сессии
> после запуска, (при отсутствии в корневом каталоге проекта файла my_account.session) в терминале поочерёдно появятся вопросы, на которые необходимо ответить, после чего появится файл my_account.session 
```
python pyro.py
```
- Теперь можно запускать бота:
```
python main.py
```