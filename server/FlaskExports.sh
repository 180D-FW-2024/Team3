#!/bin/bash

export FLASK_APP=server
export FLASK_ENV=development
export FLASK_RUN_PORT=80

export QUART_APP="app.server:app"  # module:app_instance
# export PYTHONPATH="$PYTHONPATH:/path/to/project_root"