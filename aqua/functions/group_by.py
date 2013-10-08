
from collections import defaultdict


def group_by(instances, attribute):
    grouped = defaultdict(list)
    for instance in instances:
        grouped[getattr(instance, attribute)].append(instance)
    return grouped
    
