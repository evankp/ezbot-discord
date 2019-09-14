#!/usr/bin/env bash
zip_file=lambda.zip
region='us-west-2'
function_name='discord-send-message-on-time'
project_files=(
    ./helpers/*
    ./tokens.yaml
    ./lambda_function.py
)

cd ./packages/
zip -r ${OLDPWD}/${zip_file} .
cd ${OLDPWD}

for file in "${project_files[@]}"; do
    zip ${zip_file} $file
done

aws lambda update-function-code --region $region --function-name $function_name --zip-file fileb://lambda.zip

if [[ $* != *"-d" ]]; then
    rm ${zip_file}
fi
