from src.patterns.swing import SwingPoint


def filter_swings(swings: list[SwingPoint]) -> list[SwingPoint]:
    if not swings:
        return []

    filtered = [swings[0]]

    for swing in swings[1:]:

        last = filtered[-1]

        if swing.kind != last.kind:
            filtered.append(swing)
            continue

        # Two consecutive highs
        if swing.kind == "HIGH":
            if swing.price > last.price:
                filtered[-1] = swing

        # Two consecutive lows
        else:
            if swing.price < last.price:
                filtered[-1] = swing

    return filtered