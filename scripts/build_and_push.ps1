param(
  [string]$Region = "ap-southeast-1",
  [string]$Repository = "group7-sentiment",
  [string]$Tag = "spam-v1"
)
$ErrorActionPreference = "Stop"
$AccountId = (aws sts get-caller-identity --query Account --output text).Trim()
if ($LASTEXITCODE -ne 0) { throw "Check aws configure / AWS credentials." }
$Registry = "${AccountId}.dkr.ecr.${Region}.amazonaws.com"
$ImageUri = "${Registry}/${Repository}:${Tag}"
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $Registry
if ($LASTEXITCODE -ne 0) { throw "ECR login failed" }
$BuildPath = Join-Path $PSScriptRoot "../lambda"
docker buildx build --platform linux/amd64 --provenance=false --load -t $ImageUri $BuildPath
if ($LASTEXITCODE -ne 0) { throw "Build failed" }
docker push $ImageUri
if ($LASTEXITCODE -ne 0) { throw "Push failed" }
Write-Output "Image URI: $ImageUri"
Write-Output "Now deploy this image to Lambda; pushing ECR alone does not update the function."
