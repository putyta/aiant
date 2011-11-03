#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ants import *
import sys
import traceback
import copy

log = None

OBSTACLE = 65536
GRASS = 0
UNEXPLORED = -1
MAP_RENDER = ' ' + ''.join(['+' for i in range(0, OBSTACLE-1)]) + '%' + '*'

class Maze:
  def __init__(self, rows, cols):
    """Инициализация карты rows x cols
        -1 - неисследовано
    """
    self.rows = rows
    self.cols = cols
    self.maze = [[UNEXPLORED for c in range(0, cols)] for r in range(0, rows)]
    self.unexplored = [(r,c) for c in range(0, cols) for r in range(0, rows)]

  def update(self, ants):
    """Обновление лабиринта
        используется ants (visible, map)
    """
    for loc in self.unexplored:
      if ants.visible(loc):
        r, c = loc
        if ants.map[r][c] == WATER:
          self.maze[r][c] = OBSTACLE
        else:
          self.maze[r][c] = GRASS
        self.unexplored.remove(loc)

  def renderTextMap(self):
    'return a pretty string representing the map'
    def f(x):
      if not x%10:
       return x/10%10
      else:
       return ' '
    tmp = '   %s\n' % ''.join([str(f(i)) for i in range(0,self.cols)])
    tmp += '   %s\n' % ''.join([str(i%10) for i in range(0, self.cols)])
    i = 0
    for row in self.maze:
      tmp += '%02d %s\n' % (i,''.join([MAP_RENDER[col] for col in row]))
      i += 1
    return tmp

  def getCopy(self):
    return copy.deepcopy(self.maze)

  @staticmethod
  def renderMaze(maze):
    'return a pretty string representing the maze'
    rows = len(maze)
    cols = len(maze[0])
    def f(x):
      if not x%10:
       return x/10%10
      else:
       return ' '
    tmp = '   %s\n' % ''.join([str(f(i)) for i in range(0, cols)])
    tmp += '   %s\n' % ''.join([str(i%10) for i in range(0, cols)])
    i = 0
    for row in maze:
      tmp += '%d %s\n' % (i,''.join([MAP_RENDER[col] for col in row]))
      i += 1
    return tmp


