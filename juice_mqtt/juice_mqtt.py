#!/usr/bin/env python3
from functools import partial
import paho.mqtt.client as mqtt
import json
import juice
import juice.message.format as msg_format

last_status = {}


def onMQTTMsg(client,userdate,msg):
  print('MQTTMsg: ####' )
  payload = msg.payload.decode("utf-8")
  topic = msg.topic.split('/')
  print(topic, payload)
  server = juice.connect('euterpe3', 9090)
  players = juice.get_players(server)
  for player in players:
    print(player)
    if player['name'] == topic[-1]:
      juice.pause(server, player['id'])
      break;
  server.close()

def onSBMsg(msg):
  print('SBMsg: ####' )
  print(msg)
  player = msg['player']
  try:
    track = player['playlist'][player['playlist_cur_index']]
  except KeyError:
    track = {}
  status = {
      'id': player['id'],
      'name': player['name'],
      'mode': player['mode'],
      'track': track.get('title', None),
      'album': track.get('album', None),
      'album_id': track.get('album_id', None),
      'artist': track.get('artist', None),
      'artist_id': track.get('artist_id', None),
      'title': player.get('current_title', None), 
      'volume': player['volume'],
      'playlist': player['playlist'],
      'playlist_cur_index': player.get('playlist_cur_index', None)
  }
  last_status[player['name']] = status
  client.publish('squeezebox/players/' + player['name'],
    json.dumps(status), retain=True, qos=1)
  client.publish('squeezebox/display/' + player['name'], 
    '{}\t{}\t{}'.format(track.get('title','---'),
                        track.get('artist','---'),
                        track.get('album','---')).encode('ascii','ignore'),
    retain=True, qos=1)

if __name__ == '__main__':
  client = mqtt.Client('juice-bridge')
  client.connect('euterpe3')
  client.on_message = onMQTTMsg
  #client.on_log = lambda client,ussrdata,level,buf: print("log:",level,buf)
  client.loop_start()
  client.subscribe("squeezebox/command/#")
  server = juice.connect('euterpe3', 9090)
  players = juice.get_players(server)
  for player in players:
    server.write(msg_format.player_status(player['id'], subscribe=0, start=0, page_size=9999).encode('ascii'))
  juice.loop_start(server, onSBMsg)
