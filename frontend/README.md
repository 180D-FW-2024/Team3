# Team3

## Setup
## Website
To set up the website, navigate to the `raspi-site` directory, and do the following:
1) npm run build
2) npm run start

### Backend Server
To set up backend server, first set up the conda environment from the file server/environment.yaml:
1) cd server
2) conda env create -f environment.yaml
3) conda activate Raspitouille

Then, source the appropriate Flask environment variables, and make sure the root folder contains the `.env` file
(not in github), before running the server through flask:
1) source FlaskExports.sh
2) flask run

To run ngrok use:
`ngrok http --url=<static-site> 5001`

### Backend Server (Docker)
We got it dockerized! To build use the below command
`docker build --no-cache -t flask-server .`
Then run using 
`docker run --env-file ../.env --name raspitouille-server -p 5001:5001 flask-server`