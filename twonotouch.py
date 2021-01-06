import random
import numpy as np

size = 8


def output(graph, zones):
    for y in range(size):
        for x in range(size):
            if graph[x, y]:
                print(zones[x, y], '*', end='\t')
            else:
                print(zones[x, y], end='\t')
        print()
    print()


def count_row(y, graph):
    result = 0
    for x in range(size):
        if graph[x, y]:
            result += 1
    return result


def valid_rows(x, graph):
    if x == 0:
        return list(range(size))

    result = []

    for y in range(size):
        if graph[x - 1, y]:
            continue

        if y > 0 and graph[x - 1, y - 1]:
            continue

        if y < size - 1 and graph[x - 1, y + 1]:
            continue

        if count_row(y, graph) >= 2:
            continue

        result.append(y)

    return result


def fill(x, graph):
    if x == size:
        return graph

    rows = valid_rows(x, graph)
    rows_a = rows
    rows_b = rows[:]

    random.shuffle(rows_a)
    random.shuffle(rows_b)

    for a in rows_a:
        for b in rows_b:
            if abs(a - b) > 1:

                graph_new = np.copy(graph)
                graph_new[x, a] = True
                graph_new[x, b] = True

                result = fill(x + 1, graph_new)
                if len(result) > 0:
                    return result

    return np.array([])


def adjacent_points(p):
    result = []
    x = p[0]
    y = p[1]
    for p1 in [(x, y+1), (x+1, y), (x, y-1), (x-1, y)]:
        if p1[0] < 0 or p1[1] < 0:
            continue
        if p1[0] >= size or p1[1] >= size:
            continue
        result.append(p1)
    return result


def adjacent_zones(p, zones):
    result = []
    for p1 in adjacent_points(p):
        z = zones[p1]
        if z != -1:
            result.append(z)
    return result


def target_zones(count, accessible):
    valid = count < 2
    if not valid.any():
        return np.array([])
    valid = accessible == min(accessible[valid])
    return np.array(range(size))[valid]


def update_accessible(graph, zones, accessible, center):
    result = np.full((size), 0, dtype=np.int32)
    for z in range(size):
        can_visit = np.full((size, size), True, dtype=np.bool)
        q = []
        q.append(center[z])
        found = 0

        while len(q) > 0:
            p = q.pop()
            can_visit[p] = False
            if graph[p]:
                found += 1

            for p1 in adjacent_points(p):
                if can_visit[p1] and (zones[p1] == -1 or zones[p1] == z):
                    q.append(p1)

        result[z] = found
    return result


def fill_zones(graph):
    result = np.full((size, size), -1, dtype=np.int8)
    zone_center = []
    zone_count = np.full((size), 0, dtype=np.int8)
    zone_accessible = np.full((size), 0, dtype=np.int32)

    points_empty = []
    for x in range(size):
        for y in range(size):
            points_empty.append((x, y))
    random.shuffle(points_empty)

    empty_zone = 0
    while empty_zone < size:
        p = points_empty.pop(0)

        if graph[p] == True and result[p] == -1:
            result[p] = empty_zone
            zone_count[empty_zone] += 1
            zone_center.append(p)
            empty_zone += 1
        else:
            points_empty.append(p)

    target_zone = random.choice(target_zones(zone_count, zone_accessible))

    loop_count = 0
    while len(points_empty) > 0:
        p = points_empty.pop(0)

        if target_zone in adjacent_zones(p, result):
            result[p] = target_zone
            acc_new = update_accessible(
                graph, result, zone_accessible, zone_center)
            if min(acc_new) >= 2:
                if graph[p]:
                    zone_count[target_zone] += 1
                tz = target_zones(zone_count, zone_accessible)
                if len(tz) == 0:
                    break
                target_zone = random.choice(tz)
                zone_accessible = acc_new
                loop_count = 0
            else:
                result[p] = -1
                points_empty.append(p)
                loop_count += 1
        else:
            points_empty.append(p)
            loop_count += 1

        if loop_count > len(points_empty):
            return np.array([])

    while len(points_empty) > 0:
        p = points_empty.pop(0)

        adj = adjacent_zones(p, result)
        if len(adj) > 0:
            result[p] = random.choice(adj)
        else:
            points_empty.append(p)

    return result


def solve(zones, x, graph):
    if x == size:
        zone_count = np.full((size), 0, dtype=np.int8)
        for xpos in range(size):
            for ypos in range(size):
                if graph[xpos, ypos]:
                    zone_count[zones[xpos, ypos]] += 1
        if np.all(zone_count == 2):
            output(graph, zones)
            return 1
        else:
            return 0

    rows = valid_rows(x, graph)
    result = 0

    for a in rows:
        for b in rows:
            if a > b and a - b > 1:

                graph_new = np.copy(graph)
                graph_new[x, a] = True
                graph_new[x, b] = True

                result += solve(zones, x+1, graph_new)

    return result


zones = np.array([])
while len(zones) == 0:
    graph = np.full((size, size), 0, dtype=np.bool)
    graph = fill(0, graph)
    for i in range(100):
        zones = fill_zones(graph)
        if len(zones) != 0:
            break

output(graph, zones)
print(solve(zones, 0, np.full((size, size), 0, dtype=np.bool)))
