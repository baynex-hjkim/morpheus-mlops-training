from __future__ import annotations

import json
import os
import time

import mlflow
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
    scores = [int(result["score"]) for result in results]
    durations = [float(result["duration_seconds"]) for result in results]
    run_name = os.getenv("RUN_NAME_PREFIX", "ray-mlops-demo")
    image_tag = os.getenv("IMAGE_TAG", "unknown")
    run_id = os.getenv("RUN_ID", image_tag)
    payload = {
        "run_name": run_name,
        "image_tag": image_tag,
        "run_id": run_id,
        "mlflow_tracking_uri": os.getenv("MLFLOW_TRACKING_URI", ""),
        "s3_endpoint_url": os.getenv("S3_ENDPOINT_URL", ""),
        "results": results,
    }

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "ray-mlops-demo"))
    with mlflow.start_run(run_name=f"{run_name}-{image_tag}") as run:
        mlflow.log_params(
            {
                "image_tag": image_tag,
                "run_id": run_id,
                "partitions": partitions,
                "ray_job": os.getenv("RAY_JOB_NAME", ""),
            }
        )
        mlflow.log_metrics(
            {
                "partition_count": float(partitions),
                "score_total": float(sum(scores)),
                "score_max": float(max(scores)),
                "duration_total_seconds": float(round(sum(durations), 6)),
            }
        )
        payload["mlflow_run_id"] = run.info.run_id
        try:
            mlflow.log_dict(payload, "summary.json")
        except Exception as exc:  # Keep the demo run visible even if artifact storage is not ready.
            payload["artifact_warning"] = str(exc)

    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
