# Bins API

This is the code needed to create a REST API to be used as a tutorial for learning how to interact with REST APIs. The primary functionality of this API is to allow users to create virtual bins and store a string in each of those bins.

There is an interactive explorer for this API [here](https://petstore.swagger.io/?url=https://raw.githubusercontent.com/dchosnek/bin-api-tutorial/main/openapi3.1.0.yml), but a simple overview of the API is:

🔒 **POST**   `/bins` to create a new empty bin

🔒 **GET**    `/bins/{binId}` to retrieve the contents of a specific bin

🔒 **PUT**    `/bins/{binId}` to update the contents of a specified bin

🔒 **DELETE** `/bins/{binId}` to permanently delete a bin


All of the above methods require a token (API key) that identifies the user. Normally a user would be issued a token from the system being accessed via some web page. To keep this tutorial simple, insecure methods have been added for generating and validating a token.

🔓 **GET** `/token?email={email}` to generate an expiring token

🔓 **GET** `/token/{token}` to verify if the specified token is still valid

More details of the exact format of each request and response are available in the [spec](openapi3.1.0.yml) or the interactive [guide](https://petstore.swagger.io/?url=https://raw.githubusercontent.com/dchosnek/bin-api-tutorial/main/openapi3.1.0.yml).

## Access this API

The API has been deployed to the baseUrl of [https://hyzcf9p535.execute-api.us-east-1.amazonaws.com/v1](https://hyzcf9p535.execute-api.us-east-1.amazonaws.com/v1).

## Implementation details

This API is defined by the Amazon CloudFormation [template](bins.yml) in this repository. It creates a serverless application that uses AWS lambda functions to serve most methods.

To deploy your own copy of this API, use `bins.yml` as the CloudFormation template. It expects the lambda deployment packages to be in a single S3 bucket with the names:

* create_bins.zip
* create_token.zip
* get_bins.zip
* handle_bins.zip
* verify_token.zip

