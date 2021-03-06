#!/usr/bin/env bash
zip_file=lambda.zip
region='us-west-2'
function_name='parse-sc-roadmap'
project_files=(
    ./helpers/yaml_helper.py
    ./helpers/time.py
    ./helpers/sc_roadmap.py
    ./lambda_parse_roadmap.py
)

for file in "${project_files[@]}"; do
    zip ${zip_file} $file
done

aws lambda update-function-code --region $region --function-name $function_name --zip-file fileb://lambda.zip

if [[ $* != *"-d" ]]; then
    rm ${zip_file}
fi
