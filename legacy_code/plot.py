import argparse

from positions import *
from dataset import ChemGraphDataset


"""
The purpose of this script is to plot a graph. The graph will be 
processed first if it has not already been processed.
"""


def parse_args(input_args=None):
    parser = argparse.ArgumentParser(description="Plot the graphs.")
    parser.add_argument(
        "--graph_dir",
        type=str,
        default=None,
        required=True,
        help="The folder where the graphs are stored.",
    )
    parser.add_argument(
        "--db_path",
        type=str,
        default=None,
        required=True,
        help="The path where the database is located.",
    )
    parser.add_argument(
        "--match_id",
        type=int,
        default=None,
        required=True,
        help="Match ID to plot.",
    )

    if input_args is not None:
        args = parser.parse_args(input_args)
    else:
        args = parser.parse_args()

    return args

def main(args):
    match_id = args.match_id

    dataset = ChemGraphDataset(
        root=args.graph_dir,
        match_ids=[match_id],
        db_path=args.db_path,
        edge_par=True
    )

    dataset.plot_graph(match_id, positions433, positions4231, True)

if __name__ == "__main__":
    args = parse_args()
    main(args)