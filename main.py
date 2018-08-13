"""
	Small test game implemented using Pyxel lib
	The game is a copy of Tron

"""


from random import randint
from enum import Enum
from collections import deque
import pyxel


##################
#   Constants    #
##################

MOTO_LENGTH = 3
MOTO_WIDTH = 2
MOTO_SPEED = 1.5
GRID_SIZE = 1
GRID_HEIGHT = 150
GRID_WIDTH = 150

##################
#     Enums      #
##################

class Orientation(Enum):
	VERTICAL = 1
	HORIZONTAL = 2

class Direction(Enum):
	UP = 1
	RIGHT = 2
	DOWN = 3
	LEFT = 4


##################
#      Code      #
##################



class Line:
	def __init__(self, x1, y1, color, isVertical):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x1
		self.y2 = y1
		self.color = color

		if isVertical:
			self.orientation = Orientation.VERTICAL
		else:
			self.orientation = Orientation.HORIZONTAL

	def setPoint2(self, x2, y2):
		self.x2 = x2
		self.y2 = y2

	def draw(self):
		pyxel.line(self.x1, self.y1, self.x2, self.y2, self.color)

	def isVertical(self):
		return self.orientation == Orientation.VERTICAL

	def	isHorizontal(self):
		return self.orientation == Orientation.HORIZONTAL

	def intersectX(self, x):
		return (x >= self.x1 and x <= self.x2) or (x >= self.x2 and x <= self.x1)

	def intersectY(self, y):
		return (y >= self.y1 and y <= self.y2) or (y >= self.y2 and y <= self.y1)

	def debug(self):
		print('x1:', self.x1)
		print('y1:', self.y1)
		print('x2:', self.x2)
		print('y2:', self.y2)
		print('orientation:', self.orientation)

	@staticmethod
	def orientationFromDirection(direction):
		if direction == Direction.UP or direction == Direction.DOWN:
			return Orientation.VERTICAL
		return Orientation.HORIZONTAL

class Player:
	def __init__(self, playerId, score, x, y, direction, keyMap, color):
		self.id = playerId
		self.score = score
		self.x = x
		self.y = y
		self.direction = direction
		self.orientation = Line.orientationFromDirection(direction)
		self.keyMap = keyMap
		self.color = color
		self.lastTurningPoint = [self.x, self.y]

		startLine = Line(x, y, self.color, self.direction == Direction.UP or self.direction == Direction.DOWN)
		self.history = [startLine] # may not work / List of points marking direction changes
		
		self.alive = True
		self.won = False
		self.changedDirection = False;


	def draw(self):
		for line in self.history:
			line.draw()

		if self.alive:
			if self.direction == Direction.UP:
				pyxel.rect(self.x - MOTO_WIDTH/2, self.y, self.x + MOTO_WIDTH/2, self.y - MOTO_LENGTH, self.color)
			elif self.direction == Direction.DOWN:
				pyxel.rect(self.x - MOTO_WIDTH/2, self.y, self.x + MOTO_WIDTH/2, self.y + MOTO_LENGTH, self.color)
			elif self.direction == Direction.LEFT:
				pyxel.rect(self.x - MOTO_LENGTH, self.y - MOTO_WIDTH/2, self.x, self.y + MOTO_WIDTH/2, self.color)
			elif self.direction == Direction.RIGHT:
				pyxel.rect(self.x + MOTO_LENGTH, self.y - MOTO_WIDTH/2, self.x, self.y + MOTO_WIDTH/2, self.color)



	def update(self):
		if self.alive:
			self.checkDirectionChange()
			self.updateHistory()
			self.updatePosition()

	def checkDirectionChange(self):
		self.changedDirection = False

		if pyxel.btnp(self.keyMap['UP']):
			if not (self.direction == Direction.UP or self.direction == Direction.DOWN) and not self.changedDirection:
				self.direction = Direction.UP
				self.orientation = Orientation.VERTICAL
				self.changedDirection = True
		if pyxel.btnp(self.keyMap['DOWN']):
			if not (self.direction == Direction.UP or self.direction == Direction.DOWN) and not self.changedDirection:
				self.direction = Direction.DOWN
				self.orientation = Orientation.VERTICAL
				self.changedDirection = True
		if pyxel.btnp(self.keyMap['LEFT']):
			if not (self.direction == Direction.LEFT or self.direction == Direction.RIGHT) and not self.changedDirection:
				self.direction = Direction.LEFT
				self.orientation = Orientation.HORIZONTAL
				self.changedDirection = True
		if pyxel.btnp(self.keyMap['RIGHT']):
			if not (self.direction == Direction.LEFT or self.direction == Direction.RIGHT) and not self.changedDirection:
				self.direction = Direction.RIGHT
				self.orientation = Orientation.HORIZONTAL
				self.changedDirection = True

		if self.changedDirection:
			self.orientation = Line.orientationFromDirection(self.direction)
			self.lastTurningPoint = [self.x, self.y]
		# if direction changed -> we don't remove last point as it's a turning point
		
	def updatePosition(self):
		if self.direction == Direction.UP:
			self.y -= MOTO_SPEED * GRID_SIZE
		if self.direction == Direction.DOWN:
			self.y += MOTO_SPEED * GRID_SIZE
		if self.direction == Direction.LEFT:
			self.x -= MOTO_SPEED * GRID_SIZE
		if self.direction == Direction.RIGHT:
			self.x += MOTO_SPEED * GRID_SIZE

	def updateHistory(self):
		self.history[-1].setPoint2(self.x, self.y)
		if self.changedDirection:
			self.history.append(Line(self.x, self.y, self.color, self.direction == Direction.UP or self.direction == Direction.DOWN))

	def getTrajectoryChange(self):
		if self.changedDirection:
			return self.history[-2:]
		return self.history[-1:]

	def gotCollisionNew(self, grid):
		if self.x <= 0 or self.y <= 0 or self.x == GRID_SIZE * GRID_WIDTH or self.y == GRID_SIZE * GRID_HEIGHT:
			return True # Collision with sides of the grid

		for line in list(filter(lambda l: l.x1 == self.x, grid[0])): # Vertical lines with same x
			if line.orientation != self.orientation and line.intersectY(self.y) and line.y2 != self.lastTurningPoint[1]: # TODO: Check if lastTurningPoint != l.2
				return True
			else:
				if line.intersectY(self.y) and self.lastTurningPoint[1] != line.y1 and self.lastTurningPoint[1] != line.y2:
					return True

		for line in list(filter(lambda l: l.y1 == self.y, grid[1])): # Horizontal lines with same y
			if line.orientation != self.orientation and line.intersectX(self.x) and line.x2 != self.lastTurningPoint[0]:
				return True
			else:
				if line.intersectX(self.x) and self.lastTurningPoint[0] != line.x1 and self.lastTurningPoint[0] != line.x2:
					return True

		return False

	def win(self):
		if not self.won:
			self.won = True
			self.score += 1

	def die(self):
		print("Player " + str(self.id) + " dies")
		self.alive = False



