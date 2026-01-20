#!/usr/bin/env python3
import re
import requests
import sys

if __name__ == '__main__':
    url = sys.argv[1]
    response = requests.get(url)
    response.raise_for_status()

    log_lines = response.text.splitlines()
    pattern = re.compile(r'odoo\.modules\.loading: Module (\w+) loaded in ([\d.]+)s')

    module_stats = {}

    for line in log_lines:
        match = pattern.search(line)
        if match:
            module = match.group(1)
            time = float(match.group(2))
            if module not in module_stats:
                module_stats[module] = {'count': 0, 'total_time': 0.0}
            module_stats[module]['count'] += 1
            module_stats[module]['total_time'] += time

    sorted_modules = sorted(module_stats.items(), key=lambda x: x[1]['total_time'])

    total = 0.0
    for module, stats in sorted_modules:
        total += stats['total_time']
        print(f"{stats['total_time']:.2f}s\t{stats['count']}\t{module.ljust(100)} -> total: {total:.2f}s")  # noqa: T201
