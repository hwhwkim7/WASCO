i = 1
ii = 0
output_path = f'../output/synthetic.csv'
networks = [
    'scalability_10000', 'scalability_20000', 'scalability_40000', 'scalability_80000', 'scalability_160000'
]
type = 'synthetic'
ss = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
bb = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
tactics = ['TTT', 'FFF']

with (open('cmds.txt', 'w') as f):
    for network in networks:
        for s in ss:
            for b in bb:
                for tactic in tactics:
                    if i % 25 == 0:
                        end = "&\n"
                        ii += 1
                    else: end = "&&"
                    i += 1
                    f.write(f'python3 main.py --network ../dataset/{type}/{network} --algorithm exp --s {s} --b {b} --tactics {tactic} --output_path {output_path}{end}\n')
print(ii)