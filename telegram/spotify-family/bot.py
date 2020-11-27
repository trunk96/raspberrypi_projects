import logging
import datetime
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, PicklePersistence
import calendar

import pytz

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

HOUR_TO_SEND = 11
MINUTE_TO_SEND = 0


def start(update, context):
    update.message.reply_text("Ciao! Indicami il giorno del mese in cui vuoi che ti avverta")
    return 0

def alarm(context):
    job = context.job
    string = "Scadenza Pagamento\n Situazione attuale:"
    for name in context._dispatcher.chat_data[job.context]:
        if name != 'day' and name != 'h' and name != 'm':
            string += "\n" + name + " -> ultimo mese: " + context._dispatcher.chat_data[job.context][name].strftime("%m/%Y")
    context.bot.send_message(job.context, text=string)

def confirm(update, context):
    day = update.message.text
    global jobs
    try:
        day = int(day)
        context.chat_data['day'] = day
        context.chat_data['h'] = HOUR_TO_SEND
        context.chat_data['m'] = MINUTE_TO_SEND
        update.message.reply_text("Ho aggiunto un avviso per il giorno "+str(context.chat_data['day'])+" di ogni mese")
        #t = pytz.timezone("Europe/Rome").localize(datetime.datetime.combine(datetime.datetime.today(), datetime.time(h, m, 00, 000000))).timetz()
        t = datetime.time(context.chat_data["h"], context.chat_data["m"], 00, 000000, pytz.timezone("Europe/Rome"))

        new_job = context.job_queue.run_monthly(alarm, t, day=day, context = update.message.chat_id)

        logging.info("Added new job for chat %s on day %s at %s", update.message.chat_id, day, context.chat_data['h'])

        jobs[update.message.chat_id] = new_job
        return ConversationHandler.END
        
    except (ValueError):
        update.message.reply_text("Giorno nel formato sbagliato")
        return ConversationHandler.END
        
def list_days(update, context):
    if 'day' not in context.chat_data:
        update.message.reply_text("Nessun giorno attualmente impostato")
        return
    string = str(context.chat_data['day']) + " alle ore " + str(context.chat_data['h'])
    update.message.reply_text(string)

def remove_day(update, context):
    update.message.reply_text("Ho correttamente rimosso il seguente promemoria: " + context.chat_data['day'] + " alle ore " + context.chat_data['h'])
    del context.chat_data['day']
    del context.chat_data['h']
    del context.chat_data['m']
    del jobs[update.message.chat_id]
    return 0

def list_jobs(update, context):
    l = context.job_queue.jobs()
    for job in l:
        update.message.reply_text(str(job.next_t))

def pagati(update, context):
    update.message.reply_text("Indica il nome e quanti mesi")
    return 0

names = ["ALESSANDRA", "ALESSANDRO", "EMANUELE", "GIANLUCA", "MONICA", "TIZIANO"]
def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)

def confirm_pagati(update, context):
    string = update.message.text
    try:
        name = string.split(",")[0].upper()
        months = int(string.split(",")[1])
        if name not in names:
            update.message.reply_text("Nome non esistente, riprova")
            return 0
        context.chat_data[name] = add_months(context.chat_data[name], months)
        update.message.reply_text("Aggiornato: "+ name + " -> ultimo mese: " +context.chat_data[name].strftime("%m/%Y"))
        logging.info("Updated: "+ name + " -> last_month: " +context.chat_data[name].strftime("%m/%Y"))
        return ConversationHandler.END
    except:
        update.message.reply_text("Indica il nome e quanti mesi nel formato \"Nome\", \"numero_mesi\"")
        return 0

def payments(update, context):
    string = "Situazione attuale:"
    for name in context.chat_data:
        if name != 'day' and name != 'h' and name != 'm':
            string += "\n" + name + " -> ultimo mese: " + context.chat_data[name].strftime("%m/%Y")
    update.message.reply_text(string)


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
        if 'day' not in dp.chat_data[cid]:
            continue
        h = dp.chat_data[cid]['h']
        m = dp.chat_data[cid]['m']
        #t = pytz.timezone("Europe/Rome").localize(datetime.datetime.combine(datetime.datetime.today(), datetime.time(h, m, 00, 000000))).timetz()
        t = datetime.time(h, m, 00, 000000, pytz.timezone("Europe/Rome"))
        day = dp.chat_data[cid]['day']
        new_job = dp.job_queue.run_monthly(alarm, t, day=day, context = int(cid))
        jobs[cid] = new_job
        logging.info("Restored job for chat id %s on day %s at %s", cid, dp.chat_data[cid]['day'], h)

        if names[1] not in dp.chat_data[cid]:
            for name in names:
                dp.chat_data[cid][name] = datetime.date.today()


    conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                0: [MessageHandler(Filters.all, confirm)]
                },
                fallbacks = [None])
    dp.add_handler(conv_handler)
    conv_handler2 = ConversationHandler(
            entry_points=[CommandHandler("ricevuti", pagati)],
            states={
                0: [MessageHandler(Filters.all, confirm_pagati)]
                },
                fallbacks = [None])
    dp.add_handler(conv_handler2)
    dp.add_handler(CommandHandler("mostra_giorno", list_days))
    dp.add_handler(CommandHandler("jobs", list_jobs))
    dp.add_handler(CommandHandler("rimuovi_giorno", remove_day))
    dp.add_handler(CommandHandler("mostra_situazione_pagamenti", payments))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()