class PathFinder:
  def __init__(self, rows, cols):
    self.rows = rows
    self.cols = cols
  def getTrace(self, maze, start, target):
    getVal = lambda  point: maze[point[0]][point[1]]
    trace = [target]
    curPoint = target
    while True:
      r, c = curPoint
      for wavePoint in [((r+x+self.rows)%self.rows, (c+y+self.cols)%self.cols) for x,y in [(0,1), (0,-1), (1,0), (-1,0)]]:
        if getVal(wavePoint) == getVal(curPoint) - 1:
          curPoint = wavePoint
          trace.append(curPoint)
          break
      if getVal(curPoint) == 1:
        break
    trace.reverse()
    return trace
    
  def getDirTo(self, mazei, start, objects, maxrad):
    #food_loc = pf.getDirTo(self.maze, ant_loc, food_store, ants.viewradius2)
    maze = mazei.getCopy()
    nextPoints = [start]
    found = False
    wave = 1
    x, y = start
    maze[x][y] = wave
    try:
      while True:
        if wave >= maxrad:
          return start
        curPoints = nextPoints
        nextPoints = []
        wave += 1
        str = ''
        for point in curPoints:
          r, c = point
          waveFront = [((r+x+self.rows)%self.rows, (c+y+self.cols)%self.cols) for x,y in [(0,1), (0,-1), (1,0), (-1,0)]]
          for frontPoint in waveFront:
            if frontPoint in objects:
              log.write("FOUNT OBJECT: %d:%d\n" % frontPoint)
              return frontPoint
            x, y = frontPoint
            if maze[x][y] == GRASS:
              maze[x][y] = wave
              nextPoints.append(frontPoint)
        if len(nextPoints) == 0:
          return start
    except:
      global log
      traceback.print_exc(file=log)
      return start

  def getDirection(self, mazei, start, target):
    if start == target:
      return [start]
    maze = mazei.getCopy()
    nextPoints = [start]
    found = False
    wave = 1
    x, y = start
    maze[x][y] = wave
    step = 0
    lastPoint = start
    while not found:
      step += 1
      global log
      curPoints = nextPoints
      nextPoints = []
      wave += 1
      for point in curPoints:
        r, c = point
        waveFront = [((r+x+self.rows)%self.rows, (c+y+self.cols)%self.cols) for x,y in [(0,1), (0,-1), (1,0), (-1,0)]]
        for frontPoint in waveFront:
          lastPoint = frontPoint
          x, y = frontPoint
          if maze[x][y] in [GRASS, UNEXPLORED]: #== GRASS:
            maze[x][y] = wave
            if frontPoint == target:
              log.write(Maze.renderMaze(maze))
              log.write("FOUND!!! %d:%d, len: %d, points in front: %d\n" % (target+(wave, len(nextPoints))))
              found = True
              break
            nextPoints.append((x,y))
        if found:
          break
      if not found and len(nextPoints) == 0:
        log.write("UNABLE TO DESIDE %d:%d\n" % lastPoint)
        log.write(Maze.renderMaze(maze))
        return [lastPoint]
    try:
      trace = self.getTrace(maze, start, target)
      #self.saveMaze(maze, start, target, trace)
    except:
      global log
      traceback.print_exc(file=log)
    return trace

  def getClosestUnexplored(self, mazei, start):
    maze = mazei.getCopy()
    #log.write(mazei.renderTextMap())
    #log.flush()
    nextPoints = [start]
    found = False
    wave = 1
    x, y = start
    maze[x][y] = wave
    try:
      while True:
        curPoints = nextPoints
        nextPoints = []
        wave += 1
        for point in curPoints:
          r, c = point
          waveFront = [((r+x+self.rows)%self.rows, (c+y+self.cols)%self.cols) for x,y in [(0,1), (0,-1), (1,0), (-1,0)]]
          for frontPoint in waveFront:
            x, y = frontPoint
            if maze[x][y] == UNEXPLORED:
              log.write("%d:%d -> %d:%d\n" % (start + frontPoint))
              return frontPoint
            if maze[x][y] == GRASS:
              maze[x][y] = wave
              nextPoints.append(frontPoint)
        if len(nextPoints) == 0:
          log.write("EVERYTHING HAS BEEN EXPLORED\n")
          return start
    except:
      global log
      traceback.print_exc(file=log)
      return start

  def _getClosestUnexplored(self, mazei, start):
    """ Возвращает ближайшую неисследованную точку
    """
    maze = list(mazei)
    x, y = start
    DONE = 99
    nextPoints = [start]
    try:
      while True:
        curPoints = nextPoints
        nextPoints = []
        for point in curPoints:
          r, c = point
          if(maze[r][c] == UNEXPLORED):
            return (r,c)
          waveFront = [((r+x+self.rows)%self.rows, (c+y+self.cols)%self.cols) for x,y in [(0,1), (0,-1), (1,0), (-1,0)]]
          for frontPoint in waveFront:
            if frontPoint == start:
              return start
            r, c = frontPoint
            if maze[r][c] == UNEXPLORED:
              return frontPoint
            nextPoints.append(frontPoint)
    except:
      global log
      traceback.print_exc(file=log)
      return start

  def saveMaze(self, maze, start, target, trace = None):
    f = open("maze.dat", "w+")
    f.write("START:  %d, %d\n" % start)
    f.write("FINISH: %d, %d\n" % target)
    f.write("r: %d\nc: %d\n" % (self.rows, self.cols))
    if trace is not None:
      for point in trace:
        f.write("(%d,%d)->" % point)
      f.write("\n")
    f.write("\t")
    for col in range(0, self.cols):
      f.write("%d\t" % col)
    f.write("\n")
    for row in range(0, self.rows):
      f.write("%d\t" % row)
      for col in range(0, self.cols):
        f.write(str(maze[row][col]) + "\t")
      f.write("\n")
    f.flush()
    f.close()

class MyBot:
    def __init__(self):
        self.log = open("LOG.LOG", "w+")
        global log 
        log = self.log
        self.turnCount = 0
        pass
    
    def do_setup(self, ants):
        self.hills = []
        self.maze = Maze(ants.rows, ants.cols)
        pass
    
    def do_turn(self, ants):
        self.turnCount += 1
        # обновление карты
        self.maze.update(ants)

        self.log.write("NEXT TURN----------- %d, %d\n" % (len(ants.my_ants()), self.turnCount))
        self.log.flush()
        pf = PathFinder(self.maze.rows, self.maze.cols)

        #self.log.write("unexplored: %d\n" % len(self.maze.unexplored))
        #self.log.write(self.maze.renderTextMap())
        #self.log.flush()
