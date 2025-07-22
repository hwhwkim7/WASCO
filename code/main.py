import argparse
import networkx as nx
import time

import naive
import adv
import adv_reuse
import experiment, experiment_reuse
import EKC
import exact
import compare

parser = argparse.ArgumentParser()
parser.add_argument('--s', type=int, default=5,
                    help='user parameter s')
parser.add_argument('--b', type=int, default=10,
                    help='budget b')
parser.add_argument('--t', type=str, default='',
                    help='a folder name for bound function') # 우선 bound가 없다고 가정하고 작성하시면 될 것 같습니다.
parser.add_argument('--algorithm', default='naive',
                    help='specify algorithm name')
parser.add_argument('--network', default="../dataset/test/new_network.dat",
                    help='a folder name containing network.dat')
parser.add_argument('--tactics', default="TTT",
                    help='ON/OFF for Tactics')
parser.add_argument('--compare_tactic', default="random",
                    help='How to select anchor edge')
parser.add_argument('--delta_tactic', default="compute",
                    help='How to calculate delta')
args = parser.parse_args()

G = nx.read_weighted_edgelist(args.network, nodetype=int)
# G = nx.karate_club_graph()
# print(G.edges(data=True)) # edge 및 weight 출력

print(f"data: {args.network.split('/')[2]}, nodes: {len(G.nodes())}, edges: {len(G.edges())}")

if args.algorithm == "naive":
    start_time = time.time()
    A = naive.run(G, args.s, args.b, args.t)
    end_time = time.time()
    print(end_time - start_time)
    print(A)
elif args.algorithm == "adv":
    start_time = time.time()
    A = adv.run(G, args.s, args.b, args.t)
    end_time = time.time()
    print(end_time - start_time)
    print(A)
elif args.algorithm == "adv_reuse":
    start_time = time.time()
    A = adv_reuse.run_reuse(G, args.s, args.b, args.t)
    end_time = time.time()
    print(end_time - start_time)
    print(A)

elif args.algorithm == "exp":
    if args.tactics[0] == 'T':
        T1_self_edge = True
    else:
        T1_self_edge = False
    if args.tactics[1] == 'T':
        T2_upperbound = True
    else:
        T2_upperbound = False
    
    if args.tactics[2] == 'T':
        start_time = time.time()
        A, FT, UT, G_prime = experiment_reuse.run(G, args.s, args.b, args.t, T1_self_edge, T2_upperbound)
        end_time = time.time()
        print(end_time - start_time)
        print(A)
        # print(FT)
        # print(UT)
        s_core_num = 0
        for i in G_prime.nodes:
            if G_prime.nodes[i]['label']:
                s_core_num += 1
        print(s_core_num)

    else:
        start_time = time.time()
        A, FT, UT, G_prime = experiment.run(G, args.s, args.b, args.t, T1_self_edge, T2_upperbound)
        end_time = time.time()
        print(end_time - start_time)
        print(A)
        # print(FT)
        # print(UT)
        s_core_num = 0
        for i in G_prime.nodes:
            if G_prime.nodes[i]['label']:
                s_core_num += 1
        print(s_core_num)
elif args.algorithm == "ekc":
    start_time = time.time()
    A = EKC.run(G, args.s, args.b, args.t)
    end_time = time.time()
    print(end_time - start_time)
    print(A)
elif args.algorithm == "exact":
    start_time = time.time()
    A, gain = exact.run(G, args.s, args.b, args.t)
    end_time = time.time()
    print(end_time - start_time)
    print(A)
    print(gain)
elif args.algorithm == "compare":
    start_time = time.time()
    A = compare.run(G, args.s, args.b, args.t, args.compare_tactic, args.delta_tactic)
    end_time = time.time()
    print(end_time - start_time)
    print(A)