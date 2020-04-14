import asyncio
import json
import random
import sys
import traceback
import websockets

from cah import CAH

with open('blacks.txt') as f:
    BLACKS = [line.strip() for line in f.readlines() if line.strip() and not line.strip()[0] == '#']
with open('whites.txt') as f:
    WHITES = [line.strip() for line in f.readlines() if line.strip() and not line.strip()[0] == '#']

GAME = CAH(BLACKS, WHITES)
USERS = {}
GAMEMASTERS = []

def state_event(playername):
    print(GAME.get_player_state(playername))
    return json.dumps({
        'type': 'state',
        'state': GAME.get_player_state(playername)
    })

def user_event(_):
    return json.dumps(
        {
            'type': 'user',
            'players': [{'name': player.name, 'score': player.score, 'cardczar': player.cardczar}
                        for player in GAME.players.values()]
        })

EVENTS = {
    'user': user_event,
    'state': state_event,
}

async def notify_users(msg_type):
    for name, socket in USERS.items():
        message = EVENTS[msg_type](name)
        await socket.send(message)

async def send_message(message):
    if USERS:
        msg = json.dumps({'type':'message', 'msg': message})
        await asyncio.wait([socket.send(msg) for socket in USERS.values()])

async def send_error(socket, message, error_type=''):
    await socket.send(json.dumps({'type': 'error', 'error': error_type, 'msg': message}))

async def add_user(websocket, name):
    if name in GAME.players:
        return None
    GAME.add_player(name)
    USERS[name] = websocket
    await notify_users("user")
    await send_message('%s joined the game!' % name)
    return name

async def remove_user(user):
    del GAME.players[user]
    del USERS[user]
    await notify_users('user')
    await send_message('%s left the game.' % user)

async def select_cards(user, data):
    owner = GAME.select_cards(user, data['cards'])
    await notify_users('state')
    await notify_users('user')
    await send_message('%s selected %s, point to %s' % (user, data['cards'], owner))

async def play_cards(user, data):
    GAME.play_cards(user, data['cards'])
    await notify_users('state')

async def start_game(user, data):
    GAME.start_game()
    await notify_users('state')
    await notify_users('user')
    await send_message('Game started by %s.' % user)

ACTIONS = {
    'select_cards': select_cards,
    'play_cards': play_cards,
    'start_game': start_game,
}

async def serve(websocket, path):
    try:
        user = None
        async for message in websocket:
            data = json.loads(message)
            if 'action' not in data or data['action'] != 'set_name':
                await send_error(websocket,
                                 'First message must be a set_name action!', 'no_set_name')
                await websocket.close()
                return
            user = await add_user(websocket, data['name'])
            if user:
                break
            await send_error(websocket, 'Name is already taken!', 'name_taken')

        await websocket.send(state_event(user))
        async for message in websocket:
            data = json.loads(message)
            if data['action'] in ACTIONS:
                try:
                    await ACTIONS[data['action']](user, data)
                except Exception as e:
                    await send_error(websocket, str(e))
                    traceback.print_exc()
            else:
                await send_error(websocket, '%s is not a valid action!' % data['action'],
                                 'invalid_action')

    # TODO: proper error handling?!
    finally:
        if user:
            await remove_user(user)

start_server = websockets.serve(serve, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
