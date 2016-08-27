import sys
import time
import sqlite3
from source import SourceServer

class SurfMap(object):
   """Class for Valve GoldSrc/Source surf maps"""
   
   def __init__(self, name, tier = -1, rating = -1, stages = -1, bonus = -1,
                complete = False, favourite = False):
      self._name = name.lower()
      self.tier = tier
      self.rating = rating
      self.stages = stages
      self.bonus = bonus
      self.complete = bool(complete)
      self.favourite = bool(favourite)
   
   def get(self):
      """Look up map by name"""
      
      conn = sqlite3.connect("surf.db")
      conn.isolation_level = None
      cur = conn.cursor()
      cur.execute("SELECT `tier`, `rating`, `stages`, `bonus`, " \
                  "`complete`, `favourite` FROM maps WHERE `name`=?",
                  (self._name,))
      
      row = cur.fetchone()
      
      if row == None:
         ret = False
      else:
         self.tier = int(row[0])
         self.rating = int(row[1])
         self.stages = int(row[2])
         self.bonus = int(row[3])
         self.complete = bool(row[4])
         self.favourite = bool(row[5])
         ret = True
      
      cur.close()
      conn.close()
      
      return ret
   
   def insert(self):
      """Insert map by name"""
      
      conn = sqlite3.connect("surf.db")
      conn.isolation_level = None
      cur = conn.cursor()
      cur.execute("INSERT INTO maps (`name`, `tier`, `rating`, `stages`, " \
                  "`bonus`, `complete`, `favourite`) VALUES " \
                  "(?, ?, ?, ?, ?, ?, ?)", (self._name, self.tier,
                  self.rating, self.stages, self.bonus, self.complete,
                  self.favourite))
      
      cur.close()
      conn.close()
   
   def update(self):
      """Update map by name"""
      
      conn = sqlite3.connect("surf.db")
      conn.isolation_level = None
      cur = conn.cursor()
      
      cur.execute("UPDATE maps SET `tier`=?, `rating`=?, `stages`=?, " \
                  "`bonus`=?, `complete`=?, `favourite`=? WHERE `name`=?",
                  (self.tier, self.rating, self.stages, self.bonus,
                  self.complete, self.favourite, self._name))
      
      cur.close()
      conn.close()
   
   def delete(self, confirm = True):
      """Delete map by name"""
      
      conn = sqlite3.connect("surf.db")
      conn.isolation_level = None
      cur = conn.cursor()
      
      if confirm:
         sys.stdout.write("Are you sure you want to delete map \"%s\" (y/n)? "
                          % (self._name,))
         
         if sys.stdin.read(1).lower() == 'y':
            cur.execute("DELETE FROM maps WHERE `name`=?", (self._name,))
            print "Map \"%s\" deleted" % (self._name,)
         else:
            print "Delete aborted"
      else:
         cur.execute("DELETE FROM maps WHERE `name`=?", (self._name,))
      
      cur.close()
      conn.close()