class App:
	def __init__(self):
		print("Init...")
		pyxel.init(GRID_WIDTH*GRID_SIZE, GRID_HEIGHT*GRID_SIZE, caption="PyxelTestGame")
		self.resetPlayers(0, 0)

		pyxel.run(self.update, self.draw)

	def update(self):
		if pyxel.btnp(pyxel.KEY_R):
			score1 = 0
			score2 = 0
			for player in self.playersAlive + self.playersDead:
				if player.id == 1:
					score1 = player.score
				else:
					score2 = player.score
			self.resetPlayers(score1, score2)

		if len(self.playersAlive) < 2:
			return

		for index, player in enumerate(self.playersAlive):
			player.update()
			self.updateGrid(player.getTrajectoryChange())
		# self.printGrid()
		# input()

		for player in self.playersAlive: # I want to update all positions before checking collisions
			if player.gotCollisionNew(self.trajectories):
				player.die()
				self.playersDead.append(player)
				self.playersAlive.remove(player)



	def draw(self):
		pyxel.cls(0)

		if len(self.playersAlive) == 0:
			pyxel.text(GRID_SIZE*GRID_WIDTH/2 - 25, GRID_SIZE*GRID_HEIGHT/2 - 10, 'Draw', pyxel.frame_count % 16)
		elif len(self.playersAlive) == 1:
			pyxel.text(GRID_SIZE*GRID_WIDTH/2 - 25, GRID_SIZE*GRID_HEIGHT/2 - 10, 'Player ' + str(self.playersAlive[0].id) + ' wins!', pyxel.frame_count % 16)
			self.playersAlive[0].win()
		else:
			for player in self.playersAlive + self.playersDead:
				player.draw()
		

		for i, player in enumerate(sorted(self.playersAlive + self.playersDead, key=lambda p: p.score)):
			pyxel.text(0, i*6, "Player " + str(player.id)+ ":" + str(player.score), player.color)

	def resetPlayers(self, score1, score2):
		print("Creating Players")

		keyMap1 = {
			'UP': pyxel.KEY_W,
			'LEFT': pyxel.KEY_A,
			'DOWN': pyxel.KEY_S,
			'RIGHT': pyxel.KEY_D
		}
		keyMap2 = {
			'UP': pyxel.KEY_UP,
			'LEFT': pyxel.KEY_LEFT,
			'DOWN': pyxel.KEY_DOWN,
			'RIGHT': pyxel.KEY_RIGHT
		}

		player1 = Player(1, score1, GRID_WIDTH * GRID_SIZE / 2, GRID_SIZE * GRID_HEIGHT, Direction.UP, keyMap1, 12)
		player2 = Player(2, score2, GRID_WIDTH * GRID_SIZE / 2, 0, Direction.DOWN, keyMap2, 9)

		self.playersAlive = [player1, player2]
		self.playersDead = []
		self.trajectories = [[], []] # 0 -> Vertical, 1 -> Horizontal 


	def updateGrid(self, trajectoryDelta):
		if trajectoryDelta[0].isVertical() and len(self.trajectories[0]) > 0:
			if self.trajectories[0][-1].x1 == trajectoryDelta[0].x1 and self.trajectories[0][-1].y1 == trajectoryDelta[0].y1:
				self.trajectories[0].pop()
		if trajectoryDelta[0].isHorizontal() and len(self.trajectories[1]) > 0:
			if self.trajectories[1][-1].x1 == trajectoryDelta[0].x1 and self.trajectories[1][-1].y1 == trajectoryDelta[0].y1:
				self.trajectories[1].pop()

		self.trajectories[0].extend(filter(lambda l: l.isVertical(), trajectoryDelta))
		self.trajectories[1].extend(filter(lambda l: l.isHorizontal(), trajectoryDelta))


	def printGrid(self):
		print("Grid")
		print("Vertical lines: ")
		for line in self.trajectories[0]:
			line.debug()
		print("Horizontal lines: ")
		for line in self.trajectories[1]:
			line.debug()
App()

