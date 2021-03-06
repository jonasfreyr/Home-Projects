from settings import *
from pyglet.sprite import Sprite
import random
from pyglet.gl import *

class O_Bullet:
    def __init__(self, x, y, rot, weapon, game):
        self.pos = Vector(x, y)

        self.rot = rot

        self.sprite = Sprite(game.bullet_img, x, y, batch=game.bullet_batch)
        self.sprite.update(rotation=rot, scale=WEAPONS[weapon]["bullet_size"])
        self.sprite.image.anchor_x = self.sprite.image.width / 2
        self.sprite.image.anchor_y = self.sprite.image.height / 2

class O_Grenade:
    def __init__(self, x, y, type, game):
        self.pos = Vector(x, y)
        self.type = type
        self.game = game

        if type == "grenade":
            self.sprite = Sprite(game.granade_img, x, y, batch=game.main_batch)

        elif type == "smoke":
            self.sprite = Sprite(game.smoke_img, x, y, batch=game.main_batch)

        self.sprite.image.anchor_x = self.sprite.width / 2
        self.sprite.image.anchor_y = self.sprite.height / 2

        self.exploded = False
        self.duration = 0
        self.opacity = 255
        self.explode_sprite = None

    def explode(self):
        self.exploded = True

        if self.type == "grenade":
            self.explode_sprite = Animation(self.game.explosion_anim, self.pos.x, self.pos.y,
                                            batch=self.game.effects_batch)

            self.explode_sprite.x = self.pos.x - self.explode_sprite.width / 2
            self.explode_sprite.y = self.pos.y - self.explode_sprite.height / 2

        elif self.type == "smoke":
            self.sprite = Sprite(self.game.smoke, self.pos.x, self.pos.y, batch=self.game.effects_batch)

            self.sprite.image.anchor_x = self.sprite.width / 2
            self.sprite.image.anchor_y = self.sprite.height / 2


class Bullet:
    def __init__(self, x, y, rot, img, weapon, game, main=True, owner=None):
        self.o_pos = Vector(x, y)
        self.prev_pos = Vector(x - 1, y - 1)
        self.pos = Vector(x, y)
        self.vector = Vector(WEAPONS[weapon]["bullet_speed"], 0).rotate(-rot)

        self.weapon = weapon

        self.sprite = Sprite(img, batch=game.bullet_batch)
        self.sprite.update(rotation=rot, scale=WEAPONS[weapon]["bullet_size"])
        self.sprite.image.anchor_x = self.sprite.image.width / 2
        self.sprite.image.anchor_y = self.sprite.image.height / 2

        self.distance = 0

        self.rot = rot

        if main:
            game.o_bullets.append({"rot": rot, "pos": {"x": x, "y": y}, "weapon": weapon})

        self.owner = owner

    def check(self, game):
        for wall in game.walls:
            if wall.pos.x + wall.width > self.pos.x > wall.pos.x and wall.pos.y + wall.height > self.pos.y > wall.pos.y:
                return True

            if lineLine(wall.pos.x, wall.pos.y, wall.pos.x, wall.pos.y + wall.height, self.pos.x, self.pos.y, self.prev_pos.x, self.prev_pos.y):
                return True

            if lineLine(wall.pos.x, wall.pos.y, wall.pos.x + wall.width, wall.pos.y, self.pos.x, self.pos.y, self.prev_pos.x, self.prev_pos.y):
                return True

            if lineLine(wall.pos.x + wall.width, wall.pos.y, wall.pos.x + wall.width, wall.pos.y + wall.height, self.pos.x, self.pos.y, self.prev_pos.x, self.prev_pos.y):
                return True

            if lineLine(wall.pos.x + wall.width, wall.pos.y + wall.height, wall.pos.x, wall.pos.y + wall.height, self.pos.x, self.pos.y, self.prev_pos.x, self.prev_pos.y):
                return True

        return False

    def check_player(self, player):
        if player.hit_box.x + player.hit_box.width > self.pos.x > player.hit_box.x and player.hit_box.y + player.hit_box.height > self.pos.y > player.hit_box.y:
            return True

        if lineLine(player.hit_box.x, player.hit_box.y, player.hit_box.x + player.hit_box.width, player.hit_box.y, self.pos.x, self.pos.y,
                    self.prev_pos.x, self.prev_pos.y):
            return True

        if lineLine(player.hit_box.x + player.hit_box.width, player.hit_box.y, player.hit_box.x + player.hit_box.width, player.hit_box.y + player.hit_box.height, self.pos.x,
                    self.pos.y, self.prev_pos.x, self.prev_pos.y):
            return True

        if lineLine(player.hit_box.x + player.hit_box.width, player.hit_box.y + player.hit_box.height, player.hit_box.x, player.hit_box.y + player.hit_box.height, self.pos.x,
                    self.pos.y, self.prev_pos.x, self.prev_pos.y):
            return True

        if lineLine(player.hit_box.x, player.hit_box.y + player.hit_box.height, player.hit_box.x, player.hit_box.y, self.pos.x, self.pos.y,
                    self.prev_pos.x, self.prev_pos.y):
            return True

        return False

    def update(self,dt):
        self.prev_pos = self.pos.copy()

        self.pos.x += self.vector.x  * dt
        self.pos.y += self.vector.y * dt

        self.sprite.x = self.pos.x
        self.sprite.y = self.pos.y

        self.distance = Vector(self.pos.x - self.o_pos.x, self.pos.y - self.o_pos.y).magnitude()

