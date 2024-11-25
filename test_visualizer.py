import unittest
from unittest.mock import patch, mock_open, MagicMock
from visual import (load_config, get_commits, build_dependency_graph,
                         generate_graphviz_code, save_graph_to_file, generate_png)

class TestGitVisualization(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='{"repo_path": "/path/to/repo", "output_file": "output.dot", "graphviz_path": "/usr/bin/dot"}')
    def test_load_config(self, mock_file):
        config = load_config('dummy_path')
        self.assertEqual(config['repo_path'], '/path/to/repo')
        self.assertEqual(config['output_file'], 'output.dot')
        self.assertEqual(config['graphviz_path'], '/usr/bin/dot')

    @patch('subprocess.run')
    @patch('os.chdir')
    def test_get_commits(self, mock_chdir, mock_run):
        mock_run.return_value = MagicMock(stdout='commit1\ncommit2\n')
        commits = get_commits('/path/to/repo')
        mock_chdir.assert_called_once_with('/path/to/repo')
        mock_run.assert_called_once_with(['git', 'rev-list', '--all'], capture_output=True, text=True)
        self.assertEqual(commits, ['commit1', 'commit2'])

    @patch('subprocess.run')
    def test_build_dependency_graph(self, mock_run):
        mock_run.side_effect = [
            MagicMock(stdout='parent1\n'),
            MagicMock(stdout='parent2\n'),
        ]
        commits = ['commit1', 'commit2']
        graph = build_dependency_graph(commits)
        expected_graph = {
            'commit1':[],
            'commit2': [],
            'parent1': ['commit1'],
            'parent2': ['commit2'],
        }
        self.assertEqual(dict(graph), expected_graph)

    def test_generate_graphviz_code(self):
        graph = {
            'parent1': ['commit1'],
            'parent2': ['commit2'],
        }
        expected_output = 'digraph G {\n    "parent1" -> "commit1";\n    "parent2" -> "commit2";\n}'
        result = generate_graphviz_code(graph)
        self.assertEqual(result, expected_output)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_graph_to_file(self, mock_file):
        graph_code = 'digraph G {}'
        save_graph_to_file(graph_code, 'output.dot')
        mock_file().write.assert_called_once_with(graph_code)

    @patch('subprocess.run')
    def test_generate_png(self, mock_run):
        generate_png('/usr/bin/dot', 'output.dot', 'output.png')
        mock_run.assert_called_once_with(['/usr/bin/dot', '-Tpng', 'output.dot', '-o', 'output.png'], check=True)

if __name__ == '__main__':
    unittest.main()
