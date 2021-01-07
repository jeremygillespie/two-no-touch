import numpy as np
import random
from collections import deque


max_min_zone_attempts = 50


class Search_node:
    def __init__(self, zones, p, z):
        self.p = p
        self.zones = zones.copy()
        self.zones[p] = z


class Graph:
    def __init__(self, size):
        self.size = size
        self.num_dots = self.size * 2

        self.dots = np.full((self.size, self.size), False, dtype=np.bool)
        self.zones = np.full((self.size, self.size), -1, dtype=np.int8)

    def one_solution(self):
        self.num_solutions = 0
        dots = np.full((self.size, self.size), False, dtype=np.bool)
        zone_count = np.full((self.size), 0, dtype=np.int)
        self.recurse_one_solution(dots, 0, zone_count)
        return self.num_solutions == 1

    def recurse_one_solution(self, dots, x, zone_count):
        if np.any(zone_count == 3):
            return

        if np.all(zone_count == 2):
            self.num_solutions += 1
            return

        if x == self.size:
            return

        v = self.valid_rows(dots, x)
        if len(v) < 2:
            return

        for y1 in range(self.size):
            for y2 in range(self.size):
                if y1 > y2 + 1 and v[y1] and v[y2]:
                    new_dots = dots.copy()
                    new_dots[x, y1] = True
                    new_dots[x, y2] = True

                    new_zc = zone_count.copy()
                    new_zc[self.zones[x, y1]] += 1
                    new_zc[self.zones[x, y2]] += 1

                    self.recurse_one_solution(new_dots, x + 1, new_zc)
                    if self.num_solutions > 1:
                        return

    def zones_full(self, dots):
        for n in range(self.size):
            if np.count_nonzero(np.logical_and(self.zones == n, dots)) < 2:
                return False
        return True

    def gen_min_zones(self):
        self.zones = None

        while self.zones is None:
            self.min_zones_attempts = 0
            self.gen_dots()
            assigned = np.full((self.num_dots), False, dtype=np.bool)
            self.zones = np.full((self.size, self.size), -1, dtype=np.int8)
            self.zones = self.recurse_gen_min_zones(self.zones, assigned, 0)

    def gen_dots(self):
        dots = np.full((self.size, self.size), False, dtype=np.bool)
        self.dots = self.recurse_gen_dots(dots, 0)

        self.dot_loc = []
        for x in range(self.size):
            for y in range(self.size):
                if self.dots[x, y]:
                    self.dot_loc.append((x, y))

    def recurse_gen_min_zones(self, zones, assigned, z):
        self.min_zones_attempts += 1
        if self.min_zones_attempts > max_min_zone_attempts:
            return None

        if z == self.size:
            return zones

        if self.isolated_dot(zones, assigned):
            return None

        r1 = list(range(self.num_dots))
        r2 = list(range(self.num_dots))
        random.shuffle(r1)
        random.shuffle(r2)

        for d1 in r1:
            for d2 in r2:
                if d1 != d2 and not assigned[d1] and not assigned[d2]:
                    result = zones.copy()
                    result = self.find_zone(result, d1, d2, z)
                    if result is not None:
                        self.zones = result
                        new_assigned = assigned.copy()
                        new_assigned[d1] = True
                        new_assigned[d2] = True
                        result = self.recurse_gen_min_zones(
                            result, new_assigned, z + 1)
                        if result is not None:
                            return result
        return None

    def isolated_dot(self, zones, assigned):
        for d in range(self.num_dots):
            if not assigned[d]:
                q = deque()
                q.append(self.dot_loc[d])

                checked = np.full((self.size, self.size), False, dtype=np.bool)

                while True:
                    if len(q) == 0:
                        return True

                    p = q.popleft()
                    if self.dots[p]:
                        break
                    checked[p] = True

                    for adj in self.adjacent(p):
                        if not checked[adj] and zones[adj] == -1:
                            q.append(adj)

        return False

    def adjacent(self, p):
        x = p[0]
        y = p[1]

        result = []
        for p1 in [(x, y + 1), (x, y - 1), (x - 1, y), (x + 1, y)]:
            x1 = p1[0]
            y1 = p1[1]
            if x1 < 0 or y1 < 0:
                continue
            if x1 >= self.size or y1 >= self.size:
                continue
            result.append(p1)

        return result

    def find_zone(self, zones, d1, d2, z):
        q = deque()
        q.append(Search_node(zones, self.dot_loc[d1], z))

        checked = np.full((self.size, self.size), False, dtype=np.bool)

        while len(q) > 0:
            n = q.popleft()
            checked[n.p] = True

            for adj in self.adjacent(n.p):
                if adj == self.dot_loc[d2]:
                    return Search_node(n.zones, adj, z).zones
                elif not checked[adj] and not self.dots[adj] and n.zones[adj] == -1:
                    q.append(Search_node(n.zones, adj, z))

        return None

    def recurse_gen_dots(self, dots, x):
        if x == self.size:
            return dots

        v = self.valid_rows(dots, x)

        r1 = list(range(self.size))
        r2 = list(range(self.size))
        random.shuffle(r1)
        random.shuffle(r2)

        for y1 in r1:
            for y2 in r2:
                if y1 > y2 + 1 and v[y1] and v[y2]:
                    result = dots.copy()
                    result[x, y1] = True
                    result[x, y2] = True

                    result = self.recurse_gen_dots(result, x + 1)
                    if result is not None:
                        return result
        return None

    def valid_rows(self, dots, x):
        result = np.full((self.size), True, dtype=np.bool)
        if x == 0:
            return result
        else:
            for y in range(self.size):
                if dots[x - 1, y]:
                    result[y] = False
                elif y > 0 and dots[x - 1, y - 1]:
                    result[y] = False
                elif y < self.size - 1 and dots[x - 1, y + 1]:
                    result[y] = False
                elif self.row_full(dots, y):
                    result[y] = False
            return result

    def row_full(self, dots, y):
        return np.count_nonzero(dots[:, y]) > 1

    def string(self, dots, zones):
        result = ""
        for y in range(self.size - 1, -1, -1):
            for x in range(self.size):
                if zones[x, y] != -1:
                    if dots[x, y]:
                        result += '['
                        result += str(zones[x, y])
                        result += ']'
                    else:
                        result += ' '
                        result += str(zones[x, y])
                        result += ' '
                else:
                    result += '   '

            result += '\n'

        return result

    def __str__(self):
        return self.string(self.dots, self.zones)


g = Graph(10)
while True:
    g.gen_dots()
    g.gen_min_zones()
    print(g)
    if g.one_solution():
        print('done')
        break
