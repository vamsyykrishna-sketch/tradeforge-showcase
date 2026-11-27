from src.universe.populate import populate_index

INDEXES = [
    "nifty50",
    "niftynext50",
    "niftymidcap150",
    "niftysmallcap250",
    "niftymicrocap250",
]


def populate_all_universes():
    for index_name in INDEXES:
        added, skipped = populate_index(index_name)
        print(f"{index_name}: added={added} skipped={skipped}")
