import csv, re, argparse, requests

RE_LIST = [re.compile(r"https:\/\/docs\.google\.com\/forms\/d\/e\/[A-Za-z0-9_-]{56}\/\S+"), re.compile(r"(https?:\/\/)?www\.instagram\.com\/\w+?\/?")]

def markdead(dead: "list[str]") -> None:
    data = []
    with open('data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            data.append(row)
    with open('data.csv', 'w') as f:
        for row in data:
            if row[3] in dead:
                row[5] = "no"
            f.write(f"{','.join(row)}\n")

def auto():
    done = set()
    dead = set()
    with open('data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if row[3] in done or not any(map(lambda a: a.match(row[3]), RE_LIST)) or row[5] == "no":
                continue
            else:
                print(row[3])
                resp = requests.get(
                    row[3],
                    headers={
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"
                    }
                )
                print(resp)
                if resp.status_code in [403, 410]:
                    dead.add(row[3])
                done.add(row[3])
    markdead(list(dead))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = "markdead for CatPhish",
        description="This program marks rows of data in CatPhish as dead"
    )
    command_group = parser.add_mutually_exclusive_group(required=True)
    command_group.add_argument("-d", "--dead", required=False, nargs="+", help="Mark an item as dead")
    command_group.add_argument("-a", "--auto", action="store_true", help="Automatically detect if items are dead")
    args = parser.parse_args()
    if args.dead:
        markdead(args.dead)
    elif args.auto:
        auto()
