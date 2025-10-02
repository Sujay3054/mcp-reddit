import os
import praw
from mcp.server.fastmcp import FastMCP, tools as mcp_tools
from typing import Optional
# Environment variables
os.environ["REDDIT_CLIENT_ID"] = "VoDq1m6w4nmuLk7oDUmN8Q"
os.environ["REDDIT_CLIENT_SECRET"] = "rxSEa8e2uyFSK6cfrJVlAe_omhgsXQ"
os.environ["REDDIT_USER_AGENT"] = "python:futuregen:v1.0 (by u/Striking_Economy698)"
os.environ["REDDIT_REFRESH_TOKEN"] = "200334591410393-Uwlr-vfZ65KzOQGmmr2qCUV_TrT53w"

# PRAW using refresh token
reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"].strip(),
    client_secret=os.environ["REDDIT_CLIENT_SECRET"].strip(),
    refresh_token=os.environ["REDDIT_REFRESH_TOKEN"].strip(),
    user_agent=os.environ["REDDIT_USER_AGENT"].strip()
)

# MCP server must be global
mcp = FastMCP("reddit-composio-server")

@mcp.tool()
def get_hot_posts(subreddit: str, limit: int = 5):
    posts = []
    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        posts.append({
            "title": submission.title,
            "url": submission.url,
            "score": submission.score,
            "author": str(submission.author)
        })
    return {"successful": True, "data": posts}


@mcp.tool()
def get_user_info(username: str):
    """
    Get basic information about a Reddit user.
    """
    try:
        user = reddit.redditor(username)
        if user.name:
            return {
                "successful": True,
                "data": {
                    "name": user.name,
                    "karma": user.link_karma + user.comment_karma,
                    "created_utc": user.created_utc
                }
            }
        return {"successful": False, "error": f"Could not retrieve info for user {username}"}
    except Exception as e:
        return {"successful": False, "error": str(e)}
@mcp.tool()
def create_reddit_post(subreddit: str, title: str, kind: str, text: Optional[str] = None, url: Optional[str] = None, flair_id: Optional[str] = None):
    """
    Creates a new text ('self') or link post ('link') on a specified subreddit.
    
    The 'text' parameter is used for self-posts, and 'url' is used for link posts.
    """
    
    # 1. Prepare PRAW submission arguments
    submission_args = {}
    if flair_id:
        submission_args['flair_id'] = flair_id
        
    try:
        if kind.lower() == 'self':
            if not text:
                return {"successful": False, "error": "For 'self' posts, the 'text' parameter is required."}
            
            # Submit a self-post (text post)
            submission = reddit.subreddit(subreddit).submit(
                title=title, 
                selftext=text, 
                **submission_args
            )
        
        elif kind.lower() == 'link':
            if not url:
                return {"successful": False, "error": "For 'link' posts, the 'url' parameter is required."}
            
            # Submit a link post
            submission = reddit.subreddit(subreddit).submit(
                title=title, 
                url=url, 
                **submission_args
            )
            
        else:
            return {"successful": False, "error": "Invalid value for 'kind'. Must be 'self' or 'link'."}

        # 2. Return success status and the new post's ID
        return {
            "successful": True, 
            "data": {
                "post_id": submission.id, 
                "full_url": submission.url
            },
            "error": ""
        }

    except Exception as e:
        return {"successful": False, "data": {}, "error": str(e)}

# Re-run your server after adding this code!
# python reddit_server.py
@mcp.tool()
def delete_reddit_comment(id: str):
    """
    Deletes a reddit comment, identified by its fullname ID (e.g., t1_abcxyz), 
    if the comment was authored by the authenticated user.
    """
    
    # 1. Check for 't1_' prefix (required by PRAW for full comment ID)
    if not id.startswith('t1_'):
        # PRAW often works if you pass the short ID, but it's best practice to use the fullname.
        # This check is a safeguard for the user.
        pass
    
    try:
        # 2. Access the comment object and call the delete method
        comment = reddit.comment(id)
        comment.delete()
        
        # 3. Return success
        return {
            "successful": True,
            "data": {"status": f"Comment with ID '{id}' was successfully deleted."},
            "error": ""
        }

    except Exception as e:
        # PRAW raises exceptions for permissions issues, not found errors, etc.
        return {
            "successful": False,
            "data": {},
            "error": f"Failed to delete comment: {str(e)}"
        }

