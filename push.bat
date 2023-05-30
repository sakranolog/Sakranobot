@echo off

REM Define the Docker image details
SET ACCOUNT_NAME=sakranolog
SET IMAGE_NAME=sakranobot
SET IMAGE_TAG=latest

REM Build the Docker image
docker build -t %ACCOUNT_NAME%/%IMAGE_NAME%:%IMAGE_TAG% .


REM Push the Docker image
docker push %ACCOUNT_NAME%/%IMAGE_NAME%:%IMAGE_TAG%