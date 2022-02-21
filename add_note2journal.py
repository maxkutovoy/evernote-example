#!/usr/bin/env python 
from datetime import date, datetime, timedelta
import argparse
import json

from evernote.api.client import EvernoteClient
from config import Settings


WEEK_DAYS = {
    1: u'понедельник',
    2: u'вторник',
    3: u'среда',
    4: u'четверг',
    5: u'пятница',
    6: u'суббота',
    7: u'воскресенье',
}


def is_valid_date(text):
    text = text.strip()
    if text.startswith('-') or text.startswith('+') or text.isdigit():
        return date.today() + timedelta(days=int(text))
    try:

        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(text)
        raise argparse.ArgumentTypeError(msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Adds note to notebook "Дневник", uses template note')
    parser.add_argument(
        '--date',
        nargs='?',
        type=is_valid_date,
        help='date in format "YYYY-MM-DD"'
    )
    parser.add_argument(
        '--text',
        '-t',
        type=str,
        help='Note text'
    )
    args = parser.parse_args()

    config = Settings()

    client = EvernoteClient(
        token=config.EVERNOTE_PERSONAL_TOKEN,
        sandbox=config.SANDBOX
    )
    noteStore = client.get_note_store()

    day = args.date or date.today()
    context = {
        'date': day.isoformat(),
        'dow': WEEK_DAYS[day.isoweekday()],
    }

    new_note = noteStore.copyNote(config.JOURNAL_TEMPLATE_NOTE_GUID, config.JOURNAL_NOTEBOOK_GUID)
    utitle_without_comment = new_note.title.split('#', 1)[0]
    utitle = utitle_without_comment.strip().format(**context)
    new_note.title = utitle

    text = args.text
    new_note.content = '<?xml version="1.0" encoding="UTF-8"?>'
    new_note.content += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    new_note.content += '<en-note>'
    new_note.content += f'<div>{text}</div>'
    new_note.content += '</en-note>'

    noteStore.updateNote(new_note)
    
    print(f'Note title: "{utitle}"')
    print(f'Note text: "{text}"')
    print('Note created')
