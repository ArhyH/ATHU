from modules.consts.consts import myTypes
from modules.parts.bot import keyboards, types


def chunkList(list, chunkSize):
    for i in range(0, len(list), chunkSize):
        yield list[i : i + chunkSize]


def initButtons(buttonsList, keyboard, type="inline"):
    buttons = []
    for command in buttonsList:
        button = types.InlineKeyboardButton(
            text=command["name"],
            callback_data=command["command"],
        )
        if type == myTypes.inline:
            keyboards[keyboard].add(button)
        elif type == myTypes.row:
            buttons.append(button)
    if len(buttons) != 0:
        for chunk in chunkList(buttons, 2):
            keyboards[keyboard].row(*chunk)
