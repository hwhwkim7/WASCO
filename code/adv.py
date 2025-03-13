import functions
import networkx as nx
from itertools import combinations

def run(G, s, b, t):

    G_prime = G.copy()
    A = set()  # the set of (increased edge, delta) pair
    
    s_core_num, coreness = functions.calculate_s_core(G_prime, s)  # Calculate s-core and coreness
    sum = 0  # the budget used
    
    while sum < b:
        # Compute upperbounds
        upperbound = [-1] * (len(G_prime.nodes) + 1)
        for u in G_prime.nodes:
            if not G_prime.nodes[u]['label']:
                upperbound[u] = functions.Upperbound(G_prime, u, coreness, s)

        # Filter candidate_edges
        candidate_nodes = [u for u in G_prime.nodes if not G_prime.nodes[u]['label']]
        candidate_nodes.sort(key = lambda x : -upperbound[x])
        
        # initial setting
        F = set()
        best_edge = None; best_delta = 0  # edge and delta with maximal FR
        most_FR = 0  # maximal follower rate
        
        c = len(candidate_nodes)
        for i in range(c):
            u = candidate_nodes[i]
            if most_FR > functions.U(u, u, upperbound):
                break
            for j in range(i+1, c):
                v = candidate_nodes[j]
                if most_FR >= functions.U(u, v, upperbound):
                    break
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
        print()
        print(best_edge)
        print(best_delta)

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
            # add answer
            A.add((best_edge, best_delta))
            # calculate s-core again
            s_core_num, coreness = functions.calculate_s_core(G_prime, s)
            
            # debugging 4
            # print(s_core_num)
        else:
            # print("no more")
            break

    return A