class Weapon:
    def __init__(self, weapon):
        self.name = weapon
        self.type = WEAPONS[weapon]["type"]

        self.ammo_in_mag = WEAPONS[weapon]["ammo_clip"]
        self.extra_ammo = WEAPONS[weapon]["ammo_max"]

        self.max_ammo_in_mag = self.ammo_in_mag
        self.max_extra_ammo = self.extra_ammo

        self.fired = False

        self.spray_num = 0

        self.recovery_time = 0

    def reset(self):
        self.fired = False

    def reload(self):
        if self.extra_ammo > 0 and self.ammo_in_mag != self.max_ammo_in_mag and self.fired is False:
            if self.type != "shotgun":
                a = self.max_ammo_in_mag - self.ammo_in_mag

                if self.extra_ammo - a < 0:
                    a = self.extra_ammo
                    self.extra_ammo = 0

                else:
                    self.extra_ammo -= a

                self.ammo_in_mag += a

            else:
                self.ammo_in_mag += 1
                self.extra_ammo -= 1

    def line_collide(self, game, pos, o):
        for wall in game.walls:
            topleft = [wall.pos.x, wall.pos.y + wall.height]
            topright = [wall.pos.x + wall.width, wall.pos.y + wall.height]

            bottomleft = [wall.pos.x, wall.pos.y]
            bottomright = [wall.pos.x + wall.width, wall.pos.y]

            left = lineLine(pos.x, pos.y, o.x, o.y, topleft[0], topleft[1], topleft[0], bottomleft[1])

            right = lineLine(pos.x, pos.y, o.x, o.y, topright[0], topright[1], topright[0], bottomright[1])

            top = lineLine(pos.x, pos.y, o.x, o.y, topleft[0], topleft[1], topright[0], topright[1])

            bottom = lineLine(pos.x, pos.y, o.x, o.y, bottomleft[0], bottomleft[1], bottomright[0], bottomright[1])

            if left or right or top or bottom:
                return True

        return False

    def shoot(self, pos, o_pos, rot, game):
        if self.ammo_in_mag > 0:
            if self.type == "auto":
                if self.spray_num > len(WEAPONS[self.name]["spread"]) - 1:
                    self.spray_num = 0

                spread = WEAPONS[self.name]["spread"][self.spray_num]
                # game.bullets.append(Bullet(pos.x, pos.y, rot + spread, game.bullet_img, self.name, game))
                if not self.line_collide(game, o_pos, pos):
                    game.o_bullets.append({"rot": rot + spread, "pos": {"x": pos.x, "y": pos.y}, "weapon": self.name})
                self.spray_num += 1
                self.ammo_in_mag -= 1
                game.effects.append(MuzzleFlash(pos, rot, game))

            elif self.type == "semi-auto" and self.fired is False:
                spread = random.uniform(-WEAPONS[self.name]['spread'], WEAPONS[self.name]['spread'])
                # game.bullets.append(Bullet(pos.x, pos.y, rot + spread, game.bullet_img, self.name, game))
                if not self.line_collide(game, o_pos, pos):
                    game.o_bullets.append({"rot": rot + spread, "pos": {"x": pos.x, "y": pos.y}, "weapon": self.name})
                self.ammo_in_mag -= 1
                game.effects.append(MuzzleFlash(pos, rot, game))

            elif self.type == "shotgun" and self.fired is False:
                for a in range(WEAPONS[self.name]['bullet_count']):
                    spread = random.uniform(-WEAPONS[self.name]['spread'], WEAPONS[self.name]['spread'])
                    # game.bullets.append(Bullet(pos.x, pos.y, rot + spread, game.bullet_img, self.name, game))
                    if not self.line_collide(game, o_pos, pos):
                        game.o_bullets.append({"rot": rot + spread, "pos": {"x": pos.x, "y": pos.y}, "weapon": self.name})
                self.ammo_in_mag -= 1
                game.effects.append(MuzzleFlash(pos, rot, game))

            self.fired = True

    def update(self, dt):
        if self.type == "auto":
            if self.recovery_time >= WEAPONS[self.name]["recovery_time"]:
                self.spray_num = 0
                self.recovery_time = 0

            else:
                self.recovery_time += dt

