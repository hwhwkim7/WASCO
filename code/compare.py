import functions
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
import random

def run(G, s, b, t, edge_Tactic, delta_Tactic):

    G_prime = G.copy()
    A = set()  # the set of (increased edge, delta) pair
    
    coreness = {}
    s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)  # Calculate s-core and coreness
    sum = 0  # the budget used

    # debugging for Upperbound
    # for i in G_prime.nodes:
    #     if not G_prime.nodes[i]['label']:
    #         print(i, functions.Upperbound(G_prime, i, coreness))

    # debugging 1
    # print(s_core_num)
    # print(coreness)
    cnt = 0

    while sum < b:
        
        # Filter candidate edges
        non_s_core = []
        s_core = []
        for n, d in G_prime.nodes(data=True):
            if not d['label']:
                non_s_core.append(n)
            else:
                s_core.append(n)

        # 후보 엣지 생성
        candidate_edges = []
        # 1) non-core 간
        for i in range(len(non_s_core)):
            for j in range(i+1, len(non_s_core)):
                candidate_edges.append((non_s_core[i], non_s_core[j]))
        # 2) non-core <-> s-core
        for u in non_s_core:
            for v in s_core:
                candidate_edges.append((u, v))
        
        if len(candidate_edges) == 0:
            break
        
        # debugging 2
        # print(candidate_edges)

        if edge_Tactic == 'random':
            best_edge = random.choice(candidate_edges)
            if delta_Tactic == 'compute':
                best_delta = functions.computeDelta(G_prime, s, best_edge, t, coreness)
            elif delta_Tactic == 'SmW':
                u, v = best_edge
                if G_prime.has_edge(u, v):
                    best_delta = s - G_prime[u][v]['weight']
                else:
                    best_delta = s
        else:
            if edge_Tactic == 'degree':
                score_function = score_degree
            if edge_Tactic == 'high_degree':
                score_function = score_high_layer_degree
            if edge_Tactic == 'weight_sum':
                score_function = score_weight_sum
            if edge_Tactic == 'high_weight_sum':
                score_function = score_high_layer_weight

            candidate_edges.sort(
                key=lambda e: score_function(G_prime, e[0], e[1], coreness, s),
                reverse=True
            )
            # for e in candidate_edges:
            #     print(e, score_function(G_prime, e[0], e[1], coreness, s))
            
            best_edge = candidate_edges[cnt]
            if delta_Tactic == 'compute':
                best_delta = functions.computeDelta(G_prime, s, best_edge, t, coreness)
            elif delta_Tactic == 'SmW':
                u, v = best_edge
                if G_prime.has_edge(u, v):
                    best_delta = s - G_prime[u][v]['weight']
                else:
                    best_delta = s
        if best_delta > b:
            cnt += 1
            continue

        followers = functions.FindFollowers(best_edge, best_delta, G_prime, s, coreness)
        max_FR = len(followers) / best_delta  # follower rate
        most_follower = len(followers)

        # debugging 3
        # print()
        # print(best_edge)
        # print(best_delta)
        # print(max_FR)

        # Update G_prime
        if best_edge is not None:
            u, v = best_edge

            # add edge weight
            if G_prime.has_edge(u, v):
                G_prime[u][v]['weight'] += best_delta
            else:
                G_prime.add_edge(u, v, weight=best_delta)

            # add budget
            sum += best_delta
            
            # calculate s-core again
            coreness = {}
            s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)
            
            # add answer
            A.add(((u, v), best_delta, max_FR, most_follower))
            cnt = 0
            
            # debugging 4
            # print(s_core_num)
        else:
            # print("no more")
            break
    return A


# 1) 단순 degree 합
def score_degree(G, u, v, coreness, s):
    return G.degree(u) + G.degree(v)

# 2) 단순 weight-sum 합
def score_weight_sum(G, u, v, coreness, s):
    ws_u = sum(data.get('weight',1) for _, _, data in G.edges(u, data=True))
    ws_v = sum(data.get('weight',1) for _, _, data in G.edges(v, data=True))
    return ws_u + ws_v

# 3) “높은 layer” 로 향하는 degree 합
def score_high_layer_degree(G, u, v, coreness, s):
    # u 쪽
    deg_u = sum(1 for w in G.neighbors(u) if coreness.get(w, (s, 0)) > coreness.get(u, (s, 0)))
    # v 쪽
    deg_v = sum(1 for w in G.neighbors(v) if coreness.get(w, (s, 0)) > coreness.get(v, (s, 0)))
    return deg_u + deg_v

# 4) “높은 layer” 로 향하는 weight-sum 합
def score_high_layer_weight(G, u, v, coreness, s):
    ws_u = sum(data.get('weight',1)
               for _, w, data in G.edges(u, data=True)
               if coreness.get(w, (s, 0)) > coreness.get(u, (s, 0)))
    ws_v = sum(data.get('weight',1)
               for _, w, data in G.edges(v, data=True)
               if coreness.get(w, (s, 0)) > coreness.get(v, (s, 0)))
    return ws_u + ws_v