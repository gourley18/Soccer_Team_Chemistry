import time
import sqlite3
import argparse

from multiprocessing import cpu_count

from dataset import ChemGraphDataset


"""
The purpose of this script is to process a batch of matches
from the database and store them to .pt files as PyTorch
graph objects.
"""


def get_connection(db_path) -> sqlite3.Connection:
    return sqlite3.connect(db_path)

def parse_args(input_args=None):
    parser = argparse.ArgumentParser(description="Preprocess the data into graphs.")
    parser.add_argument(
        "--graph_output_dir",
        type=str,
        default=None,
        required=True,
        help="The folder where the graphs will be stored.",
    )
    parser.add_argument(
        "--database_path",
        type=str,
        default=None,
        required=True,
        help="The path where the database is located.",
    )
    parser.add_argument(
        "--match_ids",
        nargs="+",
        type=int,
        default=None,
        help="List of match IDs to process. No start or end date should be specified.",
    )
    parser.add_argument(
        "--data_start_date",
        type=str,
        default=None,
        help="The earliest date (YYYY-MM-DD) matches will be drawn from. No match IDs should be specified.",
    )
    parser.add_argument(
        "--data_end_date",
        type=str,
        default=None,
        help="The latest date (YYYY-MM-DD) matches will be drawn from. No match IDs should be specified.",
    )
    parser.add_argument(
        "--graph_par",
        action='store_true',
        default=False,
        required=False,
        help="Parallelization at the graph level.",
    )
    parser.add_argument(
        "--edge_par",
        action='store_true',
        default=False,
        required=False,
        help="Parallelization at the graph edge level.",
    )

    if input_args is not None:
        args = parser.parse_args(input_args)
    else:
        args = parser.parse_args()

    return args

def main(args):

    print("Retreiving match IDs for specified date range")

    assert (args.match_ids != None) ^ ((args.data_start_date != None) and (args.data_end_date != None)), "You must choose match IDs to process OR specify both a start and end date"

    match_ids = []

    # Fetch the match ids given the date range
    if args.match_ids == None:
        connection = get_connection(args.database_path)
        cursor = connection.cursor()
        results = cursor.execute(
            """SELECT DISTINCT match_id FROM matches
            WHERE date >= ?
                AND date <= ?
            ORDER BY date;""",
            (args.data_start_date, args.data_end_date),
        )

        match_ids = [result[0] for result in results.fetchall()]

    else:
        match_ids = args.match_ids

    print(f"{len(match_ids)} matches to process")

    num_processes = 1
    if args.graph_par or args.edge_par:
        num_processes = min(cpu_count(), 40)
    
    print(f"Utilizing {num_processes} cores")

    print("Begin processing graphs")

    start_time = time.time()

    # Instantiate the dataset object which triggers the data processing
    ChemGraphDataset(
        root=args.graph_output_dir,
        match_ids=match_ids,
        db_path=args.database_path,
        num_processes=num_processes,
        process_data=True,
        graph_par=args.graph_par,
        edge_par=args.edge_par
    )

    print(f"Processing time: {time.time() - start_time}")


if __name__ == "__main__":
    args = parse_args()
    main(args)
