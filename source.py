import socket
import struct
import string
import time
import sys
import sqlite3
import webbrowser
import surf

class SourceServer(object):
   """Base class for Valve Source engine game servers"""
   
   def __init__(self, sID, nick, addr, port):
      self._sID = sID
      self.nick = nick
      self.addr = addr
      self.port = port
      
      # Internal variables to determine status
      self._pinged = False
      self._online = bool()
      self._latency = int()
      
      # Variables from ping
      self._header = int()
      self._protocol = int()
      self._name = str()
      self._map = str()
      self._folder = str()
      self._game = str()
      self._gameID = int()
      self._players = int()
      self._max_players = int()
      self._bots = int()
      self._type = str()
      self._env = str()
      self._vis = bool()
      self._vac = bool()
   
   @classmethod
   def new(cls, nick, addr, port):
      return cls(surf.SurfDb.getNextServerID(), nick, addr, port)

   def get(self):
      """Look up server by ID"""
      
      conn = sqlite3.connect("surf.db")
      conn.isolation_level = None
      cur = conn.cursor()
      cur.execute("SELECT `name`, `address`, `port` FROM servers WHERE " \
                  "`id`=?", (self._sID,))
      
      row = cur.fetchone()
      
      if row == None:
         ret = False
      else:
         self.name = row[0]
         self.address = row[1]
         self.port = int(row[2])
         ret = True
      
      cur.close()
      conn.close()
      
      return ret
   
   def insert(self):
      """Insert server (auto ID)"""
      
      conn = sqlite3.connect("surf.db")
      conn.isolation_level = None
      cur = conn.cursor()
      cur.execute("INSERT INTO servers (`id`, `name`, `address`, `port`) " \
                  "VALUES (?, ?, ?, ?)", (self._sID, self.nick, self.addr,
                  self.port))
      
      cur.close()
      conn.close()
   
   def update(self):
      """Update server by ID"""
      
      conn = sqlite3.connect("surf.db")
      conn.isolation_level = None
      cur = conn.cursor()
      
      cur.execute("UPDATE servers SET `name`=?, `address`=?, `port`=? " \
                  "WHERE `id`=?", (self.nick, self.addr, self.port,
                  self._sID))
      
      cur.close()
      conn.close()
   
   def delete(self):
      """Delete server by ID"""
      
      conn = sqlite3.connect("surf.db")
      conn.isolation_level = None
      cur = conn.cursor()
      
      cur.execute("DELETE FROM servers WHERE `id`=?", (self._sID,))
      
      cur.close()
      conn.close()
   
   def _ping(self, timeout):
      request_packet = "\xff\xff\xff\xff\x54\x53\x6f\x75\x72\x63\x65\x20\x45" \
                       "\x6e\x67\x69\x6e\x65\x20\x51\x75\x65\x72\x79\x00"
      
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      sock.settimeout(timeout)
      sock.connect((self.addr, self.port))
      
      t1 = time.time()
      sock.sendall(request_packet)
      
      try:
         reply = sock.recv(4096)
         t2 = time.time()
         self._latency = int(round((t2 - t1) * 1000, 0))
      except socket.error as e:
         reply = None
      finally:
         sock.close()
      
      return reply
   
   def ping(self, timeout = 0.35, maxAttempts = 2):
      attempts = 0
      
      while attempts < maxAttempts:
         reply = self._ping(timeout)
         
         if not reply == None:
            break
         
         attempts += 1
      
      if reply == None:
         self._online = False
      else:
         self._online = True
         
         self._header = struct.unpack('B', reply[4])[0]
         self._protocol = int(struct.unpack('B', reply[5])[0])
         
         i = 6
         
         while reply[i] != '\x00':
            i += 1
         
         self._name = reply[6:i]
         i += 1
         j = i
         
         while reply[i] != '\x00':
            i += 1
         
         self._map = reply[j:i].lower()
         i += 1
         j = i
         
         while reply[i] != '\x00':
            i += 1
         
         self._folder = reply[j:i]
         i += 1
         j = i
         
         while reply[i] != '\x00':
            i += 1
         
         self._game = reply[j:i]
         i += 1
         self._gameID = struct.unpack('H', reply[i:i + 2])[0]
         i += 2
         self._players = int(struct.unpack('B', reply[i])[0])
         i += 1
         self._max_players = int(struct.unpack('B', reply[i])[0])
         i += 1
         self._bots = int(struct.unpack('B', reply[i])[0])
         i += 1
         self._type = reply[i]
         i += 1
         self._env = reply[i]
         i += 1
         self._vis = bool(struct.unpack('B', reply[i])[0])
         i += 1
         self._vac = bool(struct.unpack('B', reply[i])[0])
      
      self._pinged = True
   
   def join(self, pingInterval = 0.2):
      self.ping()
      
      if self._online and self._players >= self._max_players:
         sys.stdout.write("Server \"%s\" on \"%s\" is full (%d/%d)\nListening" \
                          " for free space" % (self.nick, self._map,
                          self._players, self._max_players))
         
         while self._online and self._players >= self._max_players:
            self.ping()
            sys.stdout.write(".")
            time.sleep(pingInterval)
         
         sys.stdout.write("\n")
         
         if self._online:
            print "Space now available; joining (%d/%d)" % (self._players,
                  self._max_players)
            webbrowser.open("steam://connect/%s:%d" % (self.addr, self.port))
         else:
            print "Server \"%s\" has gone offline" % (self.nick,)
      elif self._online:
         print "Joining server \"%s\" on \"%s\" (%d/%d)" % (self.nick,
               self._map, self._players, self._max_players)
         webbrowser.open("steam://connect/%s:%d" % (self.addr, self.port))
         # Consider FancyURLopener() if this doesn't work on some platform?
      else:
         print "Server \"%s\" is offline" % (self.nick,)
   
   @staticmethod
   def pingAll(servers):
      for server in servers:
         server.ping()
