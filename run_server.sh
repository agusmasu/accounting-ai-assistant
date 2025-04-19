#!/bin/bash

# Set environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Run the functions framework
functions-framework --target=http_function --source=main_functions.py --debug 