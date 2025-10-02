
This document outlines the README for the Reddit MCP (Multi-Component Project) Server, a robust toolset built on PRAW and FastMCP for comprehensive Reddit interaction.

This project is a Python server designed to execute a wide range of Reddit actions—from retrieving post listings and user data to creating, editing, and moderating content—via a unified, API-like interface.

🚀 Getting Started
Prerequisites
Python 3.8+

The praw library (for Reddit API interaction)

The fastmcp library (for running the Multi-Component Project server)

Installation
Clone the Repository:

Bash

git clone [repository-url]
cd reddit-mcp-server
Install Dependencies:

Bash

pip install praw fastmcp
Configuration
The project requires authentication credentials to interact with the Reddit API. Set the following environment variables (as shown in the provided code snippet) in your environment or directly in the Python script.

Environment Variable	Description
REDDIT_CLIENT_ID	Your Reddit application's client ID.
REDDIT_CLIENT_SECRET	Your Reddit application's client secret.
REDDIT_USER_AGENT	A descriptive user agent string (e.g., python:futuregen:v1.0 (by u/YourUsername)).
REDDIT_REFRESH_TOKEN	A PRAW refresh token for script-based, long-term access without a username/password.

Export to Sheets
Example Configuration (from code):

Python

os.environ["REDDIT_CLIENT_ID"] = "VoDq1m6w4nmuLk7oDUmN8Q"
os.environ["REDDIT_CLIENT_SECRET"] = "rxSEa8e2uyFSK6cfrJVlAe_omhgsXQ"
os.environ["REDDIT_USER_AGENT"] = "python:futuregen:v1.0 (by u/Striking_Economy698)"
os.environ["REDDIT_REFRESH_TOKEN"] = "200334591410393-Uwlr-vfZ65KzOQGmmr2qCUV_TrT53w"
Running the Server
Start the FastMCP server from your terminal:

Bash

python reddit_server.py
# The server is now running and ready to accept API calls.
🛠️ Available Tools (API Endpoints)
The server exposes the following functions as callable tools for interacting with Reddit content and user data. Each function returns a dictionary with a successful boolean, a data payload, and an error string (if applicable).

Content Retrieval & Discovery
Tool Name	Description	Parameters
get_hot_posts	Retrieves the current hot posts from a specified subreddit.	subreddit, limit
retrieve_reddit_posts	Retrieves the current hot posts from a specified subreddit (alias for get_hot_posts).	subreddit, size
get_new_submissions	Retrieves the newest posts from a subreddit in chronological order.	subreddit, limit
get_top_posts	Retrieves the highest-scoring posts for a subreddit within a time frame.	subreddit, time_filter (day, week, etc.), limit
get_subreddit_listings	Retrieves posts based on various listing types (hot, top, new, controversial, rising).	subreddit, listing_type, time_filter (Optional), limit
get_gilded_content	Retrieves posts that have received awards (gilding) in a subreddit.	subreddit, limit
retrieve_specific_content	Retrieves detailed metadata for a specific post (t3_) or comment (t1_).	id (fullname)
retrieve_post_comments	Retrieves all comments (flattened) for a given Reddit post ID.	article (post ID)
search_across_subreddits	Searches for content across all of Reddit based on a query.	search_query, limit, sort

Export to Sheets
User & Community Info
Tool Name	Description	Parameters
get_user_info	Gets basic information (name, karma, creation date) about a Reddit user.	username
get_redditor_trophies	Retrieves the list of trophies awarded to a specified user.	username
get_user_comments	Retrieves the most recent comments made by a specified user.	username, limit
get_subreddit_details	Retrieves the title, subscriber count, and description for a subreddit.	subreddit
get_subreddit_sidebar	Retrieves the raw markdown content and description from a subreddit's sidebar.	subreddit
get_subreddit_rules	Retrieves the complete set of official rules for a specified subreddit.	subreddit
get_moderators	Retrieves the list of usernames for all moderators of a subreddit.	subreddit
search_subreddits	Searches for subreddit communities (not posts) matching a query.	query, limit
get_subreddits_by_topic	Retrieves a list of subreddits based on a specific topic or theme.	topic, limit
get_user_flair	Retrieves the flair assigned to a specific user in a subreddit.	subreddit, username
get_link_flair	Fetches the list of available link flairs for a given subreddit.	subreddit
get_blocked_users	Retrieves the list of users the authenticated account has blocked.	(None)
get_moderated_subs	Retrieves a list of all subreddits the authenticated user moderates.	limit
list_multireddits	Retrieves a list of all Multireddits created by the authenticated user.	(None)
get_multireddit_posts	Retrieves hot posts from a specific Multireddit.	multireddit_name, limit

Export to Sheets
✍️ Content Modification & Actions
Tool Name	Description	Parameters
create_reddit_post	Creates a new text (self) or link (link) post on a subreddit.		
subreddit, title, kind, text (for self), url (for link), flair_id (Optional) 

post_reddit_comment	Posts a comment, replying to an existing post (t3_) or comment (t1_).		
thing_id (fullname), text 


edit_reddit_content	Edits the body text of the authenticated user's own comment (t1_) or self-post (t3_).		
thing_id (fullname), text 

delete_reddit_comment	Deletes the authenticated user's own comment.		
id (fullname, e.g., t1_...) 

delete_reddit_post	Permanently deletes the authenticated user's own post.	id (short ID or fullname, e.g., t3_...)
vote_on_content	Casts an upvote (1), downvote (-1), or removes a vote (0) on a post or comment.	fullname, direction
send_private_message	Sends a private message to a specified Reddit user.	recipient, subject, message
send_mod_mail	Sends a message to the entire moderator team of a subreddit.	subreddit, subject, message
get_unread_messages	Retrieves a list of unread messages for the authenticated user.	limit

Export to Sheets
⚠️ Known Issues
The server output indicates a potential issue with the underlying PRAW connection:

reddit is blocking your account because of too many actions

This suggests the authenticated Reddit account may be temporarily rate-limited or blocked due to excessive API calls. Operations that create, edit, or vote on content may fail until the block is lifted.
