from mubert import *


import telebot
import os
import requests
import sqlite3
import hashlib
import traceback

import re



class DB():
    """
    class for mysql db
    """
    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
    
    def create_db(self):
        query = """
        create table if not exists users (
            user_id integer primary key,
            user_hash varchar(64) not null,
            user_loop int default 0,
            user_track_len integer default 120
        );
        """
        self.cursor.execute(query)
    
    def drop_db(self):
        query = """drop table if exists users;""";
        self.cursor.execute(query);
    
    def add_user(self, user_hash, user_loop: int = 0, user_track_len: int=120):
        query = "insert into users(user_hash, user_loop, user_track_len) values(?,?,?);"
        self.cursor.execute(query, (user_hash, user_loop, user_track_len))
        self.connection.commit()
        r = self.cursor.fetchall()

    def get_user_data(self, user_hash: str):
        query = "select user_loop, user_track_len from users where user_hash = ?;"
        self.cursor.execute(query, (user_hash, ))
        r = self.cursor.fetchone()
        if r:
            return bool(r[0]), r[1]
        return r
    
    def set_user_loop(self, user_hash: str, loop: bool):
        loop = int(loop)
        query = 'update users set user_loop = ? where user_hash = ?;'
        self.cursor.execute(query, (loop, user_hash))
        self.connection.commit()
    

    def set_user_track_len(self, user_hash: str, track_len: int):
        query = 'update users set user_track_len = ? where user_hash = ?;'
        self.cursor.execute(query, (track_len, user_hash))
        self.connection.commit()

  



def save_file_from_url(file_url, save_folder = "/tmp/"):
    """
    save file from file_url to save_folder and return file path
    """
    file_name = file_url.split('/')[-1]
    r = requests.get(file_url)
    if r.status_code != 200:
        return None
    file_path = os.path.join(save_folder, file_name)
    with open(file_path, "wb") as f:
        f.write(r.content)
    return file_path


def del_file(file: str):
    """
        delete file if exist or print exception
    """
    try:
        os.remove(file)
    except Exception as e:
        print(f"cant delete file {file}:\n", traceback.format_exc())        


def send_file(file: str, chat_id: int):
    """
    senf file to telegram chat_id
    """
    # отправлут файл с именем file в чат c chat_id в телеграм
    try:
        with open(file=file, mode='rb') as f:
            bot.send_document(
                chat_id=chat_id,
                document=f
            )
    except Exception as e:
        print(f"cant send file {file}\n", traceback.format_exc())

def get_hash(hash_string: str):
    """
    get sha256 hash from string
    """
    return hashlib.sha256(hash_string.encode("utf-8")).hexdigest()

def get_user_string(message):
    """
    convert user_id + user_credentials to string
    """
    user_string = str(message.from_user.id) + str(message.from_user.username) + \
                str(message.from_user.first_name) + str(message.from_user.last_name)
    return user_string

def get_user_hash(user_message):
    """
    calculate sha256 hash from user credentials
    """
    return get_hash(get_user_string(user_message))




TEL_API_TOKEN = os.environ.get("TEL_API_TOKEN")
MUBERT_EMAIL = os.environ.get("MUBERT_EMAIL")
DB_FILENAME = "mubert_users.db"
MAX_DURATION = 600


bot = telebot.TeleBot(token=TEL_API_TOKEN)

db = DB(DB_FILENAME)
db.create_db()
del db

print(f"telegram bot started for {MUBERT_EMAIL}")



@bot.message_handler(commands=["start"])
def print_start(message):
    db = DB(DB_FILENAME)
    user_hash = get_user_hash(message)
    db.add_user(user_hash)

    example_tags = 'action,kids,neo-classic,pumped,jazz / funk dubtechno,electro,disco house,electronic'
    text="Send list of music tags to bot\n\nExample tags:\n" + '\n'.join(example_tags.split(',')) + "\n\nBased on mubert demo https://github.com/MubertAI/Mubert-Text-to-Music"
    bot.send_message(
        chat_id = message.chat.id,
        text=text
    )

@bot.message_handler(commands=["help"])
def print_welcome(message):
    example_tags = 'action,kids,neo-classic,pumped,jazz,funk,dubtechno,house,electronic'
    text="Send list of music tags or any phrase describing music.\n\nTo change track length type: `+10` or `-5` or `=60` seconds respectively.\n\nExample tags:\n" + '\n'.join(example_tags.split(','))
    bot.send_message(
        chat_id = message.chat.id,
        text=text
    )

