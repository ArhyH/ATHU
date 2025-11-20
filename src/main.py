import modules.parts
import modules.parts.weather
from modules.parts.bot import bot
from modules.helpers.helpers import initButtons
from modules.consts.consts import myKeyboards, myTypes
from modules.consts.commands import commandsList, grmCommandsList

initButtons(commandsList, myKeyboards.start, myTypes.inline)
initButtons(grmCommandsList, myKeyboards.grm, myTypes.row)


bot.polling(none_stop=True)
