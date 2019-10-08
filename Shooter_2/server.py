# iput = input
from map import *
from os import path
from objs import *
from pyglet.sprite import Sprite
from pyglet.window import key
from hud import *
from weapons import *
import _thread, socket, site, os, sys, platform

HOST = '192.168.1.188'   # Standard loopback interface address (localhost)
PORT = 65432

conns = {}
connsUDP = {}
TCPaddress = {}

players = {}
bullets = {}
grenades = {}

t_players = []
ct_players = []

id = 1

def command_log(*args):
    with open("./res/log.txt", "r") as r:
        print(r.read())

def command_conns(*args):
    for id in players:
        if args:
            if str(id) in args:
                print("Connection with: \n id: ", id, "\n TCP address: ",
                      TCPaddress[id], "\n UDP address: ", connsUDP[id])

        else:
            print("Connection with: \n id: ", id, "\n TCP address: ",
              TCPaddress[id], "\n UDP address: ", connsUDP[id])

def command_disconnect(*args):
    for id in args:
        pass

commands = {"log": command_log, "conns": command_conns}

def remove_user(id):
    if id in connsUDP:
        del connsUDP[id]
    if id in conns:
        del conns[id]
    if id in players:
        del players[id]
    if id in bullets:
        del bullets[id]
    if id in grenades:
        del grenades[id]
    if id in TCPaddress:
        del TCPaddress[id]

    if id in t_players:
        t_players.remove(id)
    elif id in ct_players:
        ct_players.remove(id)

    # ui.remove_user()

def console():
    with open("./res/log.txt", "w") as r:
        r.write("Server Started! \n")
        r.write("")

    while True:
        c = input(">> ")

        command = c.split(" ")
        expressions = command[1:]

        if command[0] in commands:
            commands[command[0]](*expressions)

        else:
            try:
                exec(c)

            except (NameError, SyntaxError) as e:
                print(e)

def log(text):
    with open("./res/log.txt", "a") as r:
        r.write(str(text))
        r.write("\n")
        r.write("\n")

def new_client(conn, addr, id):
    conn.sendall(str(id).encode())
    conn.sendall(str(MAP).encode())

    while True:
        try:
            data = conn.recv(1024).decode()

        except:
            log("Connection ended with: \n id: " + str(id) + "\n TCP address: " + str(addr) + "\n UDP address: " + str(connsUDP[id]))
            remove_user(id)
            break

        if data == "get map":
            with open("./res/maps/" + MAP, "rb") as r:
                m = r.read()

            conn.sendall(m)

        if (data == ""):
            try:
                log("Connection ended with: \n id: " + str(id) + "\n TCP address: " + str(addr) + "\n UDP address: " + str(
                    connsUDP[id]))

            except:
                log("Connection ended with: \n id: " + str(id) + "\n TCP address: " + str(
                    addr))

            remove_user(id)
            break

        if data == "CT" and id not in ct_players and id not in t_players:
            ct_players.append(id)

        if data == "T" and id not in ct_players and id not in t_players:
            t_players.append(id)


def socket_func_TCP():
    global id
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(3)

        # _thread.start_new_thread(start_main, ())
        while True:
            conn, addr = s.accept()

            conns[id] = conn

            TCPaddress[id] = addr

            bullets[id] = []
            grenades[id] = []

            log("Connection Started with: " + str(addr))

            # ui.update_user(id)
            _thread.start_new_thread(new_client, (conn, addr, id))

            id += 1

def socket_func():
    global id, s
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST, PORT))
    # _thread.start_new_thread(start_main, ())

    while True:
        try:
            data, address = s.recvfrom(262144)

            data = eval(data.decode())

            connsUDP[data["id"]] = address
            players[data["id"]] = data["player"]
            for bullet in data["bullets"]:
                # print(bullet)
                bullets[data["id"]].append(bullet)

            for grenade in data["grenades"]:
                grenades[data["id"]].append(grenade)

        except ConnectionResetError:
            pass