class Animation(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.deleted = False

    def on_animation_end(self):
        self.delete()
        self.deleted = True

class Grenade:
    def __init__(self, game, type, owner=False):
        self.game = game

        self.type = type

        self.explode = False

        self.tossed = False

        self.duration = 0
        self.opacity = 255

        self.sent = False

        self.owner = owner

    def throw(self, pos, vel, rot, o=False):
        self.distance = 0
        self.pos = pos
        self.vel = vel.rotate(-rot)

        if self.type == "grenade":
            self.sprite = Sprite(self.game.granade_img, pos.x, pos.y, batch=self.game.main_batch)

        elif self.type == "smoke":
            self.sprite = Sprite(self.game.smoke_img, pos.x, pos.y, batch=self.game.main_batch)

        self.sprite.image.anchor_x = self.sprite.width / 2
        self.sprite.image.anchor_y = self.sprite.height / 2

        self.explode_sprite = None

        self.hit_box = GRENADE_HIT_BOX.copy()
        self.hit_box.x = pos.x - self.hit_box.width / 2
        self.hit_box.y = pos.y - self.hit_box.height / 2

        self.tossed = True

        if o is True:
            self.game.grenades.append(self)

        self.game.o_grenades.append({"pos": {"x": pos.x, "y": pos.y}, "vel": {"x": vel.x, "y": vel.y}, "rot": rot, "type": self.type})

    def collide_with_walls(self, dir):
        if dir == "x":
            for wall in self.game.walls:
                if (self.hit_box.x + self.hit_box.width > wall.pos.x and self.hit_box.y + self.hit_box.height > wall.pos.y) and (self.hit_box.x < wall.pos.x + wall.width and self.hit_box.y < wall.pos.y + wall.height):
                    if wall.center.x > self.hit_box.get_center().x:
                        self.hit_box.x = wall.pos.x - self.hit_box.width

                    elif wall.center.x < self.hit_box.get_center().x:
                        self.hit_box.x = wall.pos.x + wall.width

                    self.vel.x = -self.vel.x

        elif dir == "y":
            for wall in self.game.walls:
                if (self.hit_box.x + self.hit_box.width > wall.pos.x and self.hit_box.y + self.hit_box.height > wall.pos.y) and (self.hit_box.x < wall.pos.x + wall.width and self.hit_box.y < wall.pos.y + wall.height):
                    if wall.center.y > self.hit_box.get_center().y:
                        self.hit_box.y = wall.pos.y - self.hit_box.height

                    elif wall.center.y < self.hit_box.get_center().y:
                        self.hit_box.y = wall.pos.y + wall.height

                    self.vel.y = -self.vel.y

    def draw_hit_box(self):
        glBegin(GL_LINES)

        glVertex2i(int(self.hit_box.x), int(self.hit_box.y))
        glVertex2i(int(self.hit_box.x), int(self.hit_box.y + self.hit_box.height))

        glVertex2i(int(self.hit_box.x), int(self.hit_box.y + self.hit_box.height))
        glVertex2i(int(self.hit_box.x + self.hit_box.width), int(self.hit_box.y + self.hit_box.height))

        glVertex2i(int(self.hit_box.x + self.hit_box.width), int(self.hit_box.y + self.hit_box.height))
        glVertex2i(int(self.hit_box.x + self.hit_box.width), int(self.hit_box.y))

        glVertex2i(int(self.hit_box.x + self.hit_box.width), int(self.hit_box.y))
        glVertex2i(int(self.hit_box.x), int(self.hit_box.y))

        glEnd()

    def update(self, dt):
        if self.distance <= GRENADE_DISTANCE and self.tossed:
            # check hit box collisions
            self.hit_box.x += self.vel.x * dt
            self.collide_with_walls("x")

            self.hit_box.y += self.vel.y * dt
            self.collide_with_walls("y")

            self.pos.x = self.hit_box.x + self.hit_box.width / 2
            self.pos.y = self.hit_box.y + self.hit_box.height / 2

            self.sprite.x = self.pos.x
            self.sprite.y = self.pos.y

            self.distance += self.vel.magnitude() * dt

        else:
            if self.explode is False:
                self.sprite.delete()

                self.vel.multiply(0)
                self.explode = True
                if self.type == "grenade":
                    self.explode_sprite = Animation(self.game.explosion_anim, self.pos.x, self.pos.y, batch=self.game.effects_batch)

                elif self.type == "smoke":
                    self.explode_sprite = Animation(self.game.smoke, self.pos.x, self.pos.y, batch=self.game.effects_batch)

                    self.duration = SMOKE_DURATION

                self.explode_sprite.x = self.pos.x - self.explode_sprite.width / 2
                self.explode_sprite.y = self.pos.y - self.explode_sprite.height / 2

        if self.type == "smoke" and self.explode is True:
            if self.duration <= 0:
                if self.opacity <= 0:
                    self.explode_sprite.deleted = True

                self.explode_sprite.opacity = self.opacity
                if self.opacity > 0:
                    self.opacity -= int(300 * dt)

            else:
                self.duration -= dt


class MuzzleFlash:
    def __init__(self, pos, rot, game):
        self.pos = pos

        self.rot = rot

        self.time = 0

        self.sprite = Sprite(game.muzzle_flash_img, batch=game.effects_batch)
        self.sprite.update(rotation=rot)
        self.sprite.image.anchor_x = self.sprite.width / 3
        self.sprite.image.anchor_y = self.sprite.height / 2
        self.dead = False

        self.sprite.x = pos.x
        self.sprite.y = pos.y

    def update(self, dt):
        self.time += dt

        if self.time > MUZZLE_FLASH_LIFESPAWN:
            self.sprite.delete()
            self.dead = True

