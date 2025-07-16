import functions
import time

def make_candidate_nodes(G_prime, nodes, coreness, s, T2_upperbound, upperbound, UT):
    '''
    self_edge 전략을 사용한다면 s-core 는 완벽히 무시가 가능하다. 
    그렇기에 non-s-core 를 candidate_nodes 로 저장하여 이 노드들 간의 조합만 확인한다.
    upperbound 전략을 사용한다면 pruning 을 위해 candiate_nodes 를 upperbound 기준 정렬해둔다.
    '''
    # candidate_nodes 집합
    candidate_nodes = []
    for u in nodes:
        if not G_prime.nodes[u]['label']:
            candidate_nodes.append(u)
            # upperbound 계산
            if T2_upperbound:
                temp_start = time.time()
                upperbound[u] = functions.Upperbound(G_prime, u, coreness, s)
                temp_end = time.time()
                UT += temp_end - temp_start
    
    # upperbound 전략을 사용한다면 upperbound 기준으로 정렬해야 한다.
    if T2_upperbound:
        candidate_nodes.sort(key = lambda x : -upperbound[x])
    
    return candidate_nodes

def iteration_nodes_upperbound(G_prime, candidate_nodes, coreness, s, b, t, upperbound, spent, FT):
    '''
    self_edge, upperbound 전략을 모두 사용할 때의 iteration.
    '''
    # initial setting
    best_edge = None; best_delta = 0  # edge and delta with maximal FR
    most_FR = 0  # maximal follower rate

    c = len(candidate_nodes)
    for i in range(c):
        u = candidate_nodes[i]
        if most_FR > functions.U_single(u, upperbound) * 2:
            break
        for j in range(i, c):
            v = candidate_nodes[j]
            if most_FR >= functions.U_single(u, upperbound) + functions.U_single(v, upperbound):
                break
            if most_FR >= functions.U_double(u, v, upperbound, coreness, G_prime, s):
                continue
            else:
                e = (u, v)
                delta_e = functions.computeDelta(G_prime, s, e, t, coreness)

                if delta_e > 0 and spent + delta_e <= b:
                    # calculate the follower
                    temp_start = time.time()
                    followers = functions.FindFollowers(e, delta_e, G_prime, s, coreness)
                    temp_end = time.time()
                    FT += temp_end - temp_start

                    FR = len(followers) / delta_e  # follower rate

                    # renew the maximum value
                    if FR > most_FR:
                        best_edge = e
                        best_delta = delta_e
                        most_FR = FR
    return best_edge, best_delta, most_FR

def iteration_nodes_no_upperbound(G_prime, candidate_nodes, coreness, s, b, t, spent, FT):
    '''
    self_edge 전략만 사용할 때의 iteration. 
    upperbound 를 이용한 pruning 은 없다.
    '''
    # initial setting
    best_edge = None; best_delta = 0  # edge and delta with maximal FR
    most_FR = 0  # maximal follower rate
    c = len(candidate_nodes)
    for i in range(c):
        u = candidate_nodes[i]
        for j in range(i, c):
            v = candidate_nodes[j]
            e = (u, v)

            delta_e = functions.computeDelta(G_prime, s, e, t, coreness)

            if delta_e > 0 and spent + delta_e <= b:
                # calculate the follower
                temp_start = time.time()
                followers = functions.FindFollowers(e, delta_e, G_prime, s, coreness)
                temp_end = time.time()
                FT += temp_end - temp_start

                FR = len(followers) / delta_e  # follower rate

                # renew the maximum value
                if FR > most_FR:
                    best_edge = e
                    best_delta = delta_e
                    most_FR = FR
    return best_edge, best_delta, most_FR


