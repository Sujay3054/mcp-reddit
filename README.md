# Reddit MCP (Multi-Component Project) Server

A robust Python server built on **PRAW** and **FastMCP** for comprehensive Reddit interaction. This project allows you to retrieve posts, user data, create/edit content, moderate, and more via a unified API-like interface.

---

## 📌 Table of Contents

- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Server](#running-the-server)
- [🛠️ Available Tools (API Endpoints)](#️-available-tools-api-endpoints)
  - [Content Retrieval & Discovery](#content-retrieval--discovery)
  - [User & Community Info](#user--community-info)
- [✍️ Content Modification & Actions](#️-content-modification--actions)
- [⚠️ Known Issues](#️-known-issues)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- [`praw`](https://pypi.org/project/praw/) library
- [`fastmcp`](https://pypi.org/project/fastmcp/) library

### Installation

1. **Clone the Repository:**
    ```bash
    git clone [repository-url]
    cd reddit-mcp-server
    ```

2. **Install Dependencies:**
    ```bash
    pip install praw fastmcp
    ```

### Configuration

Set the following environment variables for Reddit API authentication:

| Environment Variable       | Description                                                     |
|----------------------------|-----------------------------------------------------------------|
| `REDDIT_CLIENT_ID`         | Your Reddit application's client ID.                            |
| `REDDIT_CLIENT_SECRET`     | Your Reddit application's client secret.                        |
| `REDDIT_USER_AGENT`        | Descriptive user agent (e.g., `python:futuregen:v1.0 (by u/YourUsername)`). |
| `REDDIT_REFRESH_TOKEN`     | PRAW refresh token for long-term script access.                 |

**Example:**
```python
import os

os.environ["REDDIT_CLIENT_ID"] = "VoDq1m6w4nmuLk7oDUmN8Q"
os.environ["REDDIT_CLIENT_SECRET"] = "rxSEa8e2uyFSK6cfrJVlAe_omhgsXQ"
os.environ["REDDIT_USER_AGENT"] = "python:futuregen:v1.0 (by u/Striking_Economy698)"
os.environ["REDDIT_REFRESH_TOKEN"] = "200334591410393-Uwlr-vfZ65KzOQGmmr2qCUV_TrT53w"
### Reddit MCP (Multi-Component Project) Server

A robust Python server built on **PRAW** and **FastMCP** for comprehensive Reddit interaction. This project allows you to retrieve posts, user data, create/edit content, moderate, and more via a unified API-like interface.

---

## 📌 Table of Contents

- [🚀 Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Server](#running-the-server)
- [🛠️ Available Tools (API Endpoints)](#️-available-tools-api-endpoints)
  - [Content Retrieval & Discovery](#content-retrieval--discovery)
  - [User & Community Info](#user--community-info)
- [✍️ Content Modification & Actions](#️-content-modification--actions)
- [⚠️ Known Issues](#️-known-issues)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- [`praw`](https://pypi.org/project/praw/) library
- [`fastmcp`](https://pypi.org/project/fastmcp/) library

### Installation

1. **Clone the Repository:**
    ```bash
    git clone [repository-url]
    cd reddit-mcp-server
    ```

2. **Install Dependencies:**
    ```bash
    pip install praw fastmcp
    ```

### Configuration

Set the following environment variables for Reddit API authentication:

| Environment Variable       | Description                                                     |
|----------------------------|-----------------------------------------------------------------|
| `REDDIT_CLIENT_ID`         | Your Reddit application's client ID.                            |
| `REDDIT_CLIENT_SECRET`     | Your Reddit application's client secret.                        |
| `REDDIT_USER_AGENT`        | Descriptive user agent (e.g., `python:futuregen:v1.0 (by u/YourUsername)`). |
| `REDDIT_REFRESH_TOKEN`     | PRAW refresh token for long-term script access.                 |

**Example:**
```python
import os

os.environ["REDDIT_CLIENT_ID"] = "VoDq1m6w4nmuLk7oDUmN8Q"
os.environ["REDDIT_CLIENT_SECRET"] = "rxSEa8e2uyFSK6cfrJVlAe_omhgsXQ"
os.environ["REDDIT_USER_AGENT"] = "python:futuregen:v1.0 (by u/Striking_Economy698)"
os.environ["REDDIT_REFRESH_TOKEN"] = "200334591410393-Uwlr-vfZ65KzOQGmmr2qCUV_TrT53w"



### Running the Server

```bash
python reddit_server.py
# The server is now running and ready to accept API calls.
###Available Tools (API Endpoints)
