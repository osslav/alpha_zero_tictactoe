import telebot

# todo !-!
import sys
sys.path.append('..')
from MCTS import MCTS
from .TicTacToeLogic import Board
from .TicTacToeGame import TicTacToeGame
from .TicTacToePlayers import *
from .keras.NNet import NNetWrapper as NNet

import numpy as np
from utils import *

import os
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

class TicTacToeBot(telebot.TeleBot):
    def __init__(self, token, parse_mode=None ) -> None:
        telebot.TeleBot.__init__( self, token, parse_mode )

token = os.getenv( 'TOKEN' )
bot = TicTacToeBot( token )

def convert_to_ch( int ):
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

def convert_to_int( ch ):
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

class InitOneGame:
    def __init__(self, bot, player_id):
        self.bot = bot
        self.player_id = player_id
        count_of_cell = 10
        self.game = TicTacToeGame(count_of_cell)
        self.board = self.game.getInitBoard()
        self.turn_available = True

        ### prepare AI player
        player_1_prepare = NNet(self.game)
        ## hardcode! >-< @todo: to .env ?
        player_1_prepare.load_checkpoint('./tictactoe/pretrained/','best.h5')
        args1 = dotdict({'numMCTSSims': 50, 'cpuct':1.0})
        mcts1 = MCTS(self.game, player_1_prepare, args1)
        self.player_1 = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

        self.sendMessage( "Your game is ready!" )
        self.sendBoard()

    def parseMessage( self, message ):
        # todo: We need better parser!
        arr_input = message.split( ' ' )
        y = convert_to_int( arr_input[1] )
        return int( arr_input[0] ), y

    def aiAction( self ):
        self.switchAiTurn()
        self.sendMessage("Now is AI's turn... Wait a second\n")

        # checking ai's move
        canonical_index_of_ai_player = -1
        while True:
            action = self.player_1(self.game.getCanonicalForm(self.board, canonical_index_of_ai_player))
            valid_moves = self.game.getValidMoves(self.game.getCanonicalForm(self.board, canonical_index_of_ai_player), 1)
            if valid_moves[ action ] != 0:
                break

            print(f'[WARN]: Action {action} is not valid!')
            print(f'valids = {valid_moves}')

        self.board, canonical_index_of_real_player = self.game.getNextState(self.board, canonical_index_of_ai_player, action)
        self.switchAiTurn()

        self.sendMessage( "AI choosed cell on the board:\n")
        self.sendBoard()

        if self.processIfGameWasFinished() != True:
            self.sendMessage("Now is your turn")


    def playerAction( self, message ):
        try:
            x, y = self.parseMessage( message )
            action = self.game.n * x + y if x!= -1 else self.game.n ** 2
            valid_moves = self.game.getValidMoves(self.board, 1)

            if valid_moves[action] == 0:
            # todo: remove available turns !-!
                out = ""
                for i in range ( len( valid_moves ) ):
                    if valid_moves[i]:
                        out += str ( int(i/self.game.n ) ) + " " +  convert_to_ch(  int(i%self.game.n) ) + "\n"
                self.sendMessage('Your turn is invalid!\nAvailable turns:\n' + out)
                return False

            canonical_index_of_real_player = 1
            self.board, canonical_index_of_ai_player = self.game.getNextState(self.board, canonical_index_of_real_player, action)
            self.sendMessage("Successfully marked your turn on the board:\n")
            self.sendBoard()
            if self.processIfGameWasFinished():
                return False
            return True
        except Exception as ex:
            print( ex )
            return False

    def processIfGameWasFinished(self):
        canonical_index_of_real_player = 1 # it does not matter
        if self.game.getGameEnded(self.board, canonical_index_of_real_player) != 0:
            out = "Game over!\n"
            if self.game.getGameEnded(self.board, 1) == canonical_index_of_real_player:
                out += "You won!"
            else:
                out += "AI won!"
            self.sendMessage( out)
            self.restartGame()
            return True
        return False

    # todo: private function, idk how to do it really !-!
    def switchAiTurn( self ):
        # todo: tern operator or some simple experession, I have no time to do it !-!
        if self.turn_available == True:
            self.turn_available = False
        else:
            self.turn_available = True

    def isTurnAvailable(self):
        return self.turn_available

    def restartGame(self ):
        self.board = self.game.getInitBoard()

    def sendMessage( self, message ):
            bot.send_message(self.player_id, message )

    def sendBoard(self):
        self.sendMessage( self.game.display( self.board ) )

# keeps id of chats:
# { 'chat_id' : InitOneGame }
storage = {}

@bot.message_handler(commands=['help'])
def command_help(message):
    bot.send_message(message.chat.id,
                     "I'm Tic Tack Toe bot!"
                     "\nAvailable commands:"
                     "\n/nickname to change your nickname (not impl)"
                     "\n/start to start a game vs AI "
                     "\n/restart to restart a game"
                     "\n/board to see a current board"
                     "\n/results to get win/lose statistics (not impl)")

@bot.message_handler( commands=['restart'])
def command_restart(message):
    player_id = message.chat.id
    if storage.get( player_id ) != None:
        storage[ player_id ].restartGame()
        bot.send_message(player_id, "Your board has beed cleared")
    else:
        bot.send_message( player_id, "At first you need to use /start command! c:")

@bot.message_handler(commands=['start'])
def command_start(message):
    player_id = message.chat.id
    if storage.get( player_id ) == None:
        bot.send_message(player_id, "Preparing your game with AI! Please, wait a second...")
        storage[player_id] = InitOneGame( bot, player_id )
    else:
        bot.send_message( player_id, "Your game is already exist!")
        storage[player_id].restartGame()
        bot.send_message(player_id, "Your board has beed cleared\nMark available cell")

# @brief send a current board to a player ( user with with chat.id )
@bot.message_handler( commands=['board'] )
def command_board(message):
    player_id = message.chat.id
    game = storage.get( player_id )
    if game != None:
        game.sendBoard()
    else:
        bot.send_message( player_id, "At first use /start command to start a game! c:")

# @brief parse any input messages from a user
@bot.message_handler(func=lambda message: True)
def parse_income_message(message):
    player_id = message.chat.id
    game = storage.get( player_id )
    if game != None:
        if game.isTurnAvailable():
            is_ai_choice = game.playerAction( message.text )
            if is_ai_choice == True:
                game.aiAction()
        else:
            bot.send_message( player_id, "Man, please wait AI's turn and then resend your indexes of cell")
    else:
        bot.send_message( player_id, "At first use /start command to start a game! c:")

bot.infinity_polling()
