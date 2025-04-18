import os
import sqlite3

from tqdm import tqdm
from itertools import combinations
from collections import OrderedDict
from concurrent.futures import as_completed, ProcessPoolExecutor

# PyTorch includes
import torch
from torch_geometric.utils import to_undirected
from torch_geometric.data import Data, Batch, InMemoryDataset

# Graphics includes
import networkx as nx
from torch_geometric.utils import to_networkx
import matplotlib.pyplot as plt

from positions import formations


"""
This is the implementation of the dataset class. It includes the logic
for processing the data, interfacing with the database, plotting the
graphs, and more.
"""


class ChemGraphDataset(InMemoryDataset):
    def __init__(
        self,
        root,
        match_ids,
        db_path,
        num_processes=8,
        process_data=True,
        graph_par=False,
        edge_par=False,
        transform=None,
        pre_transform=None,
    ):
        self.match_ids = match_ids
        self.db_path = db_path

        # Determine the number of processes assigned to each task
        if graph_par and edge_par:
            self.num_graph_processes = int(0.1 * num_processes)
            self.num_edge_processes = int((num_processes - self.num_graph_processes) / self.num_graph_processes)
        else:
            self.num_graph_processes = num_processes
            self.num_edge_processes = num_processes

        self.process_data = process_data
        self.graph_par = graph_par
        self.edge_par = edge_par
        super(ChemGraphDataset, self).__init__(root, transform, pre_transform)

    @property
    def raw_file_names(self):
        return []

    @property
    def processed_file_names(self):
        return [f"graph_{match_id}.pt" for match_id in self.match_ids]

    def download(self):
        pass

    def process(self):
        if self.process_data:
            non_processed_match_ids = []
            with tqdm(total=len(non_processed_match_ids)) as pbar:
                for match_id in self.match_ids:
                    file_path = os.path.join(self.processed_dir, f"graph_{match_id}.pt")
                    if not os.path.exists(file_path):
                        if self.graph_par:
                            non_processed_match_ids.append(match_id)
                        else:
                            self.create_graph(match_id, file_path)
                            pbar.update(1)
                if self.graph_par:
                    print(f"Actually processing {len(non_processed_match_ids)} matches")
                    with ProcessPoolExecutor(max_workers=self.num_graph_processes) as executor:
                        futures = {
                            executor.submit(
                                self.create_graph,
                                match_id,
                                os.path.join(self.processed_dir, f"graph_{match_id}.pt"),
                            ): match_id
                            for match_id in non_processed_match_ids
                        }
                        for completed_future in as_completed(futures):
                            match_id = futures[completed_future]
                            try:
                                result = completed_future.result()
                                pbar.update(1)
                            except Exception as e:
                                print(f"Task for match_id {match_id} raised an exception: {e}")

    def collate_fn(self, batch):
        return Batch.from_data_list(batch)

    def __getitem__(self, idx):
        # Load a graph
        graph_path = os.path.join(self.processed_dir, f"graph_{self.match_ids[idx]}.pt")
        graph = torch.load(graph_path)

        return graph
    
    def get_by_id(self, id):
        # Load a graph by id
        graph_path = os.path.join(self.processed_dir, f"graph_{id}.pt")
        graph = torch.load(graph_path)

        return graph

    def len(self):
        return len(self.match_ids)

    def create_graph(self, player_pair, dir):
        self.fetch_graph(self.get_connection(), player_pair, dir)

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def get_minutes_played(self, result):
        """
        Given a result from the fetch_edge query, this function
        directly computes the number of minutes the player pair 
        has played together.
        """
        if result[1] == "Starter" and result[4] == "Starter":
            if result[2] is None and result[5] is None:
                return 90
            elif result[2] is None or result[5] is None:
                return result[2] if result[5] is None else result[5]
            else:
                return result[2] if result[2] < result[5] else result[5]
        elif result[1] == "Starter" or result[4] == "Starter":
            if result[1] == "Starter":
                if result[5] is None:
                    return 0
                if result[2] is None:
                    w = 90 - result[5]
                else:
                    w = result[2] - result[5]
                if w < 0:
                    return 0
                return w
            else:
                if result[2] is None:
                    return 0
                if result[5] is None:
                    w = 90 - result[2]
                else:
                    w = result[5] - result[2]
                if w < 0:
                    return 0
                return w
        else:
            if result[2] is None or result[5] is None:
                return 0
            return 90 - result[2] if result[2] > result[5] else 90 - result[5]

    def initialize_connection(self):
        global CONNECTION
        CONNECTION = self.get_connection()

    def fetch_edge(self, player_pair, date):
        """
        This function queries the database for a player pair and
        returns the edge weight
        """
        cursor = CONNECTION.cursor()
        results = cursor.execute(
            """SELECT DISTINCT a.player_id AS 'player1',
                            a.player_type AS 'playerType1',
                            a.sub_time AS 'subTime1',
                            b.player_id AS 'player2',
                            b.player_type AS 'playerType2',
                            b.sub_time AS 'subTime2',
                            c.date AS 'date'
            FROM lineups a 
            INNER JOIN lineups b ON a.match_id = b.match_id AND a.team_id = b.team_id 
            INNER JOIN matches c ON c.match_id = a.match_id AND c.match_id = b.match_id
            WHERE c.date < ? AND a.player_id = ? AND b.player_id = ? AND a.player_type != 'Bench' AND b.player_type != 'Bench';""",
            (date, player_pair[0], player_pair[1]),
        )
        edge_weight = 0
        edge = [player_pair[0], player_pair[1]]
        for result in results:
            w = self.get_minutes_played(result)
            edge_weight += w
        
        return edge, edge_weight


    def fetch_graph(self, connection: sqlite3.Connection, match_id, dir):
        """
        This function fetches all the edges for a graph from the database and saves the
        file to the specified directory
        """
        cursor = connection.cursor()
        players = {}

        # Get the players for a given match
        results = cursor.execute(
            """SELECT DISTINCT a.player_id, a.team_id, b.date, b.home_team_id, b.away_team_id, b.home_team_goal, b.away_team_goal
            FROM lineups a
            INNER JOIN matches b ON a.match_id = b.match_id
            WHERE a.match_id = ? AND a.player_type = 'Starter';""",
            (match_id,),
        )
        results = results.fetchall()

        for result in results:
            if result[1] in players:
                players[result[1]].append(result[0])
            else:
                players[result[1]] = [result[0]]

        date = results[0][2]
        home_team_id = results[0][3]
        away_team_id = results[0][4]
        home_goal = results[0][5]
        away_goal = results[0][6]

        edges = []
        edge_weights = []

        if self.edge_par:
            player_pairs = []
            results = OrderedDict()
            # Identify the player pairs
            for team in players:
                for pair in list(combinations(players[team], 2)):
                    if pair[0] != pair[1]:
                        player_pairs.append(pair)
                        results[pair] = None
            # Assign a process to each edge
            with ProcessPoolExecutor(max_workers=self.num_edge_processes, initializer=self.initialize_connection) as executor:
                futures = {
                    executor.submit(
                        self.fetch_edge,
                        player_pair,
                        date
                    ): player_pair
                    for player_pair in player_pairs
                }
                for completed_future in as_completed(futures):
                    pair = futures[completed_future]
                    try:
                        results[pair] = completed_future.result()
                    except Exception as e:
                        print(f"Task for pair {pair} raised an exception: {e}")

                results = list(results.values())

                edges, edge_weights = zip(*results)

        else:
            global CONNECTION
            CONNECTION = self.get_connection()
            # Fetch the edge weight for each player pair
            for team in players:
                for player_pair in list(combinations(players[team], 2)):
                    if player_pair[0] != player_pair[1]:
                        edge, weight = self.fetch_edge(player_pair, date)
                        edges.append(edge)
                        edge_weights.append(weight)
            CONNECTION.close()

        connection.close()

        x = torch.tensor(
            [[p_id, t_id] for t_id in players for p_id in players[t_id]], dtype=torch.float
        )

        # Edge indices
        edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()

        # Edge weights (minutes played together)
        edge_weights = torch.tensor(edge_weights, dtype=torch.long)

        # Create a PyTorch Geometric Data object
        graph = Data(x=x, edge_index=edge_index, edge_attr=edge_weights, is_undirected=False)

        # Add graph-level attributes
        graph.match_id = match_id
        graph.date = date
        graph.home_team_id = home_team_id
        graph.away_team_id = away_team_id
        graph.home_goal = home_goal
        graph.away_goal = away_goal

        # Save the graph
        torch.save(graph, dir)

    def plot_graph(self, match_id, home_position, away_position, query_labels):
        graph = self.get_by_id(match_id)

        # Convert graph to a better visualization framework
        nx_graph = to_networkx(graph, to_undirected=False)

        # Rectify error in to_networkx of adding extraneous nodes
        nx_graph.remove_nodes_from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])

        node_labels = {node: node for node in nx_graph.nodes()}

        if query_labels:
            # Query the database for player and team names 
            connection = self.get_connection()
            cursor = connection.cursor()
            team_name_results = cursor.execute(
                """
                SELECT DISTINCT team_id, team_name FROM teams
                WHERE team_id = ? OR team_id = ?
                """,
                (graph.home_team_id, graph.away_team_id),
            )
            team_names = team_name_results.fetchall()
            home_team_name = team_names[0][1] if team_names[0][0] == graph.home_team_id else team_names[1][1]
            away_team_name = team_names[1][1] if team_names[1][0] == graph.away_team_id else team_names[0][1]
            plt.title(f"{home_team_name} vs {away_team_name} ({graph.date})\n\n{graph.home_goal} - {graph.away_goal}")

            player_ids = [str(id) for id in graph.x[:, 0].int().tolist()]

            player_name_results = cursor.execute(
                f"SELECT DISTINCT player_id, player_name FROM players WHERE player_id IN ({', '.join(player_ids)})"
            )

            player_names = player_name_results.fetchall()

            player_names_dict = dict(player_names)

            node_labels = {node: player_names_dict[node] for node in nx_graph.nodes()}

            formation_results = cursor.execute(
                """
                SELECT home_team_formation, away_team_formation FROM formations
                WHERE match_id = ?
                """,
                (match_id,),
            )

            results = formation_results.fetchall()
            home_position = formations[results[0][0]]
            away_position = formations[results[0][1]]
        
        positions = [home_position, away_position]

        # Calculate position offsets
        for i in range(len(positions[1])):
            positions[1][i][0] += 0.5
            
        # Assign nodes to positions
        pos = {}
        for i, node in enumerate(nx_graph.nodes):
            pos[node] = positions[int(i >= 11)][i % 11]

        # Draw the graph
        nx.draw(
            nx_graph,
            pos,
            labels=node_labels,
            width=[w.item() * 10 / max(graph.edge_attr) for w in graph.edge_attr],
            node_color="skyblue",
            node_shape="o",
            edge_color="grey",
            with_labels=True,
            font_size=8,
            arrows=False
        )
        plt.show()
