from dotenv import load_dotenv
import os
from utils import *
import numpy as np
from .keras.NNet import NNetWrapper as NNet
from .TicTacToePlayers import *
from .TicTacToeGame import TicTacToeGame
from .TicTacToeLogic import Board
import telebot


from MCTS import MCTS
import sys
sys.path.append('..')


load_dotenv()  # take environment variables from .env.


class TicTacToeBot(telebot.TeleBot):
    def __init__(self, token, parse_mode=None) -> None:
        telebot.TeleBot.__init__(self, token, parse_mode)


def convert_to_ch(int):
    match int:
        case 0:
            return 'A'
        case 1:
            return 'B'
        case 2:
            return 'C'
        case 3:
            return 'D'
        case 4:
            return 'E'
        case 5:
            return 'F'
        case 6:
            return 'G'
        case 7:
            return 'H'
        case 8:
            return 'I'
        case 9:
            return 'J'


def convert_to_int(ch):
    lower_ch = ch.lower()
    match lower_ch:
        case 'a':
            return 0
        case 'b':
            return 1
        case 'c':
            return 2
        case 'd':
            return 3
        case 'e':
            return 4
        case 'f':
            return 5
        case 'g':
            return 6
        case 'h':
            return 7
        case 'i':
            return 8
        case 'j':
            return 9


class Game:
    def __init__(self, player_id):

        self.player_id = player_id

        self.player_stats = {
            'wins': 0,
            'loses': 0
        }

        count_of_cell = 10
        self.game = TicTacToeGame(count_of_cell)

        self.board = self.game.getInitBoard()

        self.player_turn_available = True

        # prepare AI player
        player_1_prepare = NNet(self.game)
        folder = os.getenv('CHECKPOINT_FOLDER')
        filename = os.getenv('CHECKPOINT_FILENAME')

        player_1_prepare.load_checkpoint(folder, filename)
        args1 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
        mcts1 = MCTS(self.game, player_1_prepare, args1)
        self.player_1 = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

    def __IsGameFinished(self):
        # getGameEnded returns 0 if game was not end
        canonical_index_of_real_player = 1  # it does not matter, we can get index_of_ai
        if self.game.getGameEnded(self.board, canonical_index_of_real_player) == 0:
            return False

        if self.game.getGameEnded(self.board, 1) == canonical_index_of_real_player:
            self.player_stats['wins'] += 1
        else:
            self.player_stats['loses'] += 1
        return True

    def __switchAiTurn(self):
        self.player_turn_available = not self.player_turn_available

    def aiAction(self):
        self.__switchAiTurn()

        # checking ai's move
        canonical_index_of_ai_player = -1
        while True:
            action = self.player_1(self.game.getCanonicalForm(
                self.board, canonical_index_of_ai_player))
            valid_moves = self.game.getValidMoves(self.game.getCanonicalForm(
                self.board, canonical_index_of_ai_player), 1)
            if valid_moves[action] != 0:
                break

            print(f'[WARN]: Action {action} is not valid!')
            print(f'valids = {valid_moves}')

        self.board, canonical_index_of_real_player = self.game.getNextState(
            self.board, canonical_index_of_ai_player, action)
        self.__switchAiTurn()

        return self.__IsGameFinished()

    def playerAction(self, action):
        canonical_index_of_real_player = 1
        self.board, canonical_index_of_ai_player = self.game.getNextState(
            self.board, canonical_index_of_real_player, action)

        return self.__IsGameFinished()

    # @return action
    def prepareInput(self, message):
        x = -1
        y = -1
        arr_input = message.split(' ')
        if arr_input[0].isdigit() and arr_input[1].isalpha():
            x = int(arr_input[0])
            y = convert_to_int(arr_input[1])
        elif arr_input[1].isdigit() and arr_input[0].isalpha():
            x = int(arr_input[1])
            y = convert_to_int(arr_input[0])
        if (x < 0 or x > 9) or (y < 0 or y > 9):
            return -1  # bad aciton, we should catch it!

        action = self.game.n * x + y if x != -1 else self.game.n ** 2
        valid_moves = self.game.getValidMoves(self.board, 1)
        if valid_moves[action] == 0:
            # todo: remove available turns !-!
            out = ""
            for i in range(len(valid_moves)):
                if valid_moves[i]:
                    out += str(int(i/self.game.n)) + " " + \
                        convert_to_ch(int(i % self.game.n)) + "\n"
            # remove this guy! !-!
            print(
                'Turn is invalid!\nAvailable turns:\n' + out)
            return -1
        return action

    def isPlayerTurnAvailable(self):
        return self.player_turn_available

    # @brief clean a board
    def cleanBoard(self):
        self.board = self.game.getInitBoard()

    # @brief get a board
    def getBoard(self):
        return self.game.display(self.board)

    # @brief send current stats of the player
    def getStats(self):
        return self.player_stats

    # @brief clean current stats of the player
    def refreshStats(self):
        self.player_stats['wins'] = 0
        self.player_stats['loses'] = 0


