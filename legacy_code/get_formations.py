import asyncio
import aiohttp
import multiprocessing

import sqlite3

import pickle
from tqdm import tqdm
from bs4 import BeautifulSoup


async def fetch(session: aiohttp.ClientSession, id):
    async with session.get(
        f"https://www.espn.com/soccer/lineups/_/gameId/{id}"
    ) as response:
        if response.status < 300:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")

            elements = soup.find_all('span', class_="LineUps__TabsHeader__Title")

            if len(elements) < 2:
                return (id, None, None)
            return (id, elements[0].text, elements[1].text)
            
        elif response.status == 403:
            print("You've been caught!")
            return "*403*"
        else:
            return "*4XX*"


def process_urls(chunk_of_ids):
    async def process_chunk(chunk):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in chunk:
                task = asyncio.ensure_future(fetch(session, url))
                tasks.append(task)
            return await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(process_chunk(chunk_of_ids))
    return results


def run(ids, num_processes):
    with multiprocessing.Pool(num_processes) as pool:
        results = []
        for result in tqdm(pool.imap(process_urls, ids), total=len(ids)):
            results.extend(result)
            with open("fomrations.pkl", "wb") as f:
                pickle.dump(results, f)
    return results


if __name__ == "__main__":
    # vals = [633846]

    # GENERATE RANGE OF IDS

    # start_val = 671200
    # for i in range(start_val, start_val + 2000):
    #     vals.append(i)

    # READ MATCH IDS FROM FILE

    # with open("match_ids/vals.txt_24.txt", "r") as file:
    #     lines = file.readlines()
    #     vals = [int(line.strip()) for line in lines]

    conn = sqlite3.connect("data/lineups-data.db")
    cursor = conn.cursor()

    all_match_ids_query = ("SELECT DISTINCT match_id FROM matches")

    cursor.execute(all_match_ids_query)

    entries = [e[0] for e in cursor.fetchall()]

    query = ("SELECT DISTINCT match_id FROM formations")

    cursor.execute(query)

    results = [e[0] for e in cursor.fetchall()]

    nonexistent_ids = [id_ for id_ in entries if id_ not in [row[0] for row in results]]


    conn.close()

    print(f"URLs to retrieve: {len(nonexistent_ids)}")

    pages = []

    ids = [nonexistent_ids[i : i + 10] for i in range(0, len(nonexistent_ids), 10)]
    num_processes = multiprocessing.cpu_count()

    print(f"Numer of proccesses available: {num_processes}")

    fomrations = run(ids, num_processes)

    print(f"Fomrations retrieved: {len(fomrations)}")

    with open("fomrations.pkl", "wb") as f:
        pickle.dump(fomrations, f)

    print(pages)