@mcp.tool()
def delete_reddit_post(id: str):
    """
    Permanently deletes a reddit post by its fullname ID (e.g., t3_abcxyz), 
    provided the authenticated user has deletion permissions for that post.
    """
    
    try:
        # PRAW uses the submission() method for posts
        submission = reddit.submission(id)
        submission.delete()
        
        # Return success
        return {
            "successful": True,
            "data": {"status": f"Post with ID '{id}' was successfully deleted."},
            "error": ""
        }

    except Exception as e:
        # Catch exceptions (e.g., if the post doesn't exist, is not owned by the user, etc.)
        return {
            "successful": False,
            "data": {},
            "error": f"Failed to delete post: {str(e)}"
        }

@mcp.tool()
def edit_reddit_content(thing_id: str, text: str):
    """
    Edits the body text of the authenticated user's own existing comment (t1_) or 
    self-post (t3_) on reddit. Cannot edit link posts or titles.
    """
    
    try:
        # Determine the content type based on the ID prefix
        if thing_id.startswith('t1_'):
            # It's a comment
            item = reddit.comment(thing_id)
        elif thing_id.startswith('t3_'):
            # It's a submission/post
            item = reddit.submission(thing_id)
        else:
            return {
                "successful": False, 
                "error": "Invalid 'thing_id' format. Must be a comment (t1_...) or post (t3_...) fullname."
            }
            
        # Edit the content
        item.edit(text)
        
        # Return success
        return {
            "successful": True,
            "data": {"status": f"Content ID '{thing_id}' was successfully updated."},
            "error": ""
        }

    except Exception as e:
        # Catch exceptions (e.g., trying to edit a link post, not owning the content, or bad ID)
        return {
            "successful": False,
            "data": {},
            "error": f"Failed to edit content: {str(e)}. Ensure you own the post/comment and it's not a link post."
        }

@mcp.tool()
def get_link_flair(subreddit: str):
    """
    Fetches the list of available link flairs (i.e., post flairs) for a given subreddit.
    Returns the ID and text needed for post creation/editing.
    """
    
    try:
        # PRAW method to retrieve link flair templates
        subreddit_obj = reddit.subreddit(subreddit)
        
        flair_list = []
        # The link_templates attribute returns a list of dictionaries
        for template in subreddit_obj.flair.link_templates:
            # We extract the ID and text, which are necessary for the user
            flair_list.append({
                "flair_id": template['flair_template_id'],
                "flair_text": template['flair_text']
            })
            
        return {
            "successful": True,
            "data": flair_list,
            "error": ""
        }

    except Exception as e:
        # Catches exceptions like 'SubredditNotFound' or PRAW errors
        return {
            "successful": False,
            "data": {},
            "error": f"Failed to retrieve flairs for r/{subreddit}: {str(e)}. Check if the subreddit exists."
        }

@mcp.tool()
def post_reddit_comment(thing_id: str, text: str):
    """
    Posts a comment on reddit, replying to an existing and accessible submission (post) or another comment.
    The 'thing_id' must be the fullname (t3_ for post, t1_ for comment).
    """
    
    try:
        # Determine the content type based on the ID prefix to get the correct object
        if thing_id.startswith('t3_'):
            # It's a submission/post
            parent = reddit.submission(thing_id)
        elif thing_id.startswith('t1_'):
            # It's a comment
            parent = reddit.comment(thing_id)
        else:
            return {
                "successful": False, 
                "error": "Invalid 'thing_id' format. Must be a post (t3_...) or comment (t1_...) fullname."
            }
            
        # Reply to the parent object
        new_comment = parent.reply(text)
        
        # Return success status and details of the new comment
        return {
            "successful": True,
            "data": {
                "comment_id": new_comment.id,
                "fullname": new_comment.fullname,
                "permalink": new_comment.permalink
            },
            "error": ""
        }

    except Exception as e:
        # Catch exceptions (e.g., trying to comment on a locked post, permissions error)
        return {
            "successful": False,
            "data": {},
            "error": f"Failed to post comment: {str(e)}. Ensure the thing_id is correct and the content is not locked."
        }

