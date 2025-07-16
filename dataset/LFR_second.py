import networkx as nx

# 1. 기존 데이터셋 읽기
edges_file = "test/LFR_second.dat"
edges = []
all_nodes = set()

with open(edges_file, "r") as f:
    for line in f:
        u, v, weight = line.strip().split()
        u, v, weight = int(u), int(v), int(weight)
        edges.append((u, v, weight))
        all_nodes.add(u)
        all_nodes.add(v)

print(f"원본 데이터: {len(edges)}개 엣지, 노드 범위: {min(all_nodes)} ~ {max(all_nodes)}")

# 2. 노드 번호 재매핑 (1부터 연속된 자연수로)
sorted_nodes = sorted(all_nodes)
old_to_new = {old_node: new_node for new_node, old_node in enumerate(sorted_nodes, 1)}

print(f"노드 개수: {len(sorted_nodes)}")
print(f"재매핑: {min(sorted_nodes)} -> 1, {max(sorted_nodes)} -> {len(sorted_nodes)}")

# 3. 엣지 데이터 변환
new_edges = []
for u, v, weight in edges:
    new_u = old_to_new[u]
    new_v = old_to_new[v]
    new_edges.append((new_u, new_v, weight))

# 4. 변환된 데이터를 같은 파일에 저장
with open(edges_file, "w") as f:
    for u, v, weight in new_edges:
        f.write(f"{u} {v} {weight}\n")

print(f"→ {edges_file} 저장 완료")
print(f"변환 후: 노드 1 ~ {len(sorted_nodes)}, {len(new_edges)}개 엣지")