# self-notes

This page is intended to collect notes, useful commands and every random idea that can help make this project better.

- ``` cat /etc/os-release or hostnamectl```
-- to get details of OS of my EC2


- ``` yum update (my ec2 OS is amazon linux)```


- ``` python3 -m venv .venv and source .venv/bin/activate```
-- to create and activate virtual env




- ``` sqlite3 shop_category_mapping.db; .tables; select * from table_category; ctrl+d - exit```
-- to go in sqlite interactive terminal


- ``` streamlit run mymainstreamlit.py```
-- runs streamlit app and keeps the terminal engaged ie runs in forground


- ``` nohup streamlit run mymainstreamlit.py > streamlit.log 2>&1 &```
-- nohup stands for no hangup. nohup allows the process to keep running after i log out ie in background
-- > streamlit.log 2>&1 redirects both stdout and stderr to a log file
--- > streamlit.log -> streamlit application ka output log file me dal dega
--- 2>&1 -> 2>&1 means redirect file descriptor 2 (stderr, which is where error messages go) to wherever file descriptor 1 (stdout) is currently going. The & indicates that 1 refers to a file descriptor, not a file named "1".
-- & puts the process in the background
-- Together, > streamlit.log 2>&1 ensures that both normal program output and error messages go into the same file streamlit.log. This is important because otherwise the error messages (stderr) would still show on the terminal, not being captured in the log


- ``` ps aux ```- ps: process status; a: shows processes for all users, not just the current user; u displays the processes in a user-oriented format (showing user, CPU, memory, etc.); x includes processes that are not attached to a terminal (like daemons/services)
- ``` ps aux | grep streamlit ```<-- use like this


- ``` nginx -t```
-- to test and verify if /etc/nginx/nginx.conf is correct. a prerequisite before starting nginx



- ``` find . -name "test*"```
-- returns all files whose name contain test*


- ``` grep -Rni "my_string" .```
-- returns all files in current directory where my_string is found


- letsencrypt is certificate authority that provides TLS certs. certbot is open-source software to automate the process of getting certs from letsencrypt. in technical terms, certbot is one of ACME clients for letsencrypt


- ``` certbot certificates```
-- lists all certs managed by certbot, including their expiration dates


- ``` certbot renew```
-- renews all certs that are near expiration (<30 days)


- ``` certbot certonly --standalone -d abhishekprojects.com```
-- only obtains cert from letsencrypt but doesn't update any configuration files


- ``` certbot --nginx -d abhishekprojects.com```
-- obtains & installs cert from letsencrypt and automatically updates nginx configuration files. -d flag is to provide domain. [use this]


- ``` certbot revoke --cert-name analysemyexpense.abhishekprojects.com```
- ``` certbot delete --cert-name analysemyexpense.abhishekprojects.com```


- ``` openssl s_client -connect abhishekprojects.com:443 -showcerts```
-- connects to the server at abhishekprojects.com on port 443 (HTTPS). i run this from my local to diagnose how server returns cert. inshort, diagnosis from client perspective



- ``` docker compose up -d```
-- starts all services mentioned in docker-compose.yml file. -d flag is to run in detached mode 


- ``` docker compose down```
-- stops all services mentioned in docker-compose.yml


- ``` docker compose restart```
-- Restarts all services defined in the compose file without recreating them


- ``` docker stop $(docker ps -q)```
-- docker ps -q returns ids of containers running. pass it to stop command and it will start all running containers one-by-one


- ``` docker compose -f docker-compose.yml up -d --pull=always```
-- -f flag is for file name; --pull=always always pulls latest image before starting


- ``` docker restart firefly_iii_core```
-- restarts only "firefly_iii_core" container


- ``` docker exec -it firefly_iii_core bash```
-- goes inside the running container firefly_iii_core



- ``` curl -O https://raw.githubusercontent.com/firefly-iii/docker/main/docker-compose.yml```
-- to fetch docker-compose.yml file


- ``` curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-```(uname -m)"   -o /usr.libexec/docker/cli-plugins/docker-compose```


- ``` /opt/firefly-iii```-- firefly-iii location


- ``` /var/log/letsencrypt/letsencrypt.log```
-- letsencrypt logs go to this path


- ``` /etc/nginx/conf.d/streamlit.conf```
-- my app's nginx configuration file


- ```/etc/nginx/conf.d/streamlit.conf``` - my nginx configuration file



- ``` /opt/personal-finance-app```
-- location of my app


- ``` /opt/firefly-iii```
-- location of firefly-iii