def make_candidate_edges(G_prime, nodes, coreness, s, T2_upperbound, upperbound, UT):
    '''
    self_edge 전략을 사용하지 않기에 s-core 와의 연결도 고려해야 한다.
    그렇기에 non-s-core끼리, non-s-core 와 s-core 간의 연결, 이 두가지의 edge 들이 candidate_edges 가 된다.
    (x, y) 에서 x의 upperbound가 무조건 y의 upperbound 보다 크게 하기 위해 non-s-core 를 정렬 후 진행한다.
    이후 마지막에 upperbound 기준 정렬
    '''
    candidate_edges = []

    # Filter candidate edges
    non_s_core = []
    s_core = []
    for n in nodes:
        if not G_prime.nodes[n]['label']:
            non_s_core.append(n)
        else:
            s_core.append(n)
        
        # 이후 작업을 위해 전체에 대해 upperbound 를 정의하지만 줄일 수 있을듯. 
        # s-core 의 upperbound 는 무조건 non-s-core 의 upperbound보다 작다는 사실을 이용하면 되지 않을까.
        if T2_upperbound:
            temp_start = time.time()
            upperbound[n] = functions.Upperbound(G_prime, n, coreness, s)
            temp_end = time.time()
            UT += temp_end - temp_start

    # upperbound pruning 위해 미리 정렬
    if T2_upperbound:
        non_s_core.sort(key = lambda x : -upperbound[x])

    # Intra non-core
    non_len = len(non_s_core)
    for i in range(non_len):
        u = non_s_core[i]
        for j in range(i+1, non_len):
            v = non_s_core[j]
            candidate_edges.append((u, v))

    # core <-> non-core
    for u in non_s_core:
        for v in s_core:
            candidate_edges.append((u, v))

    if T2_upperbound:
        candidate_edges.sort(key = lambda x : (-upperbound[x[0]], -upperbound[x[1]]))   # s-core 는 upperbound 가 선언이 안 되어 있음

    return candidate_edges

def iteration_edges_upperbound(G_prime, candidate_edges, coreness, s, b, t, upperbound, spent, FT):
    '''
    self_edge 전략 없이 upperbound 전략만 사용할 때의 iteration. 
    '''
    # initial setting
    best_edge = None; best_delta = 0  # edge and delta with maximal FR
    most_FR = 0  # maximal follower rate

    for (u,v) in candidate_edges:
        if most_FR >= functions.U_single(u, upperbound) + functions.U_single(v, upperbound):
            break
        if most_FR >= functions.U_double(u, v, upperbound, coreness, G_prime, s):
            continue
        else:
            e = (u, v)
            delta_e = functions.computeDelta(G_prime, s, e, t, coreness)

            if delta_e > 0 and spent + delta_e <= b:
                # calculate the follower
                temp_start = time.time()
                followers = functions.FindFollowers(e, delta_e, G_prime, s, coreness)
                temp_end = time.time()
                FT += temp_end - temp_start

                FR = len(followers) / delta_e  # follower rate

                # renew the maximum value
                if FR > most_FR:
                    best_edge = e
                    best_delta = delta_e
                    most_FR = FR
    return best_edge, best_delta, most_FR

def iteration_edges_no_upperbound(G_prime, candidate_edges, coreness, s, b, t, spent, FT):
    '''
    naive algorithm.
    '''
    # initial setting
    best_edge = None; best_delta = 0  # edge and delta with maximal FR
    most_FR = 0  # maximal follower rate

    for (u,v) in candidate_edges:
        e = (u, v)
        delta_e = functions.computeDelta(G_prime, s, e, t, coreness)

        if delta_e > 0 and spent + delta_e <= b:
            # calculate the follower
            temp_start = time.time()
            followers = functions.FindFollowers(e, delta_e, G_prime, s, coreness)
            temp_end = time.time()
            FT += temp_end - temp_start

            FR = len(followers) / delta_e  # follower rate

            # renew the maximum value
            if FR > most_FR:
                best_edge = e
                best_delta = delta_e
                most_FR = FR
    return best_edge, best_delta, most_FR