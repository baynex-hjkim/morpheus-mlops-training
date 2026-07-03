# morpheus-mlops-training

Demo training/application repository for the Morpheus MLOps pipeline.

The GitHub Actions workflow builds `harbor.morpheus.test/mlops/mlops-demo`
with both `latest` and the commit short SHA, updates the image tag in
`baynex-hjkim/morpheus-mlops-charts`, and triggers an Argo CD sync for
the `mlops-demo` application.
