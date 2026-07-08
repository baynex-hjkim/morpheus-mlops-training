from __future__ import annotations

import json
import os
import time

import ray


@ray.remote
def train_partition(partition: int) -> dict[str, int | float]:
    start = time.time()
    score = sum(range(10_000 + partition))
    return {
        "partition": partition,
        "score": score,
        "duration_seconds": round(time.time() - start, 4),
    }


def init_ray() -> None:
    try:
        ray.init(address="auto", ignore_reinit_error=True)
    except ConnectionError:
        ray.init(ignore_reinit_error=True)


def main() -> None:
    init_ray()
    partitions = int(os.getenv("TRAIN_PARTITIONS", "4"))
    refs = [train_partition.remote(idx) for idx in range(partitions)]
    results = ray.get(refs)
    payload = {
        "run_name": os.getenv("RUN_NAME_PREFIX", "ray-mlops-demo"),
        "image_tag": os.getenv("IMAGE_TAG", "unknown"),
        "mlflow_tracking_uri": os.getenv("MLFLOW_TRACKING_URI", ""),
        "s3_endpoint_url": os.getenv("S3_ENDPOINT_URL", ""),
        "results": results,
    }
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
