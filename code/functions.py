import heapq
from collections import deque

def calculate_s_core(G, s):
    weight_sum = {node: sum(G[u][v]['weight'] for u, v in G.edges(node)) for node in G.nodes}
    for node in G.nodes:
        G.nodes[node]['label'] = True
    s_core_num = len(G.nodes)
    coreness = {}

    # make heap with the key : weight sum
    heap = [(weight, node) for node, weight in weight_sum.items()]
    heapq.heapify(heap)

    # Calculating coreness L(u) = (c(u), l(u))
    # this loop for c(u)
    while heap:
        current_core, node = heap[0]
        # doesn't have to consider node with having coreness larger than s
        if current_core >= s:
            break
        
        # this loop for l(u)
        layer = 0
        while heap[0][0] <= current_core:
            layer += 1
            temp = []
            # The node deleted in this loop has coreness "(current_core, layer)"
            while heap[0][0] <= current_core:
                weight, node = heapq.heappop(heap)

                if node in coreness:
                    continue

                coreness[node] = (current_core, layer)

                for neighbor in G.neighbors(node):
                    weight_sum[neighbor] -= G[node][neighbor]['weight']
                    temp.append((weight_sum[neighbor], neighbor))

                G.nodes[node]['label'] = False
                s_core_num -= 1
            
            # renew the key of neighbors (quite ineffective?)
            for components in temp:
                heapq.heappush(heap, components)

    # debugging
    # print(coreness)
    return s_core_num, coreness


# not considering T yet
def computeDelta(G, s, e, t, coreness):
    u, v = e
    if u in coreness:
        c_u = coreness[u][0]
    else:
        c_u = s
    if v in coreness:
        c_v = coreness[v][0]
    else:
        c_v = s
    
    return s - min(c_u, c_v)


def FindFollowers(e, delta_e, G, s, coreness):
    F = set()

    # assuming the case of edge anchored
    u, v = e
    if G.has_edge(u, v):
        edge_added = False
        G[u][v]['weight'] += delta_e
    else:
        edge_added = True
        G.add_edge(u, v, weight=delta_e)

    # Initialize priority queue
    PQ = []
    index_PQ = 0
    for node in e:
        if not G.nodes[node]['label']:
            heapq.heappush(PQ, (coreness[node], index_PQ, node))
            index_PQ += 1

    sigma_plus = {}
    while PQ:
        _, _, x = heapq.heappop(PQ)

        # σ⁺(x)
        sigma_plus[x] = sum(
            G[x][neighbor]['weight']
            for neighbor in G.neighbors(x)
            if G.nodes[neighbor]['label'] or coreness[neighbor] > coreness[x] or neighbor in F or neighbor in [element[2] for element in PQ]
        )

        # for debugging
        # sigma_plus[x] = 0
        # for neighbor in G.neighbors(x):
        #     if G.nodes[neighbor]['label'] or coreness[neighbor] > coreness[x] or neighbor in F or neighbor in [element[2] for element in PQ]:
        #         # if e == (11, 12):
        #         #     print(neighbor)
        #         sigma_plus[x] += G[x][neighbor]['weight']
        # print(x, sigma_plus[x])

        # σ⁺(x) ≥ s
        if sigma_plus[x] >= s:
            F.add(x)
            for y in G.neighbors(x):
                if not G.nodes[y]['label'] and y not in F and coreness[y] > coreness[x]:
                    heapq.heappush(PQ, (coreness[y], index_PQ, y))
                    index_PQ += 1

        # σ⁺(x) < s
        else:
            Q = deque()
            Q.append(x)
            while Q:
                y = Q.popleft()
                if y in F:
                    F.remove(y)

                for z in G.neighbors(y):
                    if z in F:
                        # # update σ⁺(z)
                        sigma_plus[z] -= G[y][z]['weight']

                        if sigma_plus[z] < s:
                            Q.append(z)

    # roll back the assumtion
    if edge_added:
        G.remove_edge(u, v)
    else:
        G[u][v]['weight'] -= delta_e

    return F


def Upperbound(G, u, coreness, s):
    Q = deque()
    visited = [False] * (len(G.nodes) + 1)

    count = 1
    Q.append(u)
    visited[u] = True

    while Q:
        v = Q.popleft()
        for w in G.neighbors(v):
            if not G.nodes[w]['label'] and coreness[v] < coreness[w]:
                if not visited[w]:
                    count += 1
                    Q.append(w)
                    visited[w] = True

    return count / (s - coreness[u][0])

def U(u, upperbound):
    return upperbound[u]
def U(u, v, upperbound):
    return upperbound[u] + upperbound[v]