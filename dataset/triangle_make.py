def generate_triangles(num_triangles, start_node=1):
    """
    num_triangles 개수만큼 아래 규칙의 삼각형을 생성
      - 노드: u, v=u+1, w=u+2
      - 엣지 (u,v): weight=3
      - 엣지 (u,w), (v,w): weight=2
    start_node부터 노드 번호를 부여합니다.
    """
    edges = []
    for i in range(num_triangles):
        u = start_node + 3*i
        v = u + 1
        w = u + 2
        # two 노드는 weighted-degree=5, 한 노드는 4
        edges.append((u, v, 3))
        edges.append((u, w, 2))
        edges.append((v, w, 2))
    return edges

num = 1000

edges = generate_triangles(num, start_node=1)
with open("test/CC_test.dat", "w") as f:
    for u, v, w in edges:
        f.write(f"{u} {v} {w}\n")