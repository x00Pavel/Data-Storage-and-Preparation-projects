# How to start

For **local** development you would need to have docker (or podman) to be installed along with docker-compose (or podman-compose).
Steps:

1. Install docker `sudo apt install docker -y`
2. Create python virtual environment `python3 -m venv upa`
3. In root directory of the project run containers `docker-compose up -d --build`
   > For this step is suggested to have `.env` file in the root directory (near `docker-compose.yaml` file) with following content
   > ```ini
   > USER="root"
   > PASSWORD="example"
   > MONGO_LOCAL_URI="mongodb://root:example@localhost:27017"
   > ```
   > These values would be used while building the containers and later in the application
4. Activate the environment
5. In root directory of the project (where `setup.py` file is located) install the package `pip install -e .`
6. Run `upa --help` to check that package is installed
