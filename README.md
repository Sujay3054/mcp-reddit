# Reddit MCP (Multi-Component Project) Server

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![PRAW Version](https://img.shields.io/badge/PRAW-Latest-orange.svg)](https://pypi.org/project/praw/)
[![FastMCP Version](https://img.shields.io/badge/FastMCP-Latest-brightgreen.svg)](https://pypi.org/project/fastmcp/)

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

- Python **3.8+**
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

| Environment Variable | Description |
| :--- | :--- |
| `REDDIT_CLIENT_ID` | Your Reddit application's client ID. |
| `REDDIT_CLIENT_SECRET` | Your Reddit application's client secret. |
| `REDDIT_USER_AGENT` | Descriptive user agent (e.g., `python:futuregen:v1.0 (by u/YourUsername)`). |
| `REDDIT_REFRESH_TOKEN` | PRAW refresh token for long-term script access. |

**Example PRAW Initialization:**
```python
import os
import praw

os.environ["REDDIT_CLIENT_ID"] = "VoDq1m6w4nmuLk7oDUmN8Q"
os.environ["REDDIT_CLIENT_SECRET"] = "rxSEa8e2uyFSK6cfrJVlAe_omhgsXQ"
os.environ["REDDIT_USER_AGENT"] = "python:futuregen:v1.0 (by u/Striking_Economy698)"
os.environ["REDDIT_REFRESH_TOKEN"] = "200334591410393-Uwlr-vfZ65KzOQGmmr2qCUV_TrT53w"

reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    refresh_token=os.environ["REDDIT_REFRESH_TOKEN"],
    user_agent=os.environ["REDDIT_USER_AGENT"]
)
'''

Running the Server
Start the FastMCP server:
python reddit_server.py
# The server is now running and ready to accept API calls.

🛠️ Available Tools (API Endpoints)
All tools return a structured JSON response:
{
  "successful": true/false,
  "data": {...},
  "error": "error message if any"
}

Content Retrieval & Discovery
| Tool Name                   | Description                                               | Parameters                                                     |
| --------------------------- | --------------------------------------------------------- | -------------------------------------------------------------- |
| `get_hot_posts`             | Retrieves hot posts from a subreddit.                     | `subreddit`, `limit`                                           |
| `retrieve_reddit_posts`     | Alias for `get_hot_posts`.                                | `subreddit`, `size`                                            |
| `get_new_submissions`       | Retrieves newest posts in chronological order.            | `subreddit`, `limit`                                           |
| `get_top_posts`             | Retrieves top posts in a time frame.                      | `subreddit`, `time_filter`, `limit`                            |
| `get_subreddit_listings`    | Retrieves posts by listing type (`hot`, `top`, etc.).     | `subreddit`, `listing_type`, `time_filter (optional)`, `limit` |
| `get_gilded_content`        | Retrieves posts with awards.                              | `subreddit`, `limit`                                           |
| `retrieve_specific_content` | Retrieves metadata for a post (`t3_`) or comment (`t1_`). | `id`                                                           |
| `retrieve_post_comments`    | Retrieves all comments for a post.                        | `article` (post ID)                                            |
| `search_across_subreddits`  | Searches Reddit globally based on a query.                | `search_query`, `limit`, `sort`                                |

👥 User & Community Info
| Tool Name                 | Description                                              | Parameters                  |
| ------------------------- | -------------------------------------------------------- | --------------------------- |
| `get_user_info`           | Gets basic info about a user.                            | `username`                  |
| `get_redditor_trophies`   | Retrieves a user's trophies.                             | `username`                  |
| `get_user_comments`       | Retrieves recent comments by a user.                     | `username`, `limit`         |
| `get_subreddit_details`   | Gets title, subscribers, and description of a subreddit. | `subreddit`                 |
| `get_subreddit_sidebar`   | Gets raw markdown content from sidebar.                  | `subreddit`                 |
| `get_subreddit_rules`     | Retrieves subreddit rules.                               | `subreddit`                 |
| `get_moderators`          | Lists moderators of a subreddit.                         | `subreddit`                 |
| `search_subreddits`       | Searches for subreddit communities.                      | `query`, `limit`            |
| `get_subreddits_by_topic` | Retrieves subreddits by topic.                           | `topic`, `limit`            |
| `get_user_flair`          | Gets a user's flair in a subreddit.                      | `subreddit`, `username`     |
| `get_link_flair`          | Fetches link flairs for a subreddit.                     | `subreddit`                 |
| `get_blocked_users`       | Retrieves blocked users.                                 | (None)                      |
| `get_moderated_subs`      | Lists subreddits moderated by the authenticated user.    | `limit`                     |
| `list_multireddits`       | Lists all Multireddits of the authenticated user.        | (None)                      |
| `get_multireddit_posts`   | Retrieves hot posts from a Multireddit.                  | `multireddit_name`, `limit` |

✍️ Content Modification & Actions
| Tool Name               | Description                                                  | Parameters                                                                               |
| ----------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| `create_reddit_post`    | Creates a text (`self`) or link (`link`) post.               | `subreddit`, `title`, `kind`, `text` (for self), `url` (for link), `flair_id (optional)` |
| `post_reddit_comment`   | Posts a comment in reply to post (`t3_`) or comment (`t1_`). | `thing_id`, `text`                                                                       |
| `edit_reddit_content`   | Edits authenticated user's comment or post.                  | `thing_id`, `text`                                                                       |
| `delete_reddit_comment` | Deletes authenticated user's comment.                        | `id`                                                                                     |
| `delete_reddit_post`    | Deletes authenticated user's post.                           | `id`                                                                                     |
| `vote_on_content`       | Upvote (`1`), downvote (`-1`), or remove vote (`0`).         | `fullname`, `direction`                                                                  |
| `send_private_message`  | Sends a private message to a user.                           | `recipient`, `subject`, `message`                                                        |
| `send_mod_mail`         | Sends message to subreddit moderators.                       | `subreddit`, `subject`, `message`                                                        |
| `get_unread_messages`   | Retrieves unread messages.                                   | `limit`                                                                                  |

⚠️ Known Issues
The server may occasionally hit Reddit API rate limits:

reddit is blocking your account because of too many actions

Operations that create, edit, or vote on content may fail temporarily until the block is lifted.


