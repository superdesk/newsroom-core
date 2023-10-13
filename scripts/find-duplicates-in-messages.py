import pathlib

msg_ids = set()

with open(pathlib.Path(__file__).parent.parent.joinpath("messages.pot"), "rt") as messages_file:
    for line in messages_file.readlines():
        if line.startswith("msgid"):
            _id = line.lower().strip()
            if _id == 'msgid ""':
                continue
            if _id in msg_ids:
                print("DUPLICATE", _id)
            else:
                msg_ids.add(_id)
