#!/usr/bin/env python3
from functools import partial
import paho.mqtt.client as mqtt
import json
import juice
import juice.message.format as msg_format

last_status = {}

def get_players(msg):
  for name in last_status.keys():
    client.publish('squeezebox/players/' + name, json.dumps(last_status[name]))

actions = {
  'players': {'get': get_players}
}

player_commands = {
  'play': juice.play,
  'pause': juice.pause,
  'volume_dec': partial(juice.set_player_volume, vol='-2'),
  'volume_inc': partial(juice.set_player_volume, vol='+2'),
  'track_next': juice.next_track,
  'track_previous': juice.previous_track,
}

def onMQTTMsg(client,userdate,msg):
  payload = msg.payload.decode("utf-8")
  topic = msg.topic.split('/')
  if('command' == topic[-1]):
    player_id = topic[-2]
    server = juice.connect('euterpe3', 9090)
    player_commands[payload](server, player_id)
  else:
    [noun,verb] = topic[-1].split('-')
    actions[noun][verb](msg)

def onSBMsg(msg):
  print('SBMsg: ####' )
  print(msg)
  player = msg['player']
  track = player['playlist'][player['playlist_cur_index']]
  status = {
      'id': player['id'],
      'name': player['name'],
      'mode': player['mode'],
      'track': track['title'],
      'album': track.get('album', None),
      'artist': track.get('artist', None),
      'title': player.get('current_title', None), 
      'volume': player['volume'],
      'playlist': player['playlist'],
      'playlist_current_index': player['playlist_cur_index'],
  }
  last_status[player['name']] = status
  client.publish('squeezebox/players/' + player['name'],
    json.dumps(status))

if __name__ == '__main__':
  client = mqtt.Client('juice-bridge')
  client.connect('euterpe3')
  client.on_message = onMQTTMsg
  #client.on_log = lambda client,ussrdata,level,buf: print("log:",level,buf)
  client.loop_start()
  client.subscribe("squeezebox/players-get")
  client.subscribe("squeezebox/players/+/command")
  server = juice.connect('euterpe3', 9090)
  players = juice.get_players(server)
  for player in players:
    server.write(msg_format.player_status(player['id'], subscribe=0, start=0, page_size=9999).encode('ascii'))
  juice.loop_start(server, onSBMsg)
