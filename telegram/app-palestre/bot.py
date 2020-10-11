import logging
import datetime
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from picklepersistencejobs import PicklePersistenceJobs

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

week = [["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]]

def start(update, context):
    update.message.reply_text("Ciao! Usa il comando /aggiungi_giorno per impostare un avviso per quel giorno")

def alarm(context):
    job = context.job
    context.bot.send_message(job.context, text="Ricordati di prenotarti su App Palestre!")

def add_day(update, context):
    update.message.reply_text("Scegli il giorno", reply_markup=ReplyKeyboardMarkup(week, one_time_keyboard=True))
    return 0

def add_hour(update, context):
    if 'day' in context.chat_data:
        context.chat_data['day'].append(update.message.text)
    else:
        context.chat_data['day'] = [update.message.text]
    update.message.reply_text("Ora scrivi l'orario nel formato hh:mm", reply_markup=ReplyKeyboardRemove())
    return 1

def confirm(update, context):
    hour = update.message.text
    try:
        h = int(hour.split(":")[0])
        m = int(hour.split(":")[1])
        if 'h' in context.chat_data:
            context.chat_data['h'].append(hour)
        else:
            context.chat_data['h'] = [hour]

        last = len(context.chat_data['h'])-1
        update.message.reply_text("Ho aggiunto un avviso per la lezione di " + context.chat_data['day'][last] + " alle ore " + context.chat_data['h'][last])
        t = datetime.time(h, m, 00, 000000)
        day = (week[0].index(context.chat_data['day'][last]) - 2) % len(week[0])
        new_job = context.job_queue.run_daily(alarm, t, days=(day,), context = update.message.chat_id)
        if 'job' in context.chat_data:
            context.chat_data['job'].append(new_job)
        else:
            context.chat_data['job'] = [new_job]
        return ConversationHandler.END
        
    except (ValueError):
        update.message.reply_text("Orario nel formato sbagliato")
        return ConversationHandler.END
        
def list_days(update, context):
    if 'day' not in context.chat_data or len(context.chat_data['day'])==0:
        update.message.reply_text("Nessun giorno attualmente impostato")
        return
    string = ""
    for i in range(len(context.chat_data['day'])):
        if i != 0:
            string += "\n"
        string += str(i+1) + ". " + context.chat_data['day'][i] + " alle ore " + context.chat_data['h'][i]
    update.message.reply_text(string)

def remove_day(update, context):
    string = ""    
    choices = [[]]
    for i in range(len(context.chat_data['day'])):
        if i != 0:
            string +="\n"
        string += str(i+1) + ". " + context.chat_data['day'][i] + " alle ore " + context.chat_data['h'][i]
        choices[0].append(str(i+1))
    update.message.reply_text("Ho in memoria le seguenti lezioni: \n\n" + string + "\n\nQuale vuoi eliminare?", reply_markup=ReplyKeyboardMarkup(choices, one_time_keyboard=True))
    return 0

def confirm_remove(update, context):
    try:
        index = int(update.message.text)
        job = context.chat_data['job'][index-1]
        job.schedule_removal()
        update.message.reply_text("Ho correttamente rimosso la seguente lezione: " + context.chat_data['day'][index-1] + " alle ore " + context.chat_data['h'][index-1], reply_markup = ReplyKeyboardRemove())
        del context.chat_data['day'][index-1]
        del context.chat_data['h'][index-1]
        del context.chat_data['job'][index-1]
    except (ValueError):
        update.message.reply_text("Qualcosa è andato storto...", reply_markup = ReplyKeyboardRemove())
    return ConversationHandler.END

def cancel(update, context):
    if len(context.chat_data['day']) != len(context.chat_data['h']):
        del context.chat_data['day'][len(context.chat_data['day']-1)]
    update.message.reply_text("Operazione annullata")
    return ConcersationHandler.END

def list_jobs(update, context):
    l = context.job_queue.jobs()
    for job in l:
        update.message.reply_text(str(job))

def main():
    # TODO PicklePersistence tries to save on disk Jobs objects (that are thread_locked) that are saved in chat_data
    # this means that it failes to dump the pickle and when it restarts, it fails to reload the pickle (it is 0 bytes)
    # In this case it is better to create a new PicklePersistence class to avoid saving Jobs contained in chat_data
    # and, possibly, to recreate jobs when the data are loaded again (remember that all the data for the creation of
    # the job are saved in user_data and in bot_data)
    my_persistence = PicklePersistenceJobs("/app/data/storage.pickle", single_file=False)
    f = open("./API_KEY.txt", "r")
    api_key = f.read().strip()
    f.close()
    updater = Updater(api_key, persistence = my_persistence, use_context = True)
    dp = updater.dispatcher

    # Here we have to restore all the jobs that are lost in the bot restart (if any)

    for cid in dp.chat_data:
        if 'job' not in dp.chat_data[cid]:
            continue
        dp.chat_data[cid]['job'] = []
        for i in range(len(dp.chat_data[cid]['h'])):
            hour = dp.chat_data[cid]['h'][i]
            h = int(hour.split(":")[0])
            m = int(hour.split(":")[1])
            t = datetime.time(h, m, 00, 000000)
            day = (week[0].index(dp.chat_data[cid]['day'][i]) - 2) % len(week[0])
            new_job = dp.job_queue.run_daily(alarm, t, days=(day,), context = int(cid))
            dp.chat_data[cid]['job'].append(new_job)
            logging.info("Restored job for chat id %s on day %s at %s", cid, dp.chat_data[cid]['day'][i], hour)

    conv_handler = ConversationHandler(
            entry_points=[CommandHandler("aggiungi_giorno", add_day)],
            states={
                0: [MessageHandler(Filters.all, add_hour)],
                1: [MessageHandler(Filters.all, confirm)]
                },
            fallbacks = [CommandHandler('annulla', cancel)])
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("elenco_giorni", list_days))
    dp.add_handler(CommandHandler("jobs", list_jobs))
    
    conv_handler2 = ConversationHandler(
            entry_points=[CommandHandler("rimuovi_giorno", remove_day)],
            states = {
                0: [MessageHandler(Filters.all, confirm_remove)]
            },
            fallbacks = [CommandHandler('annulla', cancel)])
    dp.add_handler(conv_handler2)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
        
    
