import heapq
from heapdict import heapdict
from collections import deque

def calculate_s_core(G, nodes, s, coreness):
    weight_sum = {node: sum(G[u][v]['weight'] for u, v in G.edges(node)) for node in nodes}
    for node in nodes:
        G.nodes[node]['label'] = True
    s_core_num = len(nodes)

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
        while heap and heap[0][0] <= current_core:
            layer += 1
            temp = {}
            # The node deleted in this loop has coreness "(current_core, layer)"
            while heap and heap[0][0] <= current_core:
                weight, node = heapq.heappop(heap)

                if not G.nodes[node]['label']:
                    continue
                
                coreness[node] = (current_core, layer)

                for neighbor in G.neighbors(node):
                    if not G.nodes[neighbor]['label']:
                        continue
                    # reuse 에서 s-core 에 있는 노드들을 넣지 않기 때문에 기존 s-core 가 저장되어 있지 않음
                    # 즉 기존 s-core 로 향하는 neighbor 들을 차단해줘야 함. ->overhead?
                    if neighbor not in nodes:
                        continue
                    weight_sum[neighbor] -= G[node][neighbor]['weight']
                    temp[neighbor] = weight_sum[neighbor]

                G.nodes[node]['label'] = False
                s_core_num -= 1
            
            # renew the key of neighbors (quite ineffective?)
            for (node, w) in temp.items():
                heapq.heappush(heap, (w, node))

    # debugging
    return s_core_num

def calculate_s_core_(G, nodes, s, coreness):
    weight_sum = {node: sum(G[u][v]['weight'] for u, v in G.edges(node)) for node in nodes}
    for node in nodes:
        G.nodes[node]['label'] = True
    s_core_num = len(nodes)

    # ─── heapdict로 교체 ─────────────────────────────────────────
    hd = heapdict()
    for node, w in weight_sum.items():
        hd[node] = w

    # Calculating coreness L(u) = (c(u), l(u))
    # this loop for c(u)
    while hd:
        node_min, current_core = hd.peekitem()  # 최소값 노드·우선순위 확인
        # doesn't have to consider node with having coreness larger than s
        if current_core >= s:
            break
        
        # this loop for l(u)
        layer = 0
        # 남아 있는 노드 중에서도 우선순위 ≤ current_core인 동안
        while hd and hd.peekitem()[1] <= current_core:
            layer += 1
            temp = {}

            # coreness가 (current_core, layer)인 노드들 처리
            while hd and hd.peekitem()[1] <= current_core:
                node, weight = hd.popitem()  # (node, priority)
                if not G.nodes[node]['label']:
                    continue

                coreness[node] = (current_core, layer)

                for nbr in G.neighbors(node):
                    if not G.nodes[nbr]['label']:
                        continue
                    weight_sum[nbr] -= G[node][nbr]['weight']
                    temp[nbr] = weight_sum[nbr]

                G.nodes[node]['label'] = False
                s_core_num -= 1

            # 이웃 우선순위 갱신(decrease-key)
            for nbr, new_w in temp.items():
                hd[nbr] = new_w
    # ─────────────────────────────────────────────────────────────
    return s_core_num


# not considering T yet
def computeDelta(G, s, e, t, coreness):
    u, v = e
    if not G.nodes[u]['label']:
        c_u = coreness[u][0]
    else:
        c_u = s
    if not G.nodes[v]['label']:
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
    if u == v:
        heapq.heappush(PQ, (coreness[u], index_PQ, u))
        index_PQ += 1
    else:
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
                    if y == u or y == v:
                        # Early termination
                        if edge_added:
                            G.remove_edge(u, v)
                        else:
                            G[u][v]['weight'] -= delta_e

                        return {}

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
    if G.nodes[u]['label']:
        return 0
    
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

def U_single(u, upperbound):
    return upperbound[u]

def U_double(u, v, upperbound, coreness, G, s):
    # 이걸 넣어도 될까. self_edge X upperbound O 인 경우에 s-core 의 coreness 도 고려하게 된다
    if G.nodes[v]['label']:
        cv = (s, 0)
    else:
        cv = coreness[v]
    
    if (G.has_edge(u, v) and coreness[u] < cv) or u == v:
        return upperbound[u]
    else:
        return upperbound[u] + upperbound[v]