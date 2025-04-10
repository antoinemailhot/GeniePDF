# data_structuring/aggregator.py

def aggregate_results(results):
    """
    Agrège les résultats extraits de plusieurs PDF.

    :param results: Liste de dictionnaires ou de structures issues de l'analyse de chaque PDF.
    :return: Un seul dictionnaire combinant toutes les données.
    """
    aggregated = []
    for result in results:
        if isinstance(result, list):
            aggregated.extend(result)
        else:
            aggregated.append(result)
    return aggregated