@bot.message_handler(commands=["about"])
def print_help(message):
    text = f"based on mubert demo https://github.com/MubertAI/Mubert-Text-to-Music"
    bot.send_message(
        chat_id = message.chat.id,
        text=text
    )

@bot.message_handler(commands=["status"])
def print_status(message):
    db = DB(DB_FILENAME)
    user_hash = get_user_hash(message)
    user_data = db.get_user_data(user_hash)
        
    if not user_data:
        text = f"no data for user {user_hash}\ntry command /start for adding a user to database"
        msg1 = bot.send_message(
            chat_id = message.chat.id,
            text = text
        )
        return

    text = f"""loop_mode = {["track", "loop"][user_data[0]]}\ntrack len: {user_data[1]} seconds"""    
    msg1 = bot.send_message(
        chat_id = message.chat.id,
        text = text
    )

@bot.message_handler(commands=["loop"])
def chenge_loop_mode(message):
    db = DB(DB_FILENAME)
    user_hash = get_user_hash(message)
    user_data = db.get_user_data(user_hash)
    if not user_data:
        text= f"No user in database, try /start for adding user"
        bot.reply_to(
            message = message,
            text = text
        )
        return
    
    user_loop = user_data[0]
    new_user_loop = not user_loop

    db.set_user_loop(user_hash, new_user_loop)

    user_data = db.get_user_data(user_hash)

    text = f"""loop_mode = {["track", "loop"][user_data[0]]}\ntrack len: {user_data[1]} seconds"""    

    bot.reply_to(
        message = message,
        text = text
    )

@bot.message_handler()
def get_tokens(message):

    db = DB(DB_FILENAME)
    user_hash = get_user_hash(message)
    user_data = db.get_user_data(user_hash)
    if not user_data:
        text= f"No user in database, try /start for adding user"
        bot.reply_to(
            message = message,
            text = text
        )
        return



    duration = user_data[1]
    is_loop = bool(user_data[0])

    prompt = message.text

    re_pos = re.match(r"^\+\d+", prompt)
    re_neg = re.match(r"^-\d+", prompt)
    re_set = re.match(r"^=\d+", prompt)

    if re_pos or re_neg or re_set:
        print(f"duration change:")
        if re_pos:
            print(re_pos.group())
            duration += int(re_pos.group())
        elif re_neg:
            print(re_neg.group())
            duration += int(re_neg.group())
        else:
            print(re_set.group())
            duration = int(re_set.group()[1:])
        duration = min(max(1, duration), MAX_DURATION)  # limiting to 0..MAX_DURATION
        db.set_user_track_len(user_hash, duration)
        user_data = db.get_user_data(user_hash)

        text = f"""loop_mode = {["loop", "track"][user_data[0]]}\ntrack len: {user_data[1]} seconds"""    

        bot.reply_to(
            message = message,
            text = text
        )
        return

    print(f"prompt = {prompt}")
    email = MUBERT_EMAIL

    message_start = bot.reply_to(
        message = message,
        text=f"Request send. Please wait."
    )

    out, result_msg, tags = generate_track_by_prompt(email, prompt, duration, is_loop)

    # tags processing
    new_tags = []
    print(f"old tags: {tags}")
    for tag in tags:
        elements = tag.strip().split("/")
        for element in elements:
            new_tags.append(f'#{element.strip().replace(" ", "_")}')
    print(f"new tags: {new_tags}")

    tags = f"{' '.join(new_tags)} {['', '#loop '][is_loop]}#mubert"
    print(f"Generate track out: {out}\n{result_msg}\n{tags}\n\n") 
    text = f"An Error occured during response to https://mubert.com\nException.\nTry different track length."
    if out:
        text = f"All music is generated by Mubert API – www.mubert.com.\n{out}\n{tags}"
        # text = f"{tags}"
        
    bot.edit_message_text(
        chat_id = message.chat.id,
        message_id = message_start.message_id,
        text = text
    )

    if out:
        file_path = save_file_from_url(out)
        if file_path:

            with open(file_path, "rb") as f:
                bot.send_audio(
                    chat_id = message.chat.id,
                    audio = f
                )
            del_file(file_path)    



if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True, timeout=20, interval=2)
        except Exception as e:
            print(str(e))
            time.sleep(20)
