#!/usr/bin/env python 
import argparse

from evernote.api.client import EvernoteClient
from evernote.api.client import NoteStore
from bs4 import BeautifulSoup

from config import Settings

    
def get_notebook_list(note_store, notebook_guid, number=10, offset=0):
    _filter = NoteStore.NoteFilter(notebookGuid=notebook_guid)
    resultSpec = NoteStore.NotesMetadataResultSpec(
        includeTitle=True,
        includeContentLength=True,
        includeCreated=True,
        includeUpdated=True,
        includeDeleted=False,
        includeUpdateSequenceNum=True,
        includeNotebookGuid=False,
        includeTagGuids=True,
        includeAttributes=True,
        includeLargestResourceMime=True,
        includeLargestResourceSize=True,
    )

    # this determines which info you'll get for each note
    return note_store.findNotesMetadata(_filter, offset, number, resultSpec);


if __name__ == '__main__':
    config = Settings()

    parser = argparse.ArgumentParser(description=u'Dumps notes from Evernote inbox to console')
    parser.add_argument('--number',
                        nargs='?',
                        type=int,
                        default=10,
                        help='number of records to dump')
    parser.add_argument('--notebook_id',
                        nargs='?',
                        type=str,
                        default=config.INBOX_NOTEBOOK_GUID,
                        help='Notebook ID for dump notes')
    args = parser.parse_args()

    client = EvernoteClient(
        token=config.EVERNOTE_PERSONAL_TOKEN,
        sandbox=config.SANDBOX
    )
    note_store = client.get_note_store()

    notes = get_notebook_list(note_store, config.INBOX_NOTEBOOK_GUID, args.number).notes

    # print('Notes', notes)
    
    for counter, note in enumerate(notes, start=1):
        print(f'\n--------- {counter} ---------')
        print(f'Note id: {note.guid}')
        print(f'Note title: {note.title}')
        content = note_store.getNoteContent(note.guid)  # kwargs will be skipped by api because of bug
        soup = BeautifulSoup(content, "html.parser")
        print(soup.get_text())
