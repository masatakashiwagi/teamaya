from concurrent.futures import ThreadPoolExecutor

import click

import tasks


@click.command()
@click.option("--num_threads", type=int, help='the number of threads', default=1)
@click.option("--max_workers", type=int, help='the number of max workers', default=None)
def main(num_threads: int, max_workers: int):
    # Consumer execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _ in range(num_threads):
            for task in [
                tasks.TrainConsumer(queue_name='queue.model.train'),
                tasks.PredictConsumer(queue_name='queue.model.predict')
            ]:
                executor.submit(task.run)


if __name__ == "__main__":
    main()
