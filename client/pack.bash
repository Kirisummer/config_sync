#!/bin/bash -e

pyinstaller main.py
cd dist
mv main config_client
zip -r linux_config_client.zip config_client
cd -