@mcp.tool()
def retrieve_post_comments(article: str):
    """
    Retrieves all comments for a reddit post given its article ID (e.g., a post ID like 't3_abcxyz').
    Nested replies are returned as raw PRAW objects requiring further parsing.
    """
    
    try:
        # PRAW uses the submission() method with the post ID
        submission = reddit.submission(article)
        
        # Ensure PRAW loads all comments, not just the top level ones
        submission.comments.replace_more(limit=None)
        
        # Flatten the comments for easy iteration
        comments_list = submission.comments.list()
        
        retrieved_comments = []
        for comment in comments_list:
            # Check for a valid comment object (prevents issues with nested objects/MoreComments)
            if hasattr(comment, 'author'):
                retrieved_comments.append({
                    "comment_id": comment.id,
                    "author": str(comment.author),
                    "body": comment.body,
                    "score": comment.score,
                    "permalink": comment.permalink
                })

        # Return success status and the list of comments
        return {
            "successful": True,
            "data": retrieved_comments,
            "error": ""
        }

    except Exception as e:
        # Catch exceptions like 'NotFound' or PRAW errors
        return {
            "successful": False,
            "data": {},
            "error": f"Failed to retrieve comments for article ID '{article}': {str(e)}. Ensure the post ID is correct and the post is public."
        }

@mcp.tool()
def retrieve_reddit_posts(subreddit: str, size: int = 5):
    """
    Retrieves the current hot posts from a specified, publicly accessible subreddit.
    The 'size' parameter controls the number of posts returned.
    """
    posts = []
    try:
        # PRAW uses 'limit' internally, so we pass the 'size' parameter to it
        for submission in reddit.subreddit(subreddit).hot(limit=size):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "url": submission.url,
                "score": submission.score,
                "author": str(submission.author)
            })
        
        return {
            "successful": True, 
            "data": posts,
            "error": ""
        }

    except Exception as e:
        # Catch exceptions like 'SubredditNotFound'
        return {
            "successful": False,
            "data": {},
            "error": f"Failed to retrieve posts for r/{subreddit}: {str(e)}. Check if the subreddit exists."
        }

@mcp.tool()
def retrieve_specific_content(id: str):
    """
    Retrieves detailed information for a specific reddit comment or post using its fullname (t1_ or t3_).
    """
    
    try:
        # Use reddit.info() to retrieve the item, which handles both posts and comments
        item = next(reddit.info(fullnames=[id]))

        # Safely determine and extract data
        data = {
            "id": item.id,
            "fullname": item.fullname,
            "object_type": item.fullname.split('_')[0], # t3 for post, t1 for comment
            "score": getattr(item, 'score', None),
            "author": str(getattr(item, 'author', 'Unknown')),
            "created_utc": getattr(item, 'created_utc', None)
        }

        # Handle Post-specific attributes (Submission)
        if data["object_type"] == 't3':
            data['title'] = getattr(item, 'title', None)
            data['text_body'] = getattr(item, 'selftext', None)
        
        # Handle Comment-specific attributes
        elif data["object_type"] == 't1':
            data['body'] = getattr(item, 'body', None)

        return {
            "successful": True,
            "data": data,
            "error": ""
        }

    except StopIteration:
        return {
            "successful": False,
            "data": {},
            "error": f"Content not found for ID: {id}. Check the ID format (t1_... or t3_...)."
        }
    except Exception as e:
        return {
            "successful": False,
            "data": {},
            "error": f"Failed to retrieve content: {str(e)}"
        }

@mcp.tool()
def search_across_subreddits(search_query: str, limit: int = 5, restrict_sr: bool = False, sort: str = 'relevance'):
    """
    Searches reddit for content (e.g., posts, comments) using a query across all of Reddit.
    'restrict_sr' is included in the signature but ignored in the PRAW call to prevent error.
    """
    results = []
    
    try:
        # The fix is here: The search call NO LONGER includes the 'restrict_sr' argument
        search_results = reddit.subreddit('all').search(
            query=search_query,
            sort=sort,
            limit=limit,
            syntax='lucene'
        )

        for item in search_results:
            if hasattr(item, 'title'):
                results.append({
                    "type": "post",
                    "title": item.title,
                    "id": item.id,
                    "subreddit": str(item.subreddit),
                    "score": item.score,
                    "created_utc": item.created_utc
                })
            
        return {
            "successful": True,
            "data": results,
            "error": ""
        }

    except Exception as e:
        return {
            "successful": False,
            "data": {},
            "error": f"Failed to perform search: {str(e)}. Check the search query for invalid characters."
        }

