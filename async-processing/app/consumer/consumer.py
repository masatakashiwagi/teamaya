import threading

import click

import tasks


@click.command()
@click.option("--num_threads", type=int, help='the number of threads', required=True, default=2)
def main(num_threads):
    # Consumer execution
    threads = []
    for _ in range(num_threads):
        for task in [
            tasks.TrainConsumer(queue_name='queue.model.train'),
            tasks.PredictConsumer(queue_name='queue.model.predict')
        ]:
            t = threading.Thread(target=task.run, daemon=True)
            t.start()
            threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
