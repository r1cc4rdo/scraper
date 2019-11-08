conda create --name lambda python=3.7.4
conda activate lambda

pip install --target /tmp/lambda pytz
pip install --target /tmp/lambda requests
pip install --target /tmp/lambda beautifulsoup4

cp lambda_function.py /tmp/lambda
cp download_to_json.py /tmp/lambda

cd /tmp/lambda
zip -r /tmp/deploy.zip .