@mcp.tool()
def get_subreddit_details(subreddit: str):
    """
    Retrieves the description, subscriber count, and creation date for a specified subreddit.
    """
    try:
        sub = reddit.subreddit(subreddit)
        return {
            "successful": True,
            "data": {
                "name": str(sub.display_name),
                "title": getattr(sub, 'title', None),
                "subscribers": getattr(sub, 'subscribers', None),
                "created_utc": getattr(sub, 'created_utc', None),
                "public_description": getattr(sub, 'public_description', None)
            }
        }
    except Exception as e:
        return {"successful": False, "error": str(e)}

@mcp.tool()
def send_private_message(recipient: str, subject: str, message: str):
    """
    Sends a private message to a specified Reddit user. Requires the authenticated user's permission.
    """
    try:
        reddit.redditor(recipient).message(subject=subject, body=message)
        return {
            "successful": True,
            "data": {"status": f"Message sent to {recipient}."},
            "error": ""
        }
    except Exception as e:
        return {"successful": False, "error": f"Failed to send message: {str(e)}"}

@mcp.tool()
def get_new_submissions(subreddit: str, limit: int = 5):
    """
    Retrieves the newest submissions (posts) from a subreddit in chronological order.
    This is ideal for monitoring or real-time processing.
    """
    try:
        posts = []
        # PRAW method for the 'new' listing
        for submission in reddit.subreddit(subreddit).new(limit=limit):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "url": submission.url,
                "created_utc": submission.created_utc,
                "author": str(submission.author)
            })
        return {"successful": True, "data": posts}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve new posts: {str(e)}"}

@mcp.tool()
def get_user_comments(username: str, limit: int = 10):
    """
    Retrieves the most recent comments made by a specified user.
    """
    try:
        comments = []
        # PRAW method to access a user's comment history
        for comment in reddit.redditor(username).comments.new(limit=limit):
            comments.append({
                "comment_id": comment.id,
                "subreddit": str(comment.subreddit),
                "body": comment.body,
                "score": comment.score,
                "created_utc": comment.created_utc
            })
        return {"successful": True, "data": comments}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve comments for {username}: {str(e)}"}

@mcp.tool()
def get_top_posts(subreddit: str, time_filter: str = 'day', limit: int = 10):
    """
    Retrieves the highest-scoring posts from a subreddit within a specified time frame (e.g., 'hour', 'week', 'all').
    """
    if time_filter not in ['hour', 'day', 'week', 'month', 'year', 'all']:
        return {"successful": False, "error": "Invalid time_filter. Use 'day', 'week', 'month', 'year', or 'all'."}
        
    try:
        posts = []
        # PRAW method to access the 'top' listing
        for submission in reddit.subreddit(subreddit).top(time_filter=time_filter, limit=limit):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "score": submission.score,
                "time_filter": time_filter,
                "author": str(submission.author)
            })
        return {"successful": True, "data": posts}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve top posts: {str(e)}"}

@mcp.tool()
def get_submission_details(submission_id: str):
    """
    Retrieves the complete metadata for a single post (submission) using its short ID (e.g., '1nrzroo').
    """
    try:
        # PRAW method to access a submission by its short ID
        submission = reddit.submission(submission_id)
        
        return {
            "successful": True,
            "data": {
                "title": submission.title,
                "subreddit": str(submission.subreddit),
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
                "is_self": submission.is_self
            },
            "error": None
        }
    except Exception as e:
        return {"successful": False, "error": f"Submission lookup failed: {str(e)}"}

