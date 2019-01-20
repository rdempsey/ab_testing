#!/usr/bin/env python

import logging
import pandas as pd
from datetime import datetime
import requests
from tqdm import tqdm


def run_experiment(store_ids):
    results = dict()
    for store_id in store_ids:
        response = requests.get('http://localhost:8000/treatment/{}'.format(store_id))
        try:
            data = response.json()
            results[store_id] = data['treatment']
        except Exception as e:
            print(f'Error: {e}')
            print(f'Response: {response.text}')
            break
    return results


def main():
    # Run the experiment
    print("Load testing running...")
    experiment_start = datetime.now()
    all_results = list()

    store_counts = [10, 100, 500, 1000, 5000, 10000]
    for idx, s_count in enumerate(tqdm(store_counts)):
        store_ids = range(1, s_count + 1)

        start_time = datetime.now()
        api_result = run_experiment(store_ids)
        end_time = datetime.now()
        total_time = end_time - start_time
        requests_per_second = (s_count + 1) / total_time.total_seconds()

        model_a_count = 0
        model_b_count = 0
        for k, v in api_result.items():
            if v == "model_a":
                model_a_count += 1
            elif v == "model_b":
                model_b_count += 1

        result = {
            'experiment_number': idx + 1,
            'store_count': s_count,
            'model_a_count': model_a_count,
            'model_b_count': model_b_count,
            'start_time': start_time,
            'end_time': end_time,
            'total_time': total_time,
            'requests_per_second': requests_per_second
        }

        all_results.append(result)

    experiment_end = datetime.now()

    # Report the stats of the experiments
    cols = ['experiment_number', 'store_count', 'model_a_count', 'model_b_count', 'start_time', 'end_time', 'total_time',
            'requests_per_second', ]
    experiment_df = pd.DataFrame(all_results, columns=cols)

    min_reqs_per_sec = experiment_df['requests_per_second'].min()
    avg_reqs_per_sec = experiment_df['requests_per_second'].mean()
    max_reqs_per_sec = experiment_df['requests_per_second'].max()

    print(f'A/B Testing Endpoint Load Test')
    print(f'------------------------------')
    print(f'Experiment start: {experiment_start}')
    print(f'Experiment end: {experiment_end}')
    print(f'Total time: {experiment_end - experiment_start}')
    print(f'Min Req/Sec: {min_reqs_per_sec}')
    print(f'Max Req/Sec: {max_reqs_per_sec}')
    print(f'Avg Req/Sec: {avg_reqs_per_sec}\n')
    print(f'Results:\n{experiment_df.to_string()}')


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    main()
