import functions
import networkx as nx
from itertools import combinations
import sys

def run(G, s, b, t):
    # Tactics
    T1_self_edge = True
    T2_upperbound = True

    G_prime = G.copy()
    A = set()  # the set of (increased edge, delta) pair
    
    # calculate_s_core 에는 coreness 재선언이 없기 때문에 선언 후 시작
    coreness = {}
    s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)  # Calculate s-core and coreness
    sum = 0  # the budget used
    

    # self_edge theorem 을 사용하면 s-core 는 후보에서 영원히 제거된다.
    if T1_self_edge:
        non_s_core, s_cand = self_edge_pruning(G_prime) # pruned set

    if T2_upperbound:
        upperbound = {}

    while sum < b:
        '''
        1. Candidate 만드는 과정
        - self_edge O
            s-core 를 아예 다 뺀 candiate_nodes 집합을 만든다.
        - self_edge X
            non-s-core 와 s-core 를 잘 배합해서 candidate_edges 집합을 만든다.
        '''
        if T1_self_edge:
            # 함수로 바꾸자.
            ############# 1. Candidate 만드는 과정 ##################

            # candidate_nodes 집합
            candidate_nodes = []
            for u in non_s_core:
                if not G_prime.nodes[u]['label']:
                    candidate_nodes.append(u)
                    # upperbound 계산
                    if T2_upperbound:
                        upperbound[u] = functions.Upperbound(G_prime, u, coreness, s)
            
            # upperbound 전략을 사용한다면 upperbound 기준으로 정렬해야 한다.
            if T2_upperbound:
                candidate_nodes.sort(key = lambda x : -upperbound[x])

            #########################################################
            
            # initial setting
            best_edge = None; best_delta = 0  # edge and delta with maximal FR
            most_FR = 0  # maximal follower rate
            
            if T2_upperbound:
                c = len(candidate_nodes)
                for i in range(c):
                    u = candidate_nodes[i]
                    if most_FR > functions.U_single(u, upperbound) * 2:
                        break
                    for j in range(i, c):
                        v = candidate_nodes[j]
                        if most_FR >= functions.U_single(u, upperbound) + functions.U_single(v, upperbound):
                            break
                        if most_FR >= functions.U_double(u, v, upperbound, coreness, G_prime):
                            continue
                        else:
                            e = (u, v)
                            delta_e = functions.computeDelta(G_prime, s, e, t, coreness)

                            if delta_e > 0 and sum + delta_e <= b:
                                # calculate the follower
                                followers = functions.FindFollowers(e, delta_e, G_prime, s, coreness)
                                FR = len(followers) / delta_e  # follower rate

                                # renew the maximum value
                                if FR > most_FR:
                                    best_edge = e
                                    best_delta = delta_e
                                    most_FR = FR
            else:
                c = len(candidate_nodes)
                for i in range(c):
                    u = candidate_nodes[i]
                    for j in range(i, c):
                        v = candidate_nodes[j]
                        e = (u, v)

                        delta_e = functions.computeDelta(G_prime, s, e, t, coreness)

                        if delta_e > 0 and sum + delta_e <= b:
                            # calculate the follower
                            followers = functions.FindFollowers(e, delta_e, G_prime, s, coreness)
                            FR = len(followers) / delta_e  # follower rate

                            # renew the maximum value
                            if FR > most_FR:
                                best_edge = e
                                best_delta = delta_e
                                most_FR = FR
                    
        else:

            candidate_edges = []

            # Filter candidate edges
            non_s_core = []
            s_core = []
            for n, d in G_prime.nodes(data=True):
                if not d['label']:
                    non_s_core.append(n)
                else:
                    s_core.append(n)
                
                if T2_upperbound:
                    upperbound[n] = functions.Upperbound(G_prime, n, coreness, s)

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

            # initial setting
            best_edge = None; best_delta = 0  # edge and delta with maximal FR
            most_FR = 0  # maximal follower rate

            if T2_upperbound:
                for (u,v) in candidate_edges:
                    if most_FR >= functions.U_single(u, upperbound) + functions.U_single(v, upperbound):
                        break
                    if most_FR >= functions.U_double(u, v, upperbound, coreness, G_prime):
                        continue
                    else:
                        e = (u, v)
                        delta_e = functions.computeDelta(G_prime, s, e, t, coreness)

                        if delta_e > 0 and sum + delta_e <= b:
                            # calculate the follower
                            followers = functions.FindFollowers(e, delta_e, G_prime, s, coreness)
                            FR = len(followers) / delta_e  # follower rate

                            # renew the maximum value
                            if FR > most_FR:
                                best_edge = e
                                best_delta = delta_e
                                most_FR = FR
            else:
                for (u,v) in candidate_edges:
                    e = (u, v)
                    delta_e = functions.computeDelta(G_prime, s, e, t, coreness)

                    if delta_e > 0 and sum + delta_e <= b:
                        # calculate the follower
                        followers = functions.FindFollowers(e, delta_e, G_prime, s, coreness)
                        FR = len(followers) / delta_e  # follower rate

                        # renew the maximum value
                        if FR > most_FR:
                            best_edge = e
                            best_delta = delta_e
                            most_FR = FR
                        

        # debugging 3
        # print()
        # print(best_edge)
        # print(best_delta)
        # print(most_FR)

        # Update G_prime
        if best_edge is not None:
            u, v = best_edge
            if u == v:
                v = s_cand

            # add edge weight
            if G_prime.has_edge(u, v):
                G_prime[u][v]['weight'] += best_delta
            else:
                G_prime.add_edge(u, v, weight=best_delta)

            # add budget
            sum += best_delta
            # add answer

            A.add(((u, v), best_delta))
            # calculate s-core again
            coreness = {}
            s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)
            
            # debugging 4
            # print(s_core_num)
        else:
            # print("no more")
            break
    print(s_core_num)
    return A


def self_edge_pruning(G):
    non_s_core = []
    s_cand = None
    for n, d in G.nodes(data=True):
        if not d['label']:
            non_s_core.append(n)
        else:
            if s_cand is None:
                s_cand = n
    
    if s_cand is None:
        print("No node in s-core. Change s value")
        sys.exit(1)
    
    return non_s_core, s_cand