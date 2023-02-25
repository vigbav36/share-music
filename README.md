
# Share Your Music



## About

A simple web application where we can upload and search for songs.

* Login or signup 
* All songs are listed in home page
* Enter a search prompt that fetches closest results for artists, albums and songs
* Every song has a url which can be used to stream/delete it
* Every user has a profile that lists songs and albums uploaded by the user
## Tech Stack

**Client:** HTML, CSS

**Server:** Flask, SQLite


## Run Locally

Clone the project

```bash
  git clone https://github.com/vigbav36/share-music.git
```

Go to the project directory

```bash
  cd music
```

Create a virtual environment

```bash
  sudo apt install python3-venv
  python3 -m venv my-project-env
```

Activate virtual environment

```bash
  source my-project-env/bin/activate
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  flask run
```


## Existing sample login creds for application

```txt
    User Name           password

    vig@mail.com        123
    bav@mail.com        123
    bav123@mail.com     123
```

