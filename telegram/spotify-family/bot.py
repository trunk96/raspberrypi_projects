import logging
import datetime
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, PicklePersistence

import pytz

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

HOUR_TO_SEND = 11
MINUTE_TO_SEND = 0


def start(update, context):
    update.message.reply_text("Ciao! Indicami il giorno del mese in cui vuoi che ti avverta")
    return 0

def alarm(context):
    job = context.job
    context.bot.send_message(job.context, text="Scadenza Pagamento")

def confirm(update, context):
    day = update.message.text
    global jobs
    try:
        day = int(day)
        context.chat_data['day'] = [day]
        context.chat_data['h'] = HOUR_TO_SEND
        context.chat_data['m'] = MINUTE_TO_SEND
        update.message.reply_text("Ho aggiunto un avviso per il giorno "+str(contex.chat_data['day'])+" di ogni mese")
        #t = pytz.timezone("Europe/Rome").localize(datetime.datetime.combine(datetime.datetime.today(), datetime.time(h, m, 00, 000000))).timetz()
        t = datetime.time(context.chat_data["h"], context.chat_data["m"], 00, 000000, pytz.timezone("Europe/Rome"))

        new_job = context.job_queue.run_monthly(alarm, t, day=day, context = update.message.chat_id)

        logging.info("Added new job for chat %s on day %s at %s", update.message.chat_id, day, hour)

        jobs[update.message.chat_id] = [new_job]
        return ConversationHandler.END
        
    except (ValueError):
        update.message.reply_text("Giorno nel formato sbagliato")
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
    update.message.reply_text("Ho in memoria le seguenti promemoria: \n\n" + string + "\n\nQuale vuoi eliminare?", reply_markup=ReplyKeyboardMarkup(choices, one_time_keyboard=True))
    return 0

def confirm_remove(update, context):
    global jobs
    try:
        index = int(update.message.text)
        job = jobs[update.message.chat_id][index-1]
        job.schedule_removal()
        update.message.reply_text("Ho correttamente rimosso il seguente promemoria: " + context.chat_data['day'][index-1] + " alle ore " + context.chat_data['h'][index-1], reply_markup = ReplyKeyboardRemove())
        del context.chat_data['day'][index-1]
        del context.chat_data['h'][index-1]
        del context.chat_data['m'][index-1]
        del jobs[update.message.chat_id][index-1]
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
        update.message.reply_text(str(job.next_t))

jobs = {}

def main():

    my_persistence = PicklePersistence("/app/data/storage.pickle", single_file=False)
    f = open("./API_KEY.txt", "r")
    api_key = f.read().strip()
    f.close()
    updater = Updater(api_key, persistence = my_persistence, use_context = True)
    dp = updater.dispatcher
    global jobs
    #dp.job_queue.scheduler.configure(timezone=pytz.timezone("Europe/Rome"))

    # Here we have to restore all the jobs that are lost in the bot restart (if any)

    for cid in dp.chat_data:
        if 'h' not in dp.chat_data[cid]:
            continue
        for i in range(len(dp.chat_data[cid]['h'])):
            hour = dp.chat_data[cid]['h'][i]
            h = int(hour.split(":")[0])
            m = int(hour.split(":")[1])
            #t = pytz.timezone("Europe/Rome").localize(datetime.datetime.combine(datetime.datetime.today(), datetime.time(h, m, 00, 000000))).timetz()
            t = datetime.time(h, m, 00, 000000, pytz.timezone("Europe/Rome"))
            day = (week[0].index(dp.chat_data[cid]['day'][i]) - 2) % len(week[0])
            new_job = dp.job_queue.run_daily(alarm, t, days=(day,), context = int(cid))
            if cid not in jobs:
                jobs[cid] = []
            jobs[cid].append(new_job)
            logging.info("Restored job for chat id %s on day %s at %s", cid, dp.chat_data[cid]['day'][i], hour)

    conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                0: [MessageHandler(Filters.all, confirm)]
                },
            fallbacks = [CommandHandler('annulla', cancel)])
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("mostra_giorno", list_days))
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