#        self.unseen = []
#        for row in range(ants.rows):
#            for col in range(ants.cols):
#                self.unseen.append((row, col))

        targets = {}
        def do_move_location(loc, dest):
            trace = pf.getDirection(self.maze, loc, dest)
            if( len(trace) > 1):
              log.write("DIR: %d:%d -> %d:%d\n" % (loc + trace[1]))
              directions = ants.direction(loc, trace[1])
            else:
              directions = ants.direction(loc, dest)
            for direction in directions:
                if do_move_direction(loc, direction):
                    targets[dest] = loc
                    return True
            return False
        try:
          orders = {}
          def do_move_direction(loc, direction):
              new_loc = ants.destination(loc, direction)
              log.write("ORDER: %d:%d -> %d:%d\n" % (loc + new_loc))
              ants.issue_order((loc, direction))
              orders[new_loc] = loc
              return True
#???????????????????????????????????
              if True:
                #if (ants.unoccupied(new_loc) and new_loc not in orders):
                if new_loc not in orders:
                  #log.write("ORDER: %d:%d -> %d:%d\n" % (loc + new_loc))
                  ants.issue_order((loc, direction))
                  orders[new_loc] = loc
                  return True
                else:
                  #log.write("OCCUPIED: %d:%d\n" % new_loc)
                  return False

          # prevent stepping on own hill
          for hill_loc in ants.my_hills():
            orders[hill_loc] = None

          lastExplorer = 0 #min(5, len(ants.my_ants())/10+1)
          explorers = ants.my_ants()[:lastExplorer]
          harvesters = ants.my_ants()[lastExplorer:]
          if len(self.maze.unexplored) > 0:
            for explorer in explorers:
              unexpLand = pf.getClosestUnexplored(self.maze, explorer)
              log.write("EXPLORE: %s:%s\n" % (str(explorer),str(unexpLand)))
              #log.write(self.maze.renderTextMap())
              do_move_location(explorer, unexpLand)

          # find close food
          if False:
            ant_dist = []
            for ant_loc in harvesters:
              for food_loc in ants.food():
                  #if ants.distance(ant_loc, food_loc) > 5:
                  #  continue
                  trace = pf.getDirection(self.maze, ant_loc, food_loc)
                  if(len(trace) > 1):
                    dist = len(trace) #ants.distance(ant_loc, food_loc)
                  else:
                    dist = ants.distance(ant_loc, food_loc)
                  ant_dist.append((dist, ant_loc, food_loc))
            ant_dist.sort()
            for dist, ant_loc, food_loc in ant_dist:
                if food_loc not in targets and ant_loc not in targets.values():
                  do_move_location(ant_loc, food_loc)
          #version #2
          if True:
#            food -> []
#            for each ant:
#              is there any food in raidius viewradius2 from me?:
#                yes -> go thete and remove this piece of food from food
#                no -> go exploring
            
            food_store = ants.food()[:]
            for ant_loc in harvesters:
              food_loc = pf.getDirTo(self.maze, ant_loc, food_store, ants.viewradius2)
              if food_loc <> ant_loc:
                do_move_location(ant_loc, food_loc)
                food_store.remove(food_loc)
              else:
                unexpLand = pf.getClosestUnexplored(self.maze, ant_loc)
                do_move_location(ant_loc, unexpLand)


          # unblock own hill
          for hill_loc in ants.my_hills():
              if hill_loc in ants.my_ants() and hill_loc not in orders.values():
                  for direction in ('s','e','w','n'):
                      if do_move_direction(hill_loc, direction):
                          break

          # attack hills
#          for hill_loc, hill_owner in ants.enemy_hills():
#              if hill_loc not in self.hills:
#                  self.hills.append(hill_loc)        
#          ant_dist = []
#          for hill_loc in self.hills:
#              for ant_loc in ants.my_ants():
#                  if ant_loc not in orders.values():
#                      dist = ants.distance(ant_loc, hill_loc)
#                      ant_dist.append((dist, ant_loc))
#          ant_dist.sort()
#          for dist, ant_loc in ant_dist:
#              do_move_location(ant_loc, hill_loc)





        except:
          #self.log.write("EXCEPTION: %s\n" % sys.exc_info()[1])
          traceback.print_exc(file=self.log)


if __name__ == '__main__':
    # psyco will speed up python a little, but is not needed
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(MyBot())
        #Ants.run(AvoidingCollisions())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
