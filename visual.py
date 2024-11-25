import os
import json
import subprocess
from collections import defaultdict, deque


def load_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def get_commits(repo_path):
    os.chdir(repo_path)
    result = subprocess.run(['git', 'rev-list', '--all'], capture_output=True, text=True)
    commits = result.stdout.splitlines()
    return commits


def build_dependency_graph(commits):
    graph = defaultdict(list)


    for commit in commits:
        result = subprocess.run(['git', 'show', '--pretty=%P', '--no-patch', commit], capture_output=True, text=True)
        parents = result.stdout.strip().split()

        for parent in parents:
            graph[parent].append(commit)


    transitive_graph = defaultdict(set)


    for commit in list(graph.keys()):

        queue = deque(graph[commit])
        visited = set()

        while queue:
            current_commit = queue.popleft()
            if current_commit not in visited:
                visited.add(current_commit)
                transitive_graph[commit].add(current_commit)
                queue.extend(graph[current_commit])



    return graph


def generate_graphviz_code(graph):
    dot_lines = ['digraph G {']
    for parent, children in graph.items():
        for child in children:
            dot_lines.append(f'    "{parent}" -> "{child}";')
    dot_lines.append('}')
    return '\n'.join(dot_lines)


def save_graph_to_file(graph_code, output_file):
    with open(output_file, 'w') as f:
        f.write(graph_code)


def generate_png(graphviz_path, dot_file, output_png):
    subprocess.run([graphviz_path, '-Tpng', dot_file, '-o', output_png], check=True)


def main(config_path):
    config = load_config(config_path)
    repo_path = config['repo_path']
    output_file = config['output_file']
    graphviz_path = config['graphviz_path']

    commits = get_commits(repo_path)
    graph = build_dependency_graph(commits)
    graph_code = generate_graphviz_code(graph)

    save_graph_to_file(graph_code, output_file)

 
    output_png = output_file.replace('.dot', '.png')
    generate_png(graphviz_path, output_file, output_png)

    print(graph_code)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Visualize Git commit dependencies.')
    parser.add_argument('config', type=str, help='Path to the config file')

    args = parser.parse_args()

    main(args.config)