# keeps id of chats:
# { 'chat_id' : Game }
storage = {}

token = os.getenv('TOKEN')
bot = TicTacToeBot(token)

# @brief command to see bot usage
@bot.message_handler(commands=['help'])
def command_help(message):
    bot.send_message(message.chat.id,
                     "I'm Tic Tack Toe bot!"
                     "\nAvailable commands:"
                     "\n/start to start a game vs AI "
                     "\n/clean to clean a board"
                     "\n/board to see a current board"
                     "\n/stats to get win/lose statistics"
                     "\n/refresh_stats to refresh statistics")

# @brief command to see stats of the player
@bot.message_handler(commands=['stats'])
def command_stats(message):
    player_id = message.chat.id
    if storage.get(player_id) != None:
        player_stats = storage[player_id].getStats()
        bot.send_message(player_id, "Wins: " + str(player_stats['wins'])
                         + "\nLoses: " + str(player_stats['loses'])
                         )
    else:
        bot.send_message(player_id, "Sorry, but your stats is empty!"
                         )

# @brief command to clean board of the player
@bot.message_handler(commands=['clean'])
def command_clean(message):
    player_id = message.chat.id
    if storage.get(player_id) != None:
        storage[player_id].cleanBoard()
        bot.send_message(player_id, "Your board has been cleared.")

# @brief command to clean stats of the player
@bot.message_handler(commands=['refresh_stats'])
def command_refresh_stats(message):
    player_id = message.chat.id
    if storage.get(player_id) != None:
        storage[player_id].refreshStats()
        bot.send_message(player_id, "Your statistics has been refreshed.")

# @brief command to start a game
@bot.message_handler(commands=['start'])
def command_start(message):
    player_id = message.chat.id
    if storage.get(player_id) == None:
        bot.send_message(
            player_id, "Preparing your game with AI! Please, wait a second...")

        storage[player_id] = Game(player_id)

        player_board = storage[player_id].getBoard()
        bot.send_message(player_id, "Your game is ready!")
        bot.send_message(player_id, player_board)

    else:
        bot.send_message(player_id, "Your game was already exist!\n")
        bot.send_message(
            player_id, "Mark available cell.")
        player_board = storage[player_id].getBoard()
        bot.send_message(player_id, player_board)

# @brief command to send a current board for player ( user with with chat.id )
@bot.message_handler(commands=['board'])
def command_board(message):
    player_id = message.chat.id
    game = storage.get(player_id)
    if game != None:
        player_board = storage[player_id].getBoard()
        bot.send_message(player_id, player_board)
    else:
        bot.send_message(
            player_id, "At first use /start command to start a game! c:")

# @brief parse any input messages from a user
@bot.message_handler(func=lambda message: True)
def parse_income_message(message):
    player_id = message.chat.id
    game = storage.get(player_id)
    if game != None:
        if not game.isPlayerTurnAvailable():
            bot.send_message(
                player_id, "Man, please wait AI's turn and then resend your indexes of the cell.")
            return None

        action = game.prepareInput(message.text)
        if action == -1:
            bot.send_message(player_id, "Invalid turn!\n")
            return None

        is_game_finished = game.playerAction(action)

        bot.send_message(
            player_id, "Successfully marked your turn on the board:\n")
        player_board = storage[player_id].getBoard()
        bot.send_message(player_id, player_board)

        if is_game_finished:
            bot.send_message(player_id, "My congrats, you won!")
            game.cleanBoard()
            return None

        bot.send_message(player_id, "Now is AI's turn... Wait a second.\n")
        is_game_finished = game.aiAction()
        bot.send_message(player_id, "AI choosed cell on the board:\n")
        player_board = storage[player_id].getBoard()
        bot.send_message(player_id, player_board)

        if is_game_finished:
            bot.send_message(player_id, "Artificial intelligence beat you :)")
            game.cleanBoard()
        else:
            bot.send_message(player_id, "Now is your turn!")

    else:
        bot.send_message(
            player_id, "At first use /start command to start a game! c:")

bot.infinity_polling()
