Reddit MCP Server
Component	Detail
Project Name	Reddit MCP Server
Version	v1.0
Status	Production Ready
Completion Date	September 2025 (Estimated)

Export to Sheets
🎯 Project Overview
Objective
To create a Model Context Protocol (MCP) server for Reddit, utilizing the PRAW (Python Reddit API Wrapper) library to expose comprehensive Reddit functionality as callable tools for AI assistants. The goal is to enable content retrieval, user information lookup, and basic content creation/management actions.

Key Features & Achievements

29 Production-Ready Tools for wide-ranging Reddit interactions.


Utilizes 

PRAW for stable and efficient interaction with the Reddit API.


Includes tools for 

Post and Comment Management (Create, Edit, Delete, Vote).




Comprehensive Information Retrieval for users, subreddits, and post listings (Hot, New, Top, Controversial).





Handles 

Authentication via Refresh Token for script-based, long-term access.



Error Handling with structured JSON responses for failed operations.


🏗️ Technical Architecture
Technology Stack
Component	Detail
Language	
Python (using 

praw and fastmcp libraries) 


Framework		
FastMCP (for serving the tools) 


API Client		
PRAW (Python Reddit API Wrapper) 


Authentication	
OAuth with 

Refresh Token 



Export to Sheets
Configuration and Setup
The server uses environment variables to configure the PRAW client for OAuth authentication:

Python

# Environment variables must be set for the following keys:
os.environ["REDDIT_CLIENT_ID"] = "VoDq1m6w4nmuLk7oDUmN8Q"
os.environ["REDDIT_CLIENT_SECRET"] = "rxSEa8e2uyFSK6cfrJVlAe_omhgsXQ"
os.environ["REDDIT_USER_AGENT"] = "python:futuregen:v1.0 (by u/Striking_Economy698)"
os.environ["REDDIT_REFRESH_TOKEN"] = "200334591410393-Uwlr-vfZ65KzOQGmmr2qCUV_TrT53w"
Running the Server
Bash

python reddit_server.py

(Note: The server output indicates a potential rate-limiting issue: "reddit is blocking your account because of too many actions").


🛠️ Feature Implementation (29 Tools)
The following core functionalities are exposed as MCP tools:

Content Creation & Management
Tool Name	Description	Example Result
create_reddit_post	
Creates a new self or link post.



post_id: "1nryq14" 

post_reddit_comment	
Posts a comment to a post (

t3_) or another comment (t1_).




comment_id: "nh82n8k" 

edit_reddit_content	
Edits the text of an owned post or comment.



status: "Content ID 't3_1nrzjrn' was successfully updated." 

delete_reddit_comment	
Deletes an owned comment by ID.



status: "Comment with ID 't1_ngi200e' was successfully deleted." 

delete_reddit_post	
Permanently deletes an owned post.


N/A
vote_on_content	
Casts an upvote, downvote, or clears a vote.


N/A

Export to Sheets
Content Retrieval & Discovery
Tool Name	Description	Example Result
get_hot_posts	
Retrieves the hottest posts from a subreddit.



Lists posts from 

r/AskReddit 

get_top_posts	
Retrieves the highest-scoring posts filtered by time.



Top posts for 

time_filter: "week" 

get_new_submissions	
Retrieves the newest posts from a subreddit.



Listings include posts by 

markyty04 and Silly-avocatoe 

get_subreddit_listings	
Retrieves posts by type (

controversial, rising, etc.).



Controversial posts for 

r/science 

retrieve_reddit_posts	
Retrieves hot posts from a subreddit (similar to 

get_hot_posts).



Posts from an unspecified subreddit 

search_across_subreddits	
Searches for content across all of Reddit.



Finds posts in 

r/Luthier and r/TestersCommunity 

retrieve_specific_content	
Gets metadata for a specific post or comment by fullname (

t1_ or t3_).



Details for post 

1nrzhi 

retrieve_post_comments	
Retrieves all comments for a post ID.



Returns an empty list of comments 

get_gilded_content	
Retrieves posts that have received awards.



Returns an empty list of gilded posts 


Export to Sheets
User & Subreddit Information
Tool Name	Description	Example Result
get_user_info	
Gets basic user details (karma, creation date).



Karma of 

1 for user TinyFix8992 

get_redditor_trophies	
Retrieves a user's trophy list.



Shows the 

"New User" trophy 

get_user_comments	
Retrieves a user's recent comment history.


N/A
get_subreddit_details	
Gets core subreddit metadata (subscribers, description).



Details for 

r/AskReddit with 57,050,504 subscribers 

get_subreddit_rules	
Retrieves the complete set of official rules for a subreddit.



Lists 11 rules for 

r/AskReddit 

get_subreddit_sidebar	
Retrieves the raw markdown content and description from a subreddit's sidebar.



Markdown content for 

r/AskReddit 

get_moderators	
Lists all moderator usernames for a specified subreddit.



Lists 29 moderators for 

r/AskReddit 

get_link_flair	
Fetches the available post flair templates for a subreddit.



Returns an empty list of flairs 

search_subreddits	
Searches for subreddit communities (not posts).



Finds 

r/Python, r/PythonLearning, etc. 

get_subreddits_by_topic	
Finds related subreddits based on a topic.



Finds subreddits related to 

"Artificial Intelligence" 

list_multireddits	
Retrieves the authenticated user's Multireddits.



Returns an empty list 

get_blocked_users	
Retrieves the list of users the authenticated account has blocked.

Returns a list with a count of 0 

get_moderated_subs	
Retrieves subreddits the authenticated user moderates.


N/A
get_unread_messages	
Retrieves unread inbox items.


N/A
get_user_flair	
Retrieves a user's flair in a specific subreddit.


N/A
get_multireddit_posts	
Retrieves hot posts from a specific Multireddit.


N/A
send_private_message	
Sends a private message to a specified user.


N/A
send_mod_mail	
Sends a message to a subreddit's moderator team.


N/A
get_submission_details	
Gets complete metadata for a single post by short ID.


Details for a post titled "New Post for Final Comment Test" 


⚠️ Known Issues
The server output indicates a potential issue with the underlying PRAW connection:

reddit is blocking your account because of too many actions

This suggests the authenticated Reddit account may be temporarily rate-limited or blocked due to excessive API calls. Operations that create, edit, or vote on content may fail until the block is lifted.