class SurfDb(object):
   """Static database class for surf servers and maps"""
   
   lastServers = None
   
   @staticmethod
   def join(sID):
      if SurfDb.lastServers == None:
         SurfDb.lastServers = SurfDb.getServers()
      
      SurfDb.lastServers[sID].join()
   
   @staticmethod
   def getServers():
      conn = sqlite3.connect("surf.db")
      conn.isolation_level = None
      cur = conn.cursor()
      cur.execute("SELECT `id`, `name`, `address`, `port` FROM servers")
      
      ret = list()
      
      for row in cur:
         ret.append(SourceServer(row[0], row[1], row[2], row[3]))
      
      cur.close()
      conn.close()
      
      SurfDb.lastServers = ret
      return ret
   
   @staticmethod
   def getMaps():
      conn = sqlite3.connect("surf.db")
      conn.isolation_level = None
      cur = conn.cursor()
      cur.execute("SELECT `name`, `tier`, `rating`, `stages`, `bonus`, " \
                  "`complete`, `favourite` FROM maps")
      
      ret = list()
      
      for row in cur:
         ret.append(SurfMap(row[0], row[1], row[2], row[3], row[4], row[5],
                    row[6]))
      
      cur.close()
      conn.close()
      
      return ret
   
   @staticmethod
   def prettyPrint():
      maps = SurfDb.getMaps()
      servers = SurfDb.getServers()
      SourceServer.pingAll(servers)
      
      first = True
      maxIDLen = 0
      maxNickLen = 0
      maxMapLen = 10
      
      for i, server in enumerate(servers):
         nickLen = len(server.nick)
         
         if nickLen > maxNickLen:
            maxNickLen = nickLen
         
         idLen = len(str(i))
         
         if idLen > maxIDLen:
            maxIDLen = idLen
         
         if server._online:
            mapLen = len(server._map)
            
            if mapLen > maxMapLen:
               maxMapLen = mapLen
      
      print "=" * (maxNickLen + 7 + maxMapLen + 7) \
            + "=============================================="
      print " ID | Server" + " " * (maxNickLen + 1) + "| Game | Map" + " " * \
            (maxMapLen + 4) + "| Tier | Rating | Comp  | Ping"
      
      for i, server in enumerate(servers):
         if first:
            print "====|" + "=" * (maxNickLen + 8) + "|======|" + "=" \
                  * (maxMapLen + 8) + "|======|========|=======|======"
            first = False
         else:
            print "----|" + "-" * (maxNickLen + 8) + "|------|" + "-" \
                  * (maxMapLen + 8) + "|------|--------|-------|------"
      
         if server._online:
            # Find map the server is on!!
         
            thisMap = None
         
            for map_ in maps:
               if map_._name == server._map:
                  thisMap = map_
                  break
         
            if thisMap == None:
               outStr = "{:>3d} | {:<" + str(maxNickLen) + "s} {:>2d}/{:<2d} " \
                        "| {:>4d} | {:<" + str(maxMapLen) + "s}  -/-  |    - " \
                        "|      - |   -   | {:>4}"
            
               print outStr.format(i, server.nick, server._players,
                                   server._max_players, server._gameID,
                                   server._map, server._latency)
            else:
               outStr = "{:>3d} | {:<" + str(maxNickLen) + "s} {:>2d}/{:<2d} " \
                        "| {:>4d} | {:<" + str(maxMapLen) + "s} {:>2d}/{:<2d}" \
                        " | {:>4d} | {:>6d} | {:<5s} | {:>4}"
            
               print outStr.format(i, server.nick, server._players,
                                   server._max_players, server._gameID,
                                   server._map, thisMap.stages, thisMap.bonus,
                                   thisMap.tier, thisMap.rating,
                                   str(thisMap.complete), server._latency)
         else:
            outStr = "{:>3d} | {:<" + str(maxNickLen + 6) + "s} |      | {:<" \
                  + str(maxMapLen + 6) + "s} |      |        |       |"
         
            print outStr.format(i, server.nick, "(offline!)")
   
      print "=" * (maxNickLen + 7 + maxMapLen + 7) \
            + "=============================================="
   
   @staticmethod
   def pp():
      SurfDb.prettyPrint()
   
   @staticmethod
   def monitor(delay = 180):
      while True:
         SurfDb.prettyPrint()
         time.sleep(delay)
   
   @staticmethod
   def mon(delay = 180):
      SurfDb.monitor()
   
   @staticmethod
   def getNextServerID():
      """Get next free server ID"""
      
      conn = sqlite3.connect("surf.db")
      conn.isolation_level = None
      cur = conn.cursor()
      cur.execute("SELECT MAX(`id`) + 1 FROM servers")
      
      row = cur.fetchone()
      
      if row == None:
         print "Couldn't get next free ID!"
         ret = -1
      else:
         ret = int(row[0])
      
      cur.close()
      conn.close()
      
      return ret
   
   @staticmethod
   def getServer(sID):
      SurfDb.lastServers = SurfDb.getServers()
      return SurfDb.lastServers[sID]
   
   @staticmethod
   def getMap(name):
      m = SurfMap(name)
      
      if not m.get():
         print "Map not found; returning defaults"
      
      return m