import pygame, math, random, time
from fractions import Fraction

pygame.init()

class gun:
    def __init__(self, firate, Bspeed, Blife, damage, Glength, bLength, name, Goff, bwidth, bcolor):
        self.gunFirerate = firate
        self.damage = damage
        self.gunLength = Glength
        self.gunName = name
        self.GunOff = Goff

        self.bulletSpeed = Bspeed
        self.bulletLife = Blife
        self.bulletLength = bLength
        self.bulletWidth = bwidth
        self.bulletColor = bcolor

class game:
    def __init__(self):
        self.wW = 1200
        self.wH = 900

        pygame.mouse.set_visible(False)

        self.screenM = 20

        self.screen = pygame.display.set_mode((self.wW, self.wH))

        self.FPS = 120
        self.clock = pygame.time.Clock()

        self.Scolor = (150, 150, 150)
        self.color = (0, 0, 0)
        self.bulletColor = (255, 229, 22)
        self.TextColor = (255, 255, 255)
        self.pointerColor = (255, 0, 0)

        self.size = 10
        self.hitboxRe = 2

        self.speed = 3

        self.gunLength = 20
        self.gunWidth = 3
        self.gunFirerate = 2
        self.gunEndx = 1
        self.gunEndy = 1
        self.damage = 2
        self.GunOff = 60
        self.gunName = "MINIGUN"

        self.bulletLife = 1
        self.bulletLength = 10
        self.bulletWidth = 1
        self.bulletSpeed = 7

        #[[300, 0], 10, 20]

        self.enemySize = 20
        self.eLife = 20
        self.eSpeed = 2
        self.enemySpawn = 60
        self.enemyID = 1
        self.enemyText = False

        self.Psize = 3

        self.ene = True

        self.fontSize = 50

        self.font = pygame.font.SysFont("monospace", self.fontSize)

        self.guns = []

        #    1       2    3    4    5       6      7    8     9    10
        #(Firerate,speed,life,dmg,Glength,Blength,name,Goff,width,color)
        MINI = gun(self.gunFirerate, self.bulletSpeed, self.bulletLife, self.damage, self.gunLength, self.bulletLength, self.gunName, self.GunOff, self.bulletWidth, self.bulletColor)
        AWP = gun(80, 7, 20, 20, 30, 20, "AWP", 0, 2, self.bulletColor)
        M4 = gun(20, 7, 3, 10, 25, 12, "M4", 30, 1, self.bulletColor)
        RAILGUN = gun(1, 200, 100, 1, 30, 1000, "RAILGUN", 0, 4, (0, 255, 255))

        self.guns.append(MINI)
        self.guns.append(AWP)
        self.guns.append(M4)
        self.guns.append(RAILGUN)

        self.wallThickness = 10
        self.walls = [(self.wW / 4, (self.wH / 4) * 3, self.wW / 4 - 10, self.wallThickness), (self.wW / 4, self.wH / 4, self.wW / 2, self.wallThickness), (self.wW / 4, self.wH / 4, self.wallThickness, self.wH / 2), ((self.wW / 4) * 3, self.wH / 4, self.wallThickness, self.wH / 2)]

        game.restart(self)

    def wallRender(self):
        for a in self.walls:
            pygame.draw.rect(self.screen, self.color, pygame.Rect(a))

    def gunChange(self, num):
        byssa = self.guns[num]

        self.gunFirerate = byssa.gunFirerate
        self.bulletSpeed = byssa.bulletSpeed
        self.bulletLife = byssa.bulletLife
        self.damage = byssa.damage
        self.gunLength = byssa.gunLength
        self.bulletLength = byssa.bulletLength
        self.gunName = byssa.gunName
        self.GunOff = byssa.GunOff
        self.bulletWidth = byssa.bulletWidth
        self.bulletColor = byssa.bulletColor

    def restart(self):
        self.gP = False
        self.lose = False

        self.enemies = []

        self.shots = []

        self.x = int(self.wW / 2)
        self.y = int(self.wH / 2)

        self.score = 0

        self.enemyID = 1

    def pointer(self, tuple):
        x = tuple[0]
        y = tuple[1]

        pygame.draw.circle(self.screen, self.pointerColor, (x, y), self.Psize)

    def gunRender(self, tuple):
        x = tuple[0]
        y = tuple[1]

        vector = []
        vector.append(x - self.x)
        vector.append(y - self.y)

        lengd = math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))

        if lengd == 0:
            lengd = 1
        lengd = self.gunLength / lengd

        x1 = vector[0]
        y1 = vector[1]

        x1 = x1 * lengd
        y1 = y1 * lengd

        x = self.x + x1
        y = self.y + y1

        self.gunEndx = x
        self.gunEndy = y

        #print("X:", self.x, "Y:", self.y)
        #print("GX:", self.gunEndx, "GY:", self.gunEndy)

        pygame.draw.line(self.screen, self.color, (self.x,self.y), (x, y), self.gunWidth)

    def shoot(self, tuple):
        #[[x1, y1], [x2, x2], (v1, v2)]
        x = tuple[0]
        y = tuple[1]

        tala = random.randint(-(self.GunOff), self.GunOff)

        tala1 = random.randint(0, 1)

        if tala1 == 0:
            x = x + tala
        elif tala1 == 1:
            y = y + tala

        vector = []
        vector.append(x - self.gunEndx)
        vector.append(y - self.gunEndy)

        #print(vector)

        lengd = math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))

        try:
            lengdp = self.bulletLength / lengd

        except:
            lengdp = 1

        try:
            lengdv = self.bulletSpeed / lengd

        except:
            lengdv = 1

        x1 = vector[0]
        y1 = vector[1]

        x1 = (x1 * lengdp)
        y1 = (y1 * lengdp)

        x = self.gunEndx + x1
        y = self.gunEndy + y1

        xv = vector[0] * lengdv
        yv = vector[1] * lengdv

        vector = [xv, yv]

        s = [[self.gunEndx, self.gunEndy], [x, y], vector, self.bulletLife, []]

        self.shots.append(s)

        #game.gunFlare(self, tuple)

    #def gunFlare(self, tuple):


    def shots(self):
        for a in range(len(self.shots)):
            p1 = self.shots[a][0]
            p2 = self.shots[a][1]

            #print("P1:", p1, "P2:", p2)

            pygame.draw.line(self.screen, self.bulletColor,p1, p2, self.bulletWidth)

            p11 = [p1[0] + self.shots[a][2][0], p1[1] + self.shots[a][2][1]]
            p22 = [p2[0] + self.shots[a][2][0], p2[1] + self.shots[a][2][1]]

            self.shots[a].insert(0, p11)
            self.shots[a].remove(p1)
            self.shots[a].insert(1, p22)
            self.shots[a].remove(p2)

        temp = self.shots
        for a in temp:
            if a[0][0] < 0 or a[0][0] > self.wW or a[0][1] < 0 or a[0][1] > self.wH:
                self.shots.remove(a)

    def Newenemy(self):
        side = random.randint(0, 3)

        if side == 0:
            x = random.randint(0, self.wW)
            y = random.randint(-50, 0 - self.enemySize)

        elif side == 1:
            x = random.randint(-50, 0 - self.enemySize)
            y = random.randint(0, self.wH)

        elif side == 2:
            x = random.randint(0, self.wW)
            y = random.randint(self.wH + self.enemySize, self.wH + 50)

        elif side == 3:
            x = random.randint(self.wW + self.enemySize, self.wW + 50)
            y = random.randint(0, self.wH)

        e = [[x, y], self.enemySize, self.eLife, self.enemyID]

        self.enemyID += 1
        #print("E:", e)

        self.enemies.append(e)

    def enemy(self):
        for a in range(len(self.enemies)):
            x = self.enemies[a][0][0]
            y = self.enemies[a][0][1]

            size = self.enemies[a][1]
            life = self.enemies[a][2]

            # pygame.draw.line(self.screen, self.color,[x, y], [x, y + self.enemySize], size)
            #pygame.draw.circle(self.screen, self.color, [x, y], size)

            pygame.draw.rect(self.screen, self.color, pygame.Rect(x, y, size, size))

            if self.enemyText is True:
                Efont = pygame.font.SysFont("arial", size)

                if life >= 10:
                    label = Efont.render(str(life), 1, self.TextColor)
                else:
                    label = Efont.render("0" + str(life), 1, self.TextColor)

                self.screen.blit(label, (x + 1, y - 2))


        temp = self.enemies
        tel = 0
        for a in temp:
            x = a[0][0]
            y = a[0][1]

            size = a[1]
            life = a[2]
            ID = a[3]

            vector = []
            vector.append(self.x - x)
            vector.append(self.y - y)

            lengd = math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))

            try:
                lengd = self.eSpeed / lengd

            except:
                lengd = 1

            x1 = vector[0]
            y1 = vector[1]

            x1 = (x1 * lengd)
            y1 = (y1 * lengd)

            #print("X1:", x1, "   Y1:", y1)
            #time.sleep(3)

            for b in self.enemies:
                x2 = b[0][0]
                y2 = b[0][1]

                size2 = b[1]
 #               print("B:", b)
                #time.sleep(3)

                if a != b:
                    if ((x + x1 + size) >= (x2) and (y + size) >= (y2)) and (x + x1 <= x2 + size2 and y <= y2 + size2):
                        x1 = 0

                    if ((x + size) >= (x2) and (y + y1 + size) >= (y2)) and (x <= x2 + size2 and y + y1 <= y2 + size2):
                        y1 = 0

            #(x, y, xS, yS)
            for b in self.walls:
                xW = b[0]
                yW = b[1]

                sX = b[2]
                sY = b[3]


                if (x + x1 + size > xW and y + size > yW) and (x + x1 < xW + sX and y < yW + sY):
                    x1 = 0

                if (x + size > xW and y + y1 + size > yW) and (x < xW + sX and y + y1 < yW + sY):
                    y1 = 0

            e = [[x + x1, y + y1], size, life, ID]

            self.enemies.insert(tel, e)
            self.enemies.remove(a)
            #print(self.enemies)
            #time.sleep(3)
            tel += 1

    def checkP(self):
        for a in self.enemies:
            x = a[0][0]
            y = a[0][1]

            size = a[1]

            vector1 = []
            vector1.append(x - self.x)
            vector1.append(y - self.y)

            vector2 = []
            vector2.append(x - self.x)
            vector2.append(y + size - self.y)

            vector3 = []
            vector3.append(x - self.x)
            vector3.append((y + size / 2) - self.y)

            vector4 = []
            vector4.append((x + size / 2) - self.x)
            vector4.append(y - self.y)

            vector5 = []
            vector5.append((x + size) - self.x)
            vector5.append(y - self.y)

            vector6 = []
            vector6.append((x + size) - self.x)
            vector6.append((y + size / 2) - self.y)

            vector7 = []
            vector7.append((x + size / 2) - self.x)
            vector7.append((y + size) - self.y)

            vector8 = []
            vector8.append((x + size) - self.x)
            vector8.append((y + size) - self.y)

            sizeP = self.size - self.hitboxRe

            if float(sizeP) > math.sqrt(math.pow(vector1[0], 2) + math.pow(vector1[1], 2)) or float(sizeP) > math.sqrt(math.pow(vector2[0], 2) + math.pow(vector2[1], 2)) or float(sizeP) > math.sqrt(math.pow(vector3[0], 2) + math.pow(vector3[1], 2)) or float(sizeP) > math.sqrt(math.pow(vector4[0], 2) + math.pow(vector4[1], 2)) or float(sizeP) > math.sqrt(math.pow(vector5[0], 2) + math.pow(vector5[1], 2)) or float(sizeP) > math.sqrt(math.pow(vector6[0], 2) + math.pow(vector6[1], 2)) or float(sizeP) > math.sqrt(math.pow(vector7[0], 2) + math.pow(vector7[1], 2)) or float(sizeP) > math.sqrt(math.pow(vector8[0], 2) + math.pow(vector8[1], 2)):
                game.tap(self)

    def checkE(self):
        # [[x, y], self.enemySize, self.eLife]
        # [[x1, y1], [x2, x2], (v1, v2), Slife, [ID]]

        if self.gunName == "RAILGUN":
            print("asafddddddddda")

        else:
            temps = self.shots
            telS = 0

            #print(len(self.shots))
            #print(len(temps))
            #print("---")

            for a in temps:
                p1 = a[0]
                p2 = a[1]

                v = a[2]

                Slife = a[3]
                IDlist = a[4]

                #print(a)

                temp = self.enemies
                tel = 0

                for b in temp:
                    x = b[0][0]
                    y = b[0][1]

                    size = b[1]
                    life = b[2]
                    ID = b[3]

                    if p1[0] > x and p1[0] < x + size and p1[1] > y and p1[1] < y + size and ID not in IDlist:
                        #shot = a

                        #print(Slife)
                        #print(a)

                        #shot.remove(Slife)
                        #shot.insert(3, Slife - 1)

                        #shot[4].append(ID)

                        IDlist.append(ID)

                        s = [p1, p2, v, Slife - 1, IDlist]

                        self.shots.remove(a)

                        if Slife - 1 > 0:
                            self.shots.insert(telS, s)

                        e = [[x, y], size, life - self.damage, ID]
                        #print("E:", e)
                        #print("B:", b)
                        #time.sleep(3)
                        self.enemies.remove(b)

                        if life - self.damage > 0:
                            self.enemies.insert(tel, e)

                        else:
                            self.score += 1

                        break

                    tel += 1
                telS += 1

    def tap(self):
        self.lose = True
        label = self.font.render("Game Over", 1, self.TextColor)
        self.screen.blit(label, (self.wW / 2 - self.fontSize * 3, self.wH / 2 - (self.fontSize / 2)))

    def pause(self):
        self.gP = not self.gP
        label = self.font.render("Game Paused", 1, self.TextColor)
        self.screen.blit(label, ((self.wW / 2) - 120, (self.wH / 2) - 50))

    def loop(self):
        tel = self.gunFirerate
        telE = self.enemySpawn
        while True:
            #print("Ls:", len(self.shots))
            #print("Le:", len(self.enemies))

            #for a in self.shots:
             #   print(a)

            #for a in self.enemies:
             #   print(a)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_p and self.lose == False:
                        game.pause(self)
                    if event.key == pygame.K_1:
                        game.gunChange(self, 0)
                    elif event.key == pygame.K_2:
                        game.gunChange(self, 1)
                    elif event.key == pygame.K_3:
                        game.gunChange(self, 2)
                    elif event.key == pygame.K_4:
                        game.gunChange(self, 3)
                    elif event.key == pygame.K_ESCAPE:
                        quit()

                    if event.key == pygame.K_F1:
                        self.enemyText = not self.enemyText

            poss = pygame.mouse.get_pos()
            mpressed = pygame.mouse.get_pressed()
            pressed = pygame.key.get_pressed()

            if self.gP is False and self.lose is False:
                self.screen.fill(self.Scolor)

                if self.y > 0 + self.size:
                    if pressed[pygame.K_w]:
                        self.y -= self.speed
                if self.y < self.wH - self.size:
                    if pressed[pygame.K_s]:
                        self.y += self.speed
                if self.x > 0 + self.size:
                    if pressed[pygame.K_a]:
                        self.x -= self.speed
                if self.x < self.wW - self.size:
                    if pressed[pygame.K_d]:
                        self.x += self.speed
                if mpressed[0] == 1 and tel >= self.gunFirerate:
                    game.shoot(self, poss)
                    tel = 0

                pygame.draw.circle(self.screen, self.color,(self.x, self.y), self.size)

                game.gunRender(self,poss)

                game.shots(self)

                if telE >= self.enemySpawn and self.ene == True and (len(self.enemies) < 30):
                    game.Newenemy(self)
                    telE = 0

                tel += 1
                telE += 1

                game.enemy(self)

                game.checkP(self)

                if len(self.shots) > 0:
                    game.checkE(self)

                game.wallRender(self)

                game.pointer(self, poss)

                label = self.font.render(str(self.score), 1, self.TextColor)
                self.screen.blit(label, (0, 0))

                gname = self.font.render(self.gunName, 1, self.TextColor)
                self.screen.blit(gname, (0, self.wH - self.fontSize))

            if self.gP is False and self.lose is False:
                if poss[0] < self.screenM:
                    pygame.mouse.set_pos([self.screenM, poss[1]])
                if poss[0] > self.wW - self.screenM:
                    pygame.mouse.set_pos(self.wW - self.screenM, poss[1])
                if poss[1] < self.screenM:
                    pygame.mouse.set_pos([poss[0], self.screenM])
                if poss[1] > self.wH - self.screenM:
                    pygame.mouse.set_pos([poss[0], self.wH - self.screenM])

            if pressed[pygame.K_r]:
                game.restart(self)

            pygame.display.flip()
            self.clock.tick(self.FPS)

H = game()
H.loop()