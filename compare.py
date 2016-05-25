from sys import intern
from collections import defaultdict
from pickle import load

import pdb


class ChatLine:
    def __init__(self, time, username, text):
        self.time = time
        self.username = intern(username)
        self.text = text.strip()

    def __hash__(self):
        return hash((self.time, self.username, self.text))

    def __eq__(self, other):
        return (self.time == other.time and self.username == other.username and
                self.text == other.text)

    def __repr__(self):
        return "ChatLine({}, {}, '{}')".format(self.time, repr(self.username),
                                               repr(self.text))

class ArchivePage:
    """Track multiple versions of a page through time."""
    def __init__(self, page):
        self._page = page
        self._by_date = defaultdict(set)

    def add_line(self, chat_line, archive_date):
        self._by_date[archive_date].add(chat_line)

    def self_consistent(self):
        sets = list(self._by_date.values())
        for set_a, set_b in zip(sets, sets[1:]):
            if set_a != set_b:
                return False
        return True
    
    def all_contain(self, chat_line):
        for version in self._by_date.values():
            if chat_line not in version:
                return False
        return True
            
print("Loading bitcoinstats website data.")
with open("items_all.pickle", "rb") as pickle_file:
    bitcoinirc_website = load(pickle_file)

bitcoin_irc_lines = [ChatLine(item["time"], item["username"], item["text"])
                     for item in bitcoinirc_website]

print("Loading wayback machine data.")
with open("wayback_archive_all.pickle", "rb") as pickle_file:
    wayback_archive = load(pickle_file)

print("Building page archives.")
page_map = dict()
for archive_item in wayback_archive:
    chat_line = ChatLine(archive_item["time"], archive_item["username"],
                         archive_item["text"])
    page = archive_item["time"].date()
    if page not in page_map:
        page_map[page] = ArchivePage(page)
    page_map[page].add_line(chat_line, archive_item["archive_time"])

# print("checking self consistency.")
# for page, archive in page_map.items():
#     if not archive.self_consistent():
#         print(page)

print("Checking consistency with current website.")
mismatch = []
for chat_line in bitcoin_irc_lines:
    if chat_line.time.date() not in page_map:
        continue
    expected_page = page_map[chat_line.time.date()]
    if not expected_page.all_contain(chat_line):
        mismatch.append(expected_page)

print(len(mismatch))