@mcp.tool()
def vote_on_content(fullname: str, direction: int = 1):
    """
    Casts a vote on a Reddit submission (t3_) or comment (t1_) by its fullname.
    'direction' must be: 1 (upvote), -1 (downvote), or 0 (remove vote).
    """
    try:
        # PRAW handles both comments and submissions here:
        thing = reddit.comment(fullname) if fullname.startswith('t1_') else reddit.submission(fullname)
        
        if direction == 1:
            thing.upvote()
        elif direction == -1:
            thing.downvote()
        elif direction == 0:
            thing.clear_vote()
        else:
            return {"successful": False, "error": "Invalid direction. Must be 1, -1, or 0."}

        return {"successful": True, "data": {"status": f"Vote of {direction} cast on {fullname}."}, "error": None}
    except Exception as e:
        return {"successful": False, "error": f"Voting failed: {str(e)}"}

@mcp.tool()
def vote_on_content(fullname: str, direction: int = 1):
    """
    Casts a vote on a Reddit submission (t3_) or comment (t1_) by its fullname.
    'direction' must be: 1 (upvote), -1 (downvote), or 0 (remove vote).
    """
    try:
        # PRAW handles both comments and submissions here:
        thing = reddit.comment(fullname) if fullname.startswith('t1_') else reddit.submission(fullname)
        
        if direction == 1:
            thing.upvote()
        elif direction == -1:
            thing.downvote()
        elif direction == 0:
            thing.clear_vote()
        else:
            return {"successful": False, "error": "Invalid direction. Must be 1, -1, or 0."}

        return {"successful": True, "data": {"status": f"Vote of {direction} cast on {fullname}."}, "error": None}
    except Exception as e:
        return {"successful": False, "error": f"Voting failed: {str(e)}"}

@mcp.tool()
def search_subreddits(query: str, limit: int = 10):
    """
    Searches for and retrieves a list of subreddit communities (not posts) matching a query in their name or description.
    """
    try:
        subreddits = []
        # PRAW method to search for subreddits (communities)
        for sub in reddit.subreddits.search(query, limit=limit):
            subreddits.append({
                "name": str(sub.display_name),
                "subscribers": sub.subscribers,
                "public_description": sub.public_description
            })
        return {"successful": True, "data": subreddits}
    except Exception as e:
        return {"successful": False, "error": f"Subreddit search failed: {str(e)}"}

@mcp.tool()
def get_redditor_trophies(username: str):
    """
    Retrieves the list of trophies and achievements awarded to a specified user. (Public data).
    """
    try:
        user = reddit.redditor(username)
        trophies = []
        
        # The fix is here: using getattr() to safely access attributes
        for trophy in user.trophies():
            trophies.append({
                "name": getattr(trophy, 'name', 'N/A'),
                "description": getattr(trophy, 'description', 'No description'),
                "icon_url": getattr(trophy, 'icon_url', None) # This handles the missing attribute error
            })
        return {"successful": True, "data": trophies}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve trophies for {username}: {str(e)}"}

@mcp.tool()
def get_subreddit_rules(subreddit: str):
    """
    Retrieves the complete set of official rules for a specified subreddit.
    Ideal for agents needing to verify content compliance.
    """
    try:
        # PRAW method to access the rules listing and its data (which is a dictionary)
        # The correct way to access the underlying rule data is to call the rules() method.
        rules_data = reddit.subreddit(subreddit).rules()
        
        # The final rules list is often stored under the 'rules' key in the returned dictionary
        rule_list = []
        for rule in rules_data.get('rules', []):
            rule_list.append({
                "short_name": rule.get('short_name'),
                "description": rule.get('description'),
                "created_utc": rule.get('created_utc'),
                "violation_reason": rule.get('violation_reason') # Using .get() is safe here
            })
        
        return {"successful": True, "data": rule_list, "error": None}
    except Exception as e:
        # PRAW raises exceptions for permissions issues (403) or not found errors
        return {"successful": False, "data": {}, "error": f"Failed to retrieve rules for r/{subreddit}: {str(e)}"}

