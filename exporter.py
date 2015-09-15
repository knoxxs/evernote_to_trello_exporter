__author__ = 'aapa'

import warnings

from trello import TrelloClient
import html2text

TRELLO_BOARD_NAME = "xxxx"
TRELLO_LIST_NAME = "xxxx"
EVERNOTE_NOTEBOOK_NAME = 'xxxx'
NUM_EVERNOTE_NOTES = 100


def fetch_evernote_notes():
    global notes, title
    from evernote.edam.notestore import NoteStore
    from evernote.edam.userstore import constants as user_store_constants
    from evernote.api.client import EvernoteClient
    # Real applications authenticate with Evernote using OAuth, but for the
    # purpose of exploring the API, you can get a developer token that allows
    # you to access your own Evernote account. To get a developer token, visit
    # https://sandbox.evernote.com/api/DeveloperToken.action
    # sandbox
    # sandbox_auth_token = \
    #     "xxx"
    # Initial development is performed on our sandbox server. To use the production
    # service, change sandbox=False and replace your
    # developer token above with a token from
    # https://www.evernote.com/api/DeveloperToken.action
    # client = EvernoteClient(token=sandbox_auth_token, sandbox=True)
    # original
    production_auth_token = \
        "xxxx"
    evernote_client = EvernoteClient(token=production_auth_token, sandbox=False)

    # get user store
    user_store = evernote_client.get_user_store()
    # check if API version is fine
    version_ok = user_store.checkVersion(
        "Evernote EDAMTest (Python)",
        user_store_constants.EDAM_VERSION_MAJOR,
        user_store_constants.EDAM_VERSION_MINOR
    )
    print "Is my Evernote API version up to date? ", str(version_ok)
    if not version_ok:
        exit(1)

    # get notes store
    note_store = evernote_client.get_note_store()
    # search for the notebook named ideas
    note_filter = NoteStore.NoteFilter()
    note_filter.words = 'notebook:"{}"'.format(EVERNOTE_NOTEBOOK_NAME)
    notes_metadata_result_spec = NoteStore.NotesMetadataResultSpec()
    notes_metadata_list = note_store.findNotesMetadata(note_filter, 0, NUM_EVERNOTE_NOTES, notes_metadata_result_spec)
    # get all the notes in the ideas notebook
    notes = {}
    print "Fetching notes..."
    for note_metadata in notes_metadata_list.notes:
        note_guid = note_metadata.guid

        # fetch complete note
        note = note_store.getNote(note_guid, True, True, False, False)
        title = note.title
        notes[title] = note.content

        if None != note.resources:
            print "resources are present for card: {}".format(title)

    return notes


def get_trello_list():
    # connect to trello
    trello_api_key = 'xxxx'
    trello_api_secret = 'xxxx'
    # this oauth token and secret are fetched using trello_oauth_util.py
    trello_oauth_token = "xxxx"
    trello_oauth_token_secret = "xxxx"
    trello_client = TrelloClient(api_key=trello_api_key, api_secret=trello_api_secret, token=trello_oauth_token,
                                 token_secret=trello_oauth_token_secret)
    # fetch the desired board
    # noinspection PyTypeChecker
    for board in trello_client.list_boards():
        if TRELLO_BOARD_NAME == board.name:
            for board_list in board.all_lists():
                if TRELLO_LIST_NAME == board_list.name:
                    return board_list


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    print "####### Getting notes from evernote..."
    evernote_notes = fetch_evernote_notes()
    print "{} notes fetched from evernote".format(len(evernote_notes))

    print "\n####### Fetching trello list to create new cards"
    trello_list = get_trello_list()

    print "\n####### Creating cards from notes..."
    counter = 1
    for title, content in evernote_notes.iteritems():
        content = html2text.html2text(content.decode('utf-8'))
        card = trello_list.add_card(title, desc=content)
        print "Card created: [{}] {}".format(counter, title)
        counter += 1

    print "\n####### Phew! Bye."
