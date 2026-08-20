curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

 curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2-arm.zip"

aws configure set aws_access_key_id REDACTED
aws configure set aws_secret_access_key REDACTED

aws s3 ls --endpoint-url https://files.polygon.io s3://flatfiles/us_options_opra/

aws s3 cp --endpoint-url https://files.polygon.io --recursive s3://flatfiles/us_options_opra/day_aggs_v1/ ./us_options_opra/day_aggs_v1/
aws s3 cp --endpoint-url https://files.polygon.io --recursive s3://flatfiles/us_options_opra/minute_aggs_v1/ ./us_options_opra/minute_aggs_v1/
aws s3 cp --endpoint-url https://files.polygon.io --recursive s3://flatfiles/us_options_opra/trades_v1/ ./us_options_opra/trades_v1/

# Ideas

Weight by volume
XSP collar: strike diff vs itself
XSP call fairness
SPX put fairness
MSFT put fairness