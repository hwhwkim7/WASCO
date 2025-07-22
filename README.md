# WASCO
Instruction for experiment

## parameters for experiment
- s : s-core
- b : budget
- algorithm : Which algorithm to use. For experiment, use "exp". For exact solution, use "exact". For comparement, use "compare".
- network : Address of the dataset.
- tactics : 3 boolean parameters. (TTT, TFT, ...) Each represents self_edge tactic, upperbound tactic, reuse tactic.

- compare_tactic : Algorithm for comparement. There are random, degree, high_degree, weight_sum, high_weight_sum options.
- delta_tactic : How to compute delta for an edge. There are compute, SmW options.

## examples

### Our algorithm
```
python main.py --network ../dataset/test/network.dat --s 10 --b 10 --algorithm exp --tactics TFT
```

### Experiment for exact solution
```
python main.py --network ../dataset/test/network.dat --s 10 --b 10 --algorithm exact
```

### Experiment for comparement
```
python main.py --network ../dataset/test/network.dat --s 10 --b 10 --algorithm compare --compare_tactic degree --delta_tactic compute
```