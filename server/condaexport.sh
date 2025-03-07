#!/bin/bash

conda env export > environment.yaml
sed -i '' 's/\([a-zA-Z0-9_-]*=[^=]*\)=.*/\1/' environment.yaml