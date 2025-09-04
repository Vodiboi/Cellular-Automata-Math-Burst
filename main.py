import numpy as np
import copy
import pygame
import random
import signal
import functools
from collections import defaultdict
import sys
from params import FPS, SCR_HEIGHT, SCR_WIDTH, SIZE, FILL
x = sys.stdin
sys.stdin = open("initial.txt", "r")

class Game:
    def __init__(self, n, clrs) -> None:
        self.n = n
        self.grid = np.zeros((n, n), dtype=int)
        self.x_diff = np.array([0, 0, -1, -1, -1, 1, 1, 1])
        self.y_diff = np.array([-1, 1, 0, -1, 1, 0, -1, 1])
        self.clrs = clrs
        self.alive = set()

    def updt_cells(self):
        # 0 is a dead cell
        # print(self.grid)
        nxtgrd = copy.deepcopy(self.grid)
        toAdd = set()
        toRemove = set()
        done = set()
        for x in self.alive:
            poses = [(a, b) for (a, b) in zip(self.x_diff+x[0], self.y_diff+x[1]) if self._valid(a)*self._valid(b)] + [x]
            for i, j in poses:
                if self.grid[i, j] >= 3 or (i, j) in done:
                    continue
                done.add((i, j))
                # below is non-rous, below that is torus
                nearby = np.array([self.grid[a][b] if self._valid(a)*self._valid(b) else 0 for (a, b) in zip(self.x_diff+i, self.y_diff+j)])
                # nearby = self.grid[(self.x_diff+i) % self.n, (self.y_diff+j)%self.n]
                # print(nearby)
                soil = np.sum(nearby&1)
                if (self.grid[i][j]&1 and soil not in [2, 3]) or (not (self.grid[i][j]&1) and soil == 3):
                    nxtgrd[i, j] ^= 1
                water = np.sum(nearby&2)>>1
                if (self.grid[i][j]&2 and water not in [2, 3]) or (not (self.grid[i][j]&2) and water == 3):
                    nxtgrd[i, j] ^= 2
                    
                if nxtgrd[i, j] and (i, j) not in self.alive:
                    toAdd.add((i, j))
                if nxtgrd[i, j] == 0 and (i, j) in self.alive:
                    toRemove.add((i, j))
        for x in toAdd:
            self.alive.add(x)
        for x in toRemove:
            self.alive.remove(x)
        # print(nxtgrd[nxtgrd.astype(bool)>0])
        # s = np.sum(nxtgrd.astype(bool))
        # print(s, len(self.alive))
        self.grid = nxtgrd
    
    def clr_all_non_brick(self):
        rem = set()
        for x in self.alive:
            if self.grid[x] != 4:
                self.grid[x] = 0
                rem.add(x)
        for x in rem:
            self.alive.remove(x)
    def _valid(self, a):
        return 0 <= a and a < self.n

    def run_round(self) -> bool:
        self.updt_cells()
        return 1

    def make_grid_copy(self):
        return tuple([tuple(i) for i in self.grid])

    def make_grid_copy_scr(self):
        return tuple([tuple([self.map_color(i) for i in j]) for j in self.grid])

    def map_color(self, clr):
        return self.clrs[clr]

    def __str__(self) -> str:
        # return str(self.score)
        return ""


if __name__ == "__main__":
    NUM_STATES = 5
    # I reccomend grid size 50 for quick test games
    # one nice thing about grid size 100, soem games are just purely beautiful
    # one such neat combo for 100 is Nomad + Andy, so beautiful
    tp = int(input())
    GRID_SIZE = int(input())
    BLOCK_SIZE = SIZE/GRID_SIZE

    clrs = [FILL, (145, 97, 29), (58, 116, 201), (25, 128, 31), (191, 48, 29)]
    g = Game(GRID_SIZE, clrs)
    G = {"_": 0, "S": 1, "W": 2, "P":3}
    if (tp == 0):
        for i in range(GRID_SIZE):
            s = list(input())
            for j in range(GRID_SIZE):
                g.grid[i, j] = G[s[j]]
                g.alive.add((i, j))
    else:
        k = int(input())
        for i in range(k):
            a, b, t = input().split()
            a, b = int(a), int(b)
            g.grid[a, b] = G[t]
            g.alive.add((a, b))

    pygame.init()
    pygame.font.init()
    # have faith in the comic sans
    main_font = pygame.font.SysFont('Comic Sans MS', 24)
    scr = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
    clock = pygame.time.Clock()

    # rounds = 200000000000
    # sys.stdin = x

    def changecell(event):
        p = tuple((np.array(list(reversed(event.pos)))//BLOCK_SIZE).astype(int))
        if g._valid(p[0])*g._valid(p[1]) == 0: return
        # g.grid[p] += 1
        # g.grid[p] %= NUM_STATES
        g.grid[p] = selected
        if g.grid[p]:
            g.alive.add(p)
        elif p in g.alive:
            g.alive.remove(p)

    paused = 0
    st = 0
    selected = 0
    dwn = 0
    r = 0
    while 1:
        d = 0
        # input()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # print(g)
                exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    dwn = 0
                elif event.key == pygame.K_e:
                    # empty
                    selected = 0
                elif event.key == pygame.K_s:
                    # soil
                    selected = 1
                elif event.key == pygame.K_w:
                    # water
                    selected = 2
                elif event.key == pygame.K_g:
                    # grass
                    selected = 3
                elif event.key == pygame.K_b:
                    # brick
                    # print("A")
                    selected = 4
                elif paused and event.key == pygame.K_c:
                    g.clr_all_non_brick()
                    d=1
            elif paused and event.type == pygame.MOUSEBUTTONDOWN:
                changecell(event)
                d = 1
                dwn = 1
            elif event.type == pygame.MOUSEBUTTONUP:
                dwn = 0
            elif paused and dwn and event.type == pygame.MOUSEMOTION:
                changecell(event)
                d=1
        if not paused and st:
            nm = g.run_round()
        if not paused or d:
            r += 1
            # print(r)
            # print(FILL)
            scr.fill(FILL)
            grd = g.make_grid_copy_scr()
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    pygame.draw.rect(scr, grd[i][j], pygame.Rect(j*BLOCK_SIZE, i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            st += 1
            pygame.display.flip()
            # for i, b in enumerate(bots):
            #     t1 = main_font.render(f'{bots[i]} : {g.score[i+1]}', False, clrs[i+1])
                # scr.blit(t1, (20, 500 + i*24))
            # t1 = main_font.render(f'Round : {rnd+1}', False, (255, 255, 255))
            # scr.blit(t1, (20, 500 + (i+1)*24))
            # if nm == 0:
            #     break
        if st == 1:
            paused = 1

    # when game over, stall till user quit
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(g)
                exit(0)