@mcp.tool()
def get_subreddit_listings(subreddit: str, listing_type: str = 'hot', time_filter: Optional[str] = None, limit: int = 10):
    """
    Retrieves posts from a specified subreddit based on a listing type (hot, top, new, controversial, rising).
    Supports time_filter ('day', 'week', 'all') for 'top' and 'controversial' listings.
    """
    listing_type = listing_type.lower()
    if listing_type not in ['hot', 'top', 'new', 'rising', 'controversial']:
        return {"successful": False, "error": "Invalid listing_type. Use 'hot', 'top', 'new', 'rising', or 'controversial'."}
        
    try:
        sub = reddit.subreddit(subreddit)
        
        # Determine the correct PRAW method to call
        if listing_type == 'hot':
            submissions = sub.hot(limit=limit)
        elif listing_type == 'new':
            submissions = sub.new(limit=limit)
        elif listing_type == 'rising':
            submissions = sub.rising(limit=limit)
        elif listing_type == 'top':
            submissions = sub.top(time_filter=time_filter or 'day', limit=limit)
        elif listing_type == 'controversial':
            submissions = sub.controversial(time_filter=time_filter or 'day', limit=limit)
        
        posts = [{
            "title": s.title, 
            "id": s.id, 
            "score": s.score, 
            "author": str(s.author),
            "listing_type": listing_type
        } for s in submissions]
        
        return {"successful": True, "data": posts}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve {listing_type} posts for r/{subreddit}: {str(e)}"}

@mcp.tool()
def send_mod_mail(subreddit: str, subject: str, message: str):
    """
    Sends a message to the entire moderator team of a specified subreddit. 
    Requires the authenticated user to be a moderator of the target subreddit.
    """
    try:
        # PRAW method to send a message to the subreddit's moderation team
        reddit.subreddit(subreddit).message(
            subject=subject, 
            message=message
        )
        return {"successful": True, "data": {"status": f"Modmail sent successfully to moderators of r/{subreddit}."}, "error": None}
    except Exception as e:
        return {"successful": False, "error": f"Failed to send modmail: {str(e)}"}

@mcp.tool()
def get_subreddit_sidebar(subreddit: str):
    """
    Retrieves the raw markdown content and description from a subreddit's sidebar.
    """
    try:
        sub = reddit.subreddit(subreddit)
        return {
            "successful": True,
            "data": {
                "description_md": getattr(sub, 'description', None), # Markdown description
                "public_description": getattr(sub, 'public_description', None), # Short public description
                "subscribers": getattr(sub, 'subscribers', None)
            },
            "error": None
        }
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve sidebar content for r/{subreddit}: {str(e)}"}

@mcp.tool()
def get_subreddits_by_topic(topic: str, limit: int = 10):
    """
    Retrieves a list of subreddit communities based on a specific topic or theme.
    """
    try:
        subreddits = []
        # PRAW method to get subreddits recommended based on a query
        for sub in reddit.subreddits.search(topic, limit=limit):
            subreddits.append({
                "name": str(sub.display_name),
                "subscribers": sub.subscribers,
                "public_description": sub.public_description
            })
        return {"successful": True, "data": subreddits}
    except Exception as e:
        return {"successful": False, "error": f"Failed to search subreddits by topic: {str(e)}"}

@mcp.tool()
def get_moderators(subreddit: str):
    """
    Retrieves the complete list of usernames for all moderators of a specified subreddit.
    """
    try:
        # PRAW method to get the list of moderators
        mod_list = [str(mod) for mod in reddit.subreddit(subreddit).moderator()]
        
        return {
            "successful": True,
            "data": {"moderators": mod_list, "count": len(mod_list)},
            "error": None
        }
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve moderators for r/{subreddit}: {str(e)}"}

@mcp.tool()
def get_user_flair(subreddit: str, username: str):
    """
    Retrieves the flair text and CSS class assigned to a specific user in a given subreddit.
    """
    try:
        # PRAW returns an iterable (or a list of one dictionary)
        flair_generator = reddit.subreddit(subreddit).flair(username=username)
        
        # Convert the single result from the generator into a dictionary (the safe way)
        flair_data_list = list(flair_generator)
        
        if not flair_data_list:
             return {"successful": True, "data": {"status": "User has no flair set in this subreddit."}, "error": None}

        # The first item in the list is the data dictionary we need
        flair_dict = flair_data_list[0]
        
        return {
            "successful": True,
            "data": {
                # Use .get() method to safely handle missing keys in the dictionary
                "username": flair_dict.get('user'),
                "flair_text": flair_dict.get('flair_text'),
                "flair_css_class": flair_dict.get('flair_css_class')
            },
            "error": None
        }

    except Exception as e:
        return {"successful": False, "data": {}, "error": f"Failed to retrieve flair for {username} in r/{subreddit}: {str(e)}"}

