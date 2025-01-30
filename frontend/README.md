# Team3

## Setup
### Backend Server
To set up backend server, first set up the conda environment from the file server/environment.yaml:
1) cd server
2) conda env create -f environment.yaml
3) conda activate Raspitouille

Then, source the appropriate Flask environment variables, and make sure the root folder contains the `.env` file
(not in github), before running the server through flask:
1) source FlaskExports.sh
2) flask run

To run ngrok
ngrok http --url=<static-site> 5001