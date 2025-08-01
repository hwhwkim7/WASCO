import functions
import time
import csv
import os

def make_candidate_nodes(G_prime, nodes, coreness, s, b, T2_upperbound, upperbound, UT):
    '''
    self_edge 전략을 사용한다면 s-core 는 완벽히 무시가 가능하다. 
    그렇기에 non-s-core 를 candidate_nodes 로 저장하여 이 노드들 간의 조합만 확인한다.
    upperbound 전략을 사용한다면 pruning 을 위해 candiate_nodes 를 upperbound 기준 정렬해둔다.
    '''
    # candidate_nodes 집합
    candidate_nodes = []
    for u in nodes:
        # 잔여 budget 을 넘어서는 delta 가 필요하다면 pruning
        if not G_prime.nodes[u]['label'] and s - coreness[u][0] <= b:
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

def iteration_nodes_upperbound(G_prime, candidate_nodes, coreness, s, b, T1_self_edge, t, upperbound, spent, FT, s_cand):
    '''
    self_edge, upperbound 전략을 모두 사용할 때의 iteration.
    '''
    # initial setting
    best_edge = None; best_delta = 0  # edge and delta with maximal FR
    most_FR = 0; most_follower = 0  # maximal follower rate

    c = len(candidate_nodes)
    for i in range(c):
        u = candidate_nodes[i]
        # TODO 크거나 같다
        if most_FR >= functions.U_single(u, upperbound) * 2:
            break
        for j in range(i if T1_self_edge else i+1, c):
            v = candidate_nodes[j]
            if most_FR >= functions.U_single(u, upperbound) + functions.U_single(v, upperbound):
                break
            if most_FR >= functions.U_double(u, v, upperbound, coreness, G_prime, s):
                continue
            else:
                e = (u, v)
                if u == v:
                    e = (u, s_cand)

                delta_e = functions.computeDelta(G_prime, s, e, t, coreness)

                if delta_e > 0 and spent + delta_e <= b:
                    # calculate the follower
                    temp_start = time.time()
                    followers = functions.FindFollowers(e, delta_e, G_prime, s, coreness)
                    temp_end = time.time()
                    FT += temp_end - temp_start

                    FR = len(followers) / delta_e  # follower rate

                    # renew the maximum value
                    # Total order 로 비교하기 TODO
                    if FR > most_FR or (FR == most_FR and best_edge is not None and e < best_edge):
                        best_edge = e
                        best_delta = delta_e
                        most_FR = FR
                        most_follower = len(followers)
    return best_edge, best_delta, most_FR, most_follower

def iteration_nodes_no_upperbound(G_prime, candidate_nodes, coreness, s, b, t, spent, FT, s_cand):
    '''
    self_edge 전략만 사용할 때의 iteration. 
    upperbound 를 이용한 pruning 은 없다.
    '''
    # initial setting
    best_edge = None; best_delta = 0  # edge and delta with maximal FR
    most_FR = 0; most_follower = 0  # maximal follower rate
    c = len(candidate_nodes)
    for i in range(c):
        u = candidate_nodes[i]
        for j in range(i, c):
            v = candidate_nodes[j]
            e = (u, v)
            if u == v:
                e = (u, s_cand)

            delta_e = functions.computeDelta(G_prime, s, e, t, coreness)

            if delta_e > 0 and spent + delta_e <= b:
                # calculate the follower
                temp_start = time.time()
                followers = functions.FindFollowers(e, delta_e, G_prime, s, coreness)
                temp_end = time.time()
                FT += temp_end - temp_start

                FR = len(followers) / delta_e  # follower rate

                # renew the maximum value
                if FR > most_FR or (FR == most_FR and best_edge is not None and e < best_edge):
                    best_edge = e
                    best_delta = delta_e
                    most_FR = FR
                    most_follower = len(followers)
    return best_edge, best_delta, most_FR, most_follower


def make_candidate_edges(G_prime, nodes, coreness, s, b, T2_upperbound, upperbound, UT):
    '''
    upperbound 전략을 사용하지 않을 때.
    self_edge 전략을 사용하지 않기에 s-core 와의 연결도 고려해야 한다.
    그렇기에 non-s-core끼리, non-s-core 와 s-core 간의 연결, 이 두가지의 edge 들이 candidate_edges 가 된다.
    '''
    candidate_edges = []

    non_s_core = []
    s_core = []
    for u in nodes:
        if s - coreness.get(u, (s, 0))[0] > b:
            continue
        if not G_prime.nodes[u]['label']:
            non_s_core.append(u)
        else:
            s_core.append(u)

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

    return candidate_edges

def make_candidate_nodes_v2(G_prime, nodes, coreness, s, b, T2_upperbound, upperbound, UT):
    '''
    upperbound 전략을 사용할 때
    self_edge 전략을 사용하지 않지만 upperbound 를 사용하기 위해 candidate_nodes 집합을 만든다. 
    s-core 의 upperbound 는 0으로 설정한 후 정렬.
    '''
    candidate_nodes = []

    for u in nodes:
        # 잔여 budget 을 넘어서는 delta 가 필요하다면 pruning
        if s - coreness.get(u, (s, 0))[0] > b:
            continue

        if not G_prime.nodes[u]['label']:
            temp_start = time.time()
            upperbound[u] = functions.Upperbound(G_prime, u, coreness, s)
            temp_end = time.time()
            UT += temp_end - temp_start
        else:
            if T2_upperbound:
                upperbound[u] = 0
        candidate_nodes.append(u)
    
    candidate_nodes.sort(key = lambda x : -upperbound[x])

    return candidate_nodes

def iteration_edges_no_upperbound(G_prime, candidate_edges, coreness, s, b, t, spent, FT):
    '''
    naive algorithm.
    '''
    # initial setting
    best_edge = None; best_delta = 0  # edge and delta with maximal FR
    most_FR = 0; most_follower = 0  # maximal follower rate

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
            if FR > most_FR or (FR == most_FR and best_edge is not None and e < best_edge):
                best_edge = e
                best_delta = delta_e
                most_FR = FR
                most_follower = len(followers)
    return best_edge, best_delta, most_FR, most_follower

def save_result_to_csv(A, s_core_num, total_time, memory, args):
    write_header = not os.path.exists(args.output_path)
    data = args.network.split('/')[3]

    with open(args.output_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["data", "s", "b", "tactics", "num_s_core", "num_anchored_edges", "iter", "delta", "num_follower", "total_time", "memory"])
        for idx, (_, delta, _, num_follower) in enumerate(A, start=1):
            writer.writerow(
                [data, args.s, args.b, args.tactics, s_core_num, len(A), idx, delta, num_follower, total_time, memory])
    print(f"Saved results to {data, args.s, args.b, args.tactics}")