@mcp.tool()
def get_gilded_content(subreddit: str, limit: int = 10):
    """
    Retrieves a list of posts that have received awards (gilding) by filtering top posts 
    on the specified subreddit. This is a more stable method than the direct .gilded() call.
    """
    try:
        gilded_items = []
        # Stabilized method: Get the top posts and filter for awarded items (PRAW handles the filtering implicitly)
        for item in reddit.subreddit(subreddit).top(limit=limit, time_filter='all'):
            if item.total_awards_received > 0:
                gilded_items.append({
                    "type": "Submission",
                    "title": item.title,
                    "author": str(item.author),
                    "score": item.score,
                    "awards_count": item.total_awards_received
                })
        
        return {"successful": True, "data": gilded_items, "error": None}
        
    except Exception as e:
        # Catch exceptions like 'SubredditNotFound'
        return {"successful": False, "error": f"Failed to retrieve gilded content: {str(e)}"}

@mcp.tool()
def list_multireddits():
    """
    Retrieves a list of all Multireddits (Custom Feeds) created by the authenticated user.
    """
    try:
        multis = []
        # PRAW method to access the authenticated user's multireddit list
        for multi in reddit.user.multireddits():
            multis.append({
                "name": multi.display_name,
                "path": multi.path,
                "visibility": multi.visibility,
                "subreddits": [str(sub) for sub in multi.subreddits]
            })
        return {"successful": True, "data": multis, "error": None}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve multireddits: {str(e)}"}

@mcp.tool()
def get_multireddit_posts(multireddit_name: str, limit: int = 10):
    """
    Retrieves hot posts from a specific Multireddit (Custom Feed).
    """
    try:
        posts = []
        # PRAW method to access a multireddit's submissions
        multi = reddit.multireddit(reddit.user.me().name, multireddit_name)
        
        for submission in multi.hot(limit=limit):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "subreddit": str(submission.subreddit),
                "score": submission.score
            })
        return {"successful": True, "data": posts, "error": None}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve posts from multireddit '{multireddit_name}': {str(e)}"}

@mcp.tool()
def get_blocked_users():
    """
    Retrieves the complete list of users the authenticated account has blocked.
    """
    try:
        blocked_users = []
        # PRAW method to access the authenticated user's blocked list
        for user in reddit.user.blocked():
            blocked_users.append({
                "username": str(user.name),
                "id": str(user.id)
            })
        return {"successful": True, "data": {"blocked_users": blocked_users, "count": len(blocked_users)}, "error": None}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve blocked users: {str(e)}"}

@mcp.tool()
def get_moderated_subs(limit: int = 25):
    """
    Retrieves a list of all subreddits the authenticated user is a moderator of.
    """
    try:
        subs = []
        # Final, stable fix: Access the moderator_of generator directly from the current user object
        for sub in reddit.user.me().moderator_of(limit=limit):
            subs.append({
                "name": str(sub.display_name),
                "subscribers": sub.subscribers,
                "is_moderator": True
            })
        return {"successful": True, "data": subs, "error": None}
    except Exception as e:
        # This will now catch the AttributeError if the PRAW object fails to load entirely.
        return {"successful": False, "error": f"Failed to retrieve moderated subreddits: {str(e)}"}

@mcp.tool()
def get_unread_messages(limit: int = 10):
    """
    Retrieves a list of unread messages, replies, and modmail for the authenticated user.
    """
    try:
        messages = []
        # PRAW method to access the authenticated user's unread inbox
        for item in reddit.inbox.unread(limit=limit):
            messages.append({
                "type": item.fullname.split('_')[0], # t1=comment, t4=message
                "subject": getattr(item, 'subject', 'N/A'),
                "author": str(getattr(item, 'author', 'Reddit')),
                "is_new": True,
                "text_preview": getattr(item, 'body', getattr(item, 'subject', ''))[:100]
            })
            
        return {"successful": True, "data": messages, "error": None}
    except Exception as e:
        # This requires user login (which is currently problematic), but the tool is useful.
        return {"successful": False, "error": f"Failed to retrieve unread messages: {str(e)}"}

if __name__ == "__main__":
    mcp.run()