class Game(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs).__init__(vsync=False)

        self.frame_rate = 1 / 120

        pyglet.clock.schedule_interval(self.update, self.frame_rate)
        #pyglet.clock.set_fps_limit(FPS)

        self.set_location(1000, 500)

        self.keys = {key.A: False, key.W: False, key.D: False, key.S: False}

        self.buy_menu = False

    def on_key_press(self, symbol, modifiers):
        """
        When a key is pressed on
        the keyboard.
        :param symbol:
        :param modifiers:
        :return: None
        """
        self.keys[symbol] = True

        if symbol == key.ESCAPE:
            log("Server Stopped!")
            pyglet.app.exit()

    def on_key_release(self, symbol, modifiers):
        self.keys[symbol] = False

    def load(self):
        osystem = platform.system()

        if osystem == "Linux" or osystem == "Darwin":
            game_folder = os.getcwd()
            res_folder = game_folder + "/res"
            img_folder = res_folder + "/img"
            self.map_folder = res_folder + "/maps"
        elif osystem == "Windows":
            game_folder = path.dirname(__file__)
            res_folder = path.join(game_folder, "res")
            img_folder = path.join(res_folder, "img")
            self.map_folder = path.join(res_folder, "maps")

        self.player_images = {}
        for a in PLAYER_IMAGES:
            p = preload_img(PLAYER_IMAGES[a])
            texture = p.get_texture()
            texture.width = WEAPONS[a]["img_size"].x
            texture.height = WEAPONS[a]["img_size"].y

            self.player_images[a] = p

        self.crosshair_img = preload_img(CROSSHAIR_IMG)

        texture = self.crosshair_img.get_texture()
        texture.width = CROSSHAIR_WIDTH
        texture.height = CROSSHAIR_HEIGHT

        self.bullet_img = preload_img(BULLET_IMG)

        # x = texture.width / 2
        # y = texture.height / 2

        # cursor = pyglet.window.ImageMouseCursor(crosshair_img, x, y)
        # self.set_mouse_cursor(cursor)

        self.muzzle_flash_img = preload_img(MUZZLE_FLASH_IMG)
        texture = self.muzzle_flash_img.get_texture()
        texture.width = MUZZLE_FLASH_SIZE.x
        texture.height = MUZZLE_FLASH_SIZE.y

        self.granade_img = preload_img(GRENADE_IMG)
        texture = self.granade_img.get_texture()
        texture.width = GRENADE_SIZE.x
        texture.height = GRENADE_SIZE.y

        explosion = preload_img(EXPLOSION_IMG)
        explosion_seq = pyglet.image.ImageGrid(explosion, 4, 5, item_width=96, item_height=96)
        self.explosion_anim = pyglet.image.Animation.from_image_sequence(explosion_seq[0:], EXPLOSION_DURATION, loop=False)

        self.smoke_img = preload_img(SMOKE_GRENADE_IMG)
        texture = self.smoke_img.get_texture()
        texture.width = SMOKE_GRENADE_SIZE.x
        texture.height = SMOKE_GRENADE_SIZE.y

        self.smoke = preload_img(SMOKE_IMG)
        texture = self.smoke.get_texture()
        texture.width = SMOKE_SIZE.x
        texture.height = SMOKE_SIZE.y

        # smoke_seq = pyglet.image.ImageGrid(smoke, 6, 12, item_width=341, item_height=280)
        # self.smoke_anim = pyglet.image.Animation.from_image_sequence(smoke_seq[0:], SMOKE_DURATION, loop=False)


    def new(self):
        self.main_batch = pyglet.graphics.Batch()
        self.bullet_batch = pyglet.graphics.Batch()
        self.effects_batch = pyglet.graphics.Batch()
        self.hud_batch = pyglet.graphics.Batch()
        self.hud_logo_batch = pyglet.graphics.Batch()
        self.o_players_batch = pyglet.graphics.Batch()

        self.map = TiledRenderer((self.map_folder + "/" + MAP))

        self.hud_labels = []
        self.walls = []
        self.effects = []
        self.grenades = []
        self.o_players = []
        self.weapon_logos = {}
        self.o_bullets = []
        self.new_bullets = []
        self.new_grenades = []
        self.o_grenades = []

        for tile_object in self.map.tmx_data.objects:
            pos = Vector(tile_object.x, (self.map.size[1] - tile_object.y - tile_object.height))
            pos.x = pos.x + tile_object.width / 2
            pos.y = pos.y + tile_object.height / 2
            if tile_object.name == "Wall":
                self.walls.append(Wall(tile_object.x, pos.y - tile_object.height / 2, tile_object.width, tile_object.height))

            elif tile_object.name == "Player":
                self.player = Player(pos.x, pos.y, self, tile_object.type)

        self.bullets = []

        self.camera = Camera()

        self.mouse = Mouse(Sprite(self.crosshair_img), self)

        # self.hud_labels.append(Logo(SMOKE_LOGO_POS ,Sprite(self.smoke_logo, batch=self.hud_batch), self))

        #   Ammo Label
        l =  pyglet.text.Label("big lel", x=WINDOW_WIDTH, y=0, batch=self.hud_batch)
        l.anchor_x = "right"
        l.font_size = FONT_SIZE
        self.hud_labels.append(AmmoText(self, l))

        self.target = self.player

    def update(self, dt):
        # print(len(self.bullets))
        # print(len(self.effects))
        # print(len(self.grenades))
        # print(len(self.o_players))
        # print(ct_players)
        i_ids = []
        for id in players:
            i_ids.append(id)
            for player in self.o_players:
                if id == player.id:
                    player.rot = players[id]["rot"]
                    player.pos.x = players[id]["pos"]["x"]
                    player.pos.y = players[id]["pos"]["y"]
                    player.weapon = players[id]["weapon"]
                    if players[id]["respawn"]:
                        player.health = PLAYER_HEALTH
                        player.dead = False
                    break

            else:
                self.o_players.append(
                    Oplayers(id, Vector(players[id]["pos"]["x"], players[id]["pos"]["x"]),
                             players[id]["rot"], players[id]["weapon"], self))

        for player in self.o_players:
            if player.id not in i_ids:
                self.o_players.remove(player)

        temp = bullets
        for num in temp:
            for bullet in temp[num]:
                self.bullets.append(Bullet(bullet["pos"]["x"], bullet["pos"]["y"], bullet["rot"], self.bullet_img, bullet["weapon"], self, False))
                self.effects.append(MuzzleFlash(Vector(bullet["pos"]["x"], bullet["pos"]["y"]), bullet["rot"], self))
                bullets[num].remove(bullet)

        temp = grenades
        for id in temp:
            for grenade in temp[id]:
                Grenade(self, grenade["type"]).throw(Vector(grenade["pos"]["x"], grenade["pos"]["y"]),
                                                     Vector(grenade["vel"]["x"], grenade["vel"]["y"]), grenade["rot"],
                                                     True)
                grenades[id].remove(grenade)

        self.dt = dt


        self.player.vel.multiply(0)

        if self.keys[key.W]:
            self.player.vel.y += PLAYER_SPEED

        if self.keys[key.S]:
            self.player.vel.y += -PLAYER_SPEED

        if self.keys[key.D]:
            self.player.vel.x += PLAYER_SPEED

        if self.keys[key.A]:
            self.player.vel.x += -PLAYER_SPEED
            # print("yay")

        for bullet in self.bullets:
            bullet.update(dt)

            if bullet.distance > WEAPONS[bullet.weapon]["bullet_distance"] or bullet.check(self):
                bullet.sprite.delete()
                self.bullets.remove(bullet)

        for grenade in self.grenades:
            grenade.update(dt)

            if grenade.explode_sprite is not None:
                if grenade.explode_sprite.deleted:
                    self.grenades.remove(grenade)

        for effect in self.effects:
            effect.update(dt)

            if effect.dead:
                self.effects.remove(effect)

        self.player.update(dt, True)

        for player in self.o_players:
            player.update()

            if not player.dead:
                for bullet in self.bullets:
                    if bullet.check_player(player):
                        player.health -= WEAPONS[bullet.weapon]["damage"]
                        self.bullets.remove(bullet)

                for grenade in self.grenades:
                    if grenade.explode and not grenade.sent and grenade.type == "grenade":
                        mag = (player.pos - grenade.pos).magnitude()
                        if  mag <= GRENADE_DAMAGE_RADIUS:
                            dmg = round(GRENADE_DAMAGE / (mag / 32))
                            print(mag)
                            print(dmg)
                            print("----------")
                            player.health -= dmg


        tempB = []
        for bullet in self.bullets:
            tempB.append({"pos": {"x": bullet.pos.x, "y": bullet.pos.y}, "rot": bullet.rot, "weapon": bullet.weapon})

        tempG = []
        for grenade in self.grenades:
            if grenade.sent is False or grenade.type == "smoke":
                tempG.append({"pos": {"x": grenade.pos.x, "y": grenade.pos.y}, "exploded": grenade.explode, "type": grenade.type, "opacity": grenade.opacity})
                if grenade.explode:
                    grenade.sent = True

        playersC = dict(players)
        for player in self.o_players:
            playersC[player.id]["health"] = player.health
            if player.health <= 0:
                playersC[player.id]["dead"] = True
                player.dead = True

            else:
                playersC[player.id]["dead"] = False

        try:
            tempC = dict(connsUDP)
            for id in tempC:
                temp = dict(playersC)

                health = temp[id]["health"]

                del temp[id]

                d = {"players": temp, "bullets": tempB, "grenades": tempG, "health": health}
                # print(d)
                s.sendto(str(d).encode(), tempC[id])

        except:
            pass

    def on_draw(self):
        pyglet.clock.tick()

        self.clear()

        pyglet.gl.glPushMatrix()
        self.camera.draw(self.target)
        self.map.draw()
        self.main_batch.draw()
        # self.player.draw()
        for player in self.o_players:
            if not player.dead:
                player.sprite.draw()
                player.draw_hit_box()

        self.bullet_batch.draw()
        self.effects_batch.draw()

        for wall in self.walls:
            wall.draw()

        for grenade in self.grenades:
            grenade.draw_hit_box()

        pyglet.gl.glPopMatrix()


g = Game(WINDOW_WIDTH, WINDOW_HEIGHT, "Shooter 2", resizable=False)

g.load()
g.new()

_thread.start_new_thread(console, ())
_thread.start_new_thread(socket_func, ())
_thread.start_new_thread(socket_func_TCP, ())

pyglet.app.run()
