import threading

import tasks


def main():
    # Consumer execution
    threads = []
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
