import os
import praw
from mcp.server.fastmcp import FastMCP, tools as mcp_tool

# NOTE: SECURITY RISK! Hardcoding sensitive credentials is not recommended.
# These values MUST be replaced with your actual Reddit App credentials.
os.environ["REDDIT_CLIENT_ID"] = "U3KzItyiU3RJgnGYaEmYkA"
os.environ["REDDIT_CLIENT_SECRET"] = "Cg6S_IOLt5XbEVqqRxTViEECnfWl2Q"
os.environ["REDDIT_USER_AGENT"] = "python:reddit-mcp-server:v1.0 (by /u/TinyFix8992)"

# Initialize the Reddit API client (PRAW)
reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    user_agent=os.environ["REDDIT_USER_AGENT"]
)

# Initialize MCP server
mcp = FastMCP("reddit-mcp-server")

# ==================================================
# REDDIT TOOLS (Code for tools remains the same)
# ==================================================

@mcp.tool()
def get_hot_posts(subreddit: str, limit: int = 5):
    """
    Get the hottest posts from a specified subreddit.
    """
    posts = []
    try:
        for submission in reddit.subreddit(subreddit).hot(limit=limit):
            posts.append({
                "title": submission.title,
                "url": submission.url,
                "score": submission.score,
                "author": str(submission.author)
            })
        return {"successful": True, "data": posts}
    except Exception as e:
        return {"successful": False, "error": str(e)}

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
def create_reddit_post(subreddit: str, title: str, kind: str, text: str = None, url: str = None, flair_id: str = None):
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
    Retrieves detailed information for a specific reddit comment (t1_...) or post (t3_...) 
    using its fullname ID.
    """
    
    try:
        # PRAW method to retrieve objects by fullname
        # reddit.info returns a generator of PRAW objects (Submission, Comment, or Redditor)
        item = next(reddit.info(fullnames=[id]))

        # Helper to convert PRAW objects to a simple dictionary for the tool response
        def serialize_item(item):
            data = {
                "id": item.id,
                "fullname": item.fullname,
                "kind": item.kind, # Will be 't1' for comment, 't3' for submission
                "score": item.score,
                "author": str(item.author)
            }
            if item.kind == 't3': # Submission/Post
                data['title'] = getattr(item, 'title', None)
                data['subreddit'] = str(item.subreddit)
                data['is_self'] = getattr(item, 'is_self', False)
                data['text_body'] = getattr(item, 'selftext', None)
            elif item.kind == 't1': # Comment
                data['link_id'] = getattr(item, 'link_id', None)
                data['body'] = getattr(item, 'body', None)
            
            return data

        # Return the serialized data
        return {
            "successful": True,
            "data": serialize_item(item),
            "error": ""
        }

    except StopIteration:
        # This occurs if reddit.info() returns nothing (ID not found)
        return {
            "successful": False,
            "data": {},
            "error": f"Content not found for ID: {id}. Check the ID format (t1_... or t3_...)."
        }
    except Exception as e:
        # Catch other PRAW exceptions (e.g., private content)
        return {
            "successful": False,
            "data": {},
            "error": f"Failed to retrieve content: {str(e)}"
        }

@mcp.tool()
def search_across_subreddits(search_query: str, limit: int = 5, restrict_sr: bool = False, sort: str = 'relevance'):
    """
    Searches reddit for content (e.g., posts, comments) using a query across all of Reddit.
    'restrict_sr' is typically set to False for an across-subreddit search.
    """
    results = []
    
    # Set the search scope: Use the general search available via the 'all' subreddit
    # The PRAW search method uses the 'restrict_sr' parameter to control scope
    search_results = reddit.subreddit('all').search(
        query=search_query,
        sort=sort,
        limit=limit,
        syntax='lucene', # Recommended for advanced search queries
        restrict_sr=restrict_sr # True restricts the search to the current context (subreddits)
    )

    try:
        for item in search_results:
            # We only expect submissions (posts) from the subreddit search
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

if __name__ == "__main__":
    mcp.run()