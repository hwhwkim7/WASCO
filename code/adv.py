import functions
import networkx as nx
from itertools import combinations

def run(G, s, b, t):

    G_prime = G.copy()
    A = set()  # the set of (increased edge, delta) pair
    
    coreness = {}
    s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)  # Calculate s-core and coreness
    print(s_core_num)
    sum = 0  # the budget used
    
    # non-s-core set - pruned set
    non_s_core = []
    s_cand = None
    for n, d in G_prime.nodes(data=True):
        if not d['label']:
            non_s_core.append(n)
        else:
            if s_cand is None:
                s_cand = n
    
    if s_cand is None:
        print("No node in s-core. Change s value")
        return

    upperbound = {}

    while sum < b:
        # Compute upperbound for only candidate nodes
        candidate_nodes = []
        for u in non_s_core:
            if not G_prime.nodes[u]['label']:
                upperbound[u] = functions.Upperbound(G_prime, u, coreness, s)
                candidate_nodes.append(u)
        # print(len(upperbound))

        candidate_nodes.sort(key = lambda x : -upperbound[x])
        
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

            # 고치기 s_cand 로
            A.add(((u, v), best_delta, most_FR))
            # calculate s-core again
            coreness = {}
            s_core_num = functions.calculate_s_core(G_prime, G_prime.nodes, s, coreness)
            
            # debugging 4
            # print(s_core_num)
        else:
            # print("no more")
            break
    # print(s_core_num)
    return A