
import itertools  
import os
import praw
from mcp.server.fastmcp import FastMCP, tools as mcp_tools
from typing import Optional
from typing import Dict, Any
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta


def safe_execute(func, *args, **kwargs) -> Dict[str, Any]:
    """
    A centralized wrapper to execute PRAW functions, handle exceptions,
    and ensure a consistent JSON response format.
    """
    try:
        # Execute the function that makes the actual API call
        result = func(*args, **kwargs)
        # Return a success response
        return {"successful": True, "data": result, "error": None}
    except Exception as e:
        # If any error occurs, catch it and return a failure response
        return {"successful": False, "data": {}, "error": str(e)}
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

from typing import Optional

@mcp.tool()
def get_hot_posts(subreddit: str, limit: int = 5) -> dict:
    """Fetches a list of "hot" posts from a specified subreddit.

    Retrieves top posts from the "hot" section of a given subreddit,
    returning key information for each post.

    Args:
        subreddit (str): The name of the subreddit to fetch posts from (e.g., 'python'). (Required)
        limit (int): The maximum number of posts to retrieve. Defaults to 5. (Optional)

    Returns:
        dict: A dictionary containing a 'successful' status boolean and a 'data'field with a list of post objects. Each object includes thetitle, url, score, and author.
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
def get_user_info(username: str) -> dict:
    """Get basic information about a Reddit user.

    Retrieves public profile details for a given Reddit username, including
    their karma and account creation date.

    Args:
        username (str): The Reddit username to look up. (Required)

    Returns:
        dict: A dictionary containing the user's name, total karma (link and
              comment), and the UTC timestamp of account creation.
    """
    try:
        user = reddit.redditor(username)
        # Check if user exists by trying to access an attribute
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
def create_reddit_post(subreddit: str, title: str, kind: str, text: Optional[str] = None, url: Optional[str] = None, flair_id: Optional[str] = None) -> dict:
    """Creates a new post on a specified subreddit.

    Submits either a text post (kind='self') or a link post (kind='link').
    The 'text' parameter is used for self-posts, and 'url' is for link posts.

    Args:
        subreddit (str): The target subreddit name. (Required)
        title (str): The title of the post. (Required)
        kind (str): The type of post, must be 'self' or 'link'. (Required)
        text (Optional[str]): The body content for a 'self' post. (Optional)
        url (Optional[str]): The URL for a 'link' post. (Optional)
        flair_id (Optional[str]): The flair template ID to apply to the post. (Optional)

    Returns:
        dict: On success, a dictionary with the new post's ID and full URL.
              On failure, an error message.
    """
    submission_args = {}
    if flair_id:
        submission_args['flair_id'] = flair_id
        
    try:
        if kind.lower() == 'self':
            if not text:
                return {"successful": False, "error": "For 'self' posts, the 'text' parameter is required."}
            submission = reddit.subreddit(subreddit).submit(title=title, selftext=text, **submission_args)
        
        elif kind.lower() == 'link':
            if not url:
                return {"successful": False, "error": "For 'link' posts, the 'url' parameter is required."}
            submission = reddit.subreddit(subreddit).submit(title=title, url=url, **submission_args)
            
        else:
            return {"successful": False, "error": "Invalid value for 'kind'. Must be 'self' or 'link'."}

        return {"successful": True, "data": {"post_id": submission.id, "full_url": submission.url}}
    except Exception as e:
        return {"successful": False, "error": str(e)}

        # 2. Return success status and the new post's ID
        return {
            "successful": True, 
            "data": {
                "post_id": submission.id, 
                "full_url": submission.url
            },
            "error": ""
        }

# Re-run your server after adding this code!
# python reddit_server.py
@mcp.tool()
def delete_reddit_comment(id: str) -> dict:
    """Deletes a Reddit comment authored by the authenticated user.

    Identifies the comment by its fullname ID (e.g., 't1_abcxyz') and
    deletes it.

    Args:
        id (str): The fullname ID of the comment to delete. (Required)

    Returns:
        dict: A dictionary containing a confirmation message on success or
              an error message on failure.
    """
    try:
        comment = reddit.comment(id)
        comment.delete()
        return {"successful": True, "data": {"status": f"Comment with ID '{id}' was successfully deleted."}}
    except Exception as e:
        return {"successful": False, "error": f"Failed to delete comment: {str(e)}"}

@mcp.tool()
def delete_reddit_post(id: str) -> dict:
    """Deletes a Reddit post authored by the authenticated user.

    Permanently deletes a post using its fullname ID (e.g., 't3_abcxyz'),
    if the authenticated user has permission.

    Args:
        id (str): The fullname ID of the post to delete. (Required)

    Returns:
        dict: A dictionary with a confirmation message on success or an
              error message on failure.
    """
    try:
        submission = reddit.submission(id)
        submission.delete()
        return {"successful": True, "data": {"status": f"Post with ID '{id}' was successfully deleted."}}
    except Exception as e:
        return {"successful": False, "error": f"Failed to delete post: {str(e)}"}

@mcp.tool()
def edit_reddit_content(thing_id: str, text: str) -> dict:
    """Edits the body of an existing self-post or comment.

    Updates the content of a user's own comment (ID prefix 't1_') or
    self-post (ID prefix 't3_'). This cannot be used to edit post titles
    or the content of link posts.

    Args:
        thing_id (str): The fullname ID of the post or comment (e.g., 't1_...'
                        or 't3_...'). (Required)
        text (str): The new markdown text to replace the existing content. (Required)

    Returns:
        dict: A dictionary with a confirmation message on success or an
              error message on failure.
    """
    try:
        if thing_id.startswith('t1_'):
            item = reddit.comment(thing_id)
        elif thing_id.startswith('t3_'):
            item = reddit.submission(thing_id)
        else:
            return {"successful": False, "error": "Invalid 'thing_id' format. Must start with 't1_' or 't3_'."}
            
        item.edit(text)
        return {"successful": True, "data": {"status": f"Content ID '{thing_id}' was successfully updated."}}
    except Exception as e:
        return {"successful": False, "error": f"Failed to edit content: {str(e)}."}

@mcp.tool()
def get_link_flair(subreddit: str) -> dict:
    """Fetches the available link (post) flairs for a subreddit.

    Retrieves a list of all flair templates that can be applied to posts
    in the specified subreddit.

    Args:
        subreddit (str): The name of the subreddit to check for flairs. (Required)

    Returns:
        dict: A dictionary containing a list of available flairs. Each item
              in the list is a dictionary with 'flair_id' and 'flair_text'.
    """
    try:
        subreddit_obj = reddit.subreddit(subreddit)
        flair_list = []
        for template in subreddit_obj.flair.link_templates:
            flair_list.append({
                "flair_id": template['flair_template_id'],
                "flair_text": template['flair_text']
            })
        return {"successful": True, "data": flair_list}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve flairs for r/{subreddit}: {str(e)}."}

@mcp.tool()
def post_reddit_comment(thing_id: str, text: str) -> dict:
    """Posts a comment replying to a submission or another comment.

    Creates a new comment on Reddit under a specified parent object. The
    parent can be a submission (post) or an existing comment.

    Args:
        thing_id (str): The fullname ID of the parent post (e.g., 't3_abcxyz')
                        or comment (e.g., 't1_abcxyz') to reply to. (Required)
        text (str): The markdown-formatted content for the comment. (Required)

    Returns:
        dict: A dictionary containing the ID, fullname, and permalink of the
              newly created comment on success.
    """
    try:
        if thing_id.startswith('t3_'):
            parent = reddit.submission(thing_id)
        elif thing_id.startswith('t1_'):
            parent = reddit.comment(thing_id)
        else:
            return {"successful": False, "error": "Invalid 'thing_id' format. Must start with 't1_' or 't3_'."}
            
        new_comment = parent.reply(text)
        
        return {
            "successful": True,
            "data": {
                "comment_id": new_comment.id,
                "fullname": new_comment.fullname,
                "permalink": new_comment.permalink
            }
        }
    except Exception as e:
        return {"successful": False, "error": f"Failed to post comment: {str(e)}."}
@mcp.tool()
def retrieve_post_comments(article: str) -> dict:
    """Retrieves all comments from a specific Reddit post.

    Fetches a flattened list of all comments and replies for a given post,
    identified by its article ID.

    Args:
        article (str): The ID of the post (e.g., 'abcxyz' or 't3_abcxyz') from
                       which to retrieve comments. (Required)

    Returns:
        dict: A dictionary containing a list of comment objects. Each object
              includes the comment's ID, author, body, score, and permalink.
    """
    try:
        submission = reddit.submission(article)
        submission.comments.replace_more(limit=None)
        
        comments_list = submission.comments.list()
        
        retrieved_comments = []
        for comment in comments_list:
            if hasattr(comment, 'author'):
                retrieved_comments.append({
                    "comment_id": comment.id,
                    "author": str(comment.author),
                    "body": comment.body,
                    "score": comment.score,
                    "permalink": comment.permalink
                })

        return {"successful": True, "data": retrieved_comments}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve comments for article ID '{article}': {str(e)}."}
@mcp.tool()
def retrieve_reddit_posts(subreddit: str, size: int = 5) -> dict:
    """Retrieves a number of hot posts from a specified subreddit.

    Fetches a list of posts from the "hot" section of a given subreddit,
    returning key details for each post.

    Args:
        subreddit (str): The name of the subreddit (e.g., 'python'). (Required)
        size (int): The maximum number of posts to retrieve. Defaults to 5. (Optional)

    Returns:
        dict: A dictionary containing a list of post objects. Each object
              includes the title, ID, URL, score, and author.
    """
    posts = []
    try:
        for submission in reddit.subreddit(subreddit).hot(limit=size):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "url": submission.url,
                "score": submission.score,
                "author": str(submission.author)
            })
        
        return {"successful": True, "data": posts}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve posts for r/{subreddit}: {str(e)}."}
@mcp.tool()
def retrieve_specific_content(id: str) -> dict:
    """Retrieves detailed information for a specific post or comment.

    Fetches data for a single Reddit content item, identified by its unique
    fullname ID. Works for both submissions (posts) and comments.

    Args:
        id (str): The fullname ID of the post (e.g., 't3_abcxyz') or comment
                  (e.g., 't1_abcxyz') to retrieve. (Required)

    Returns:
        dict: A dictionary containing detailed information about the content,
              such as ID, author, score, and body or title text.
    """
    try:
        item = next(reddit.info(fullnames=[id]))

        data = {
            "id": item.id,
            "fullname": item.fullname,
            "object_type": item.fullname.split('_')[0],
            "score": getattr(item, 'score', None),
            "author": str(getattr(item, 'author', 'Unknown')),
            "created_utc": getattr(item, 'created_utc', None)
        }

        if data["object_type"] == 't3':
            data['title'] = getattr(item, 'title', None)
            data['text_body'] = getattr(item, 'selftext', None)
        
        elif data["object_type"] == 't1':
            data['body'] = getattr(item, 'body', None)

        return {"successful": True, "data": data}
    except StopIteration:
        return {"successful": False, "error": f"Content not found for ID: {id}."}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve content: {str(e)}"}
    
@mcp.tool()
def search_across_subreddits(search_query: str, limit: int = 5, restrict_sr: bool = False, sort: str = 'relevance') -> dict:
    """Searches for posts across all of Reddit.

    Performs a global search for a given query and returns matching posts.
    The 'sort' parameter can be 'relevance', 'hot', 'top', 'new', or 'comments'.
    Note: The 'restrict_sr' parameter is ignored to ensure a global search.

    Args:
        search_query (str): The term or phrase to search for. (Required)
        limit (int): The maximum number of results to return. Defaults to 5. (Optional)
        restrict_sr (bool): This parameter is ignored by the function. (Optional)
        sort (str): The method for sorting results. Defaults to 'relevance'. (Optional)

    Returns:
        dict: A dictionary containing a list of post objects that match the
              search query.
    """
    results = []
    try:
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
        
        return {"successful": True, "data": results}
    except Exception as e:
        return {"successful": False, "error": f"Failed to perform search: {str(e)}."}
@mcp.tool()
def get_subreddit_details(subreddit: str) -> dict:
    """Retrieves metadata for a specified subreddit.

    Fetches key details about a subreddit, including its public description,
    subscriber count, and creation date.

    Args:
        subreddit (str): The name of the subreddit to retrieve details for. (Required)

    Returns:
        dict: A dictionary containing the subreddit's name, title, subscriber
              count, creation timestamp, and public description.
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
def send_private_message(recipient: str, subject: str, message: str) -> dict:
    """Sends a private message to a specified Reddit user.

    Composes and sends a direct message from the authenticated user to
    another Reddit user.

    Args:
        recipient (str): The username of the user to send the message to. (Required)
        subject (str): The subject line of the message. (Required)
        message (str): The body content of the message. (Required)

    Returns:
        dict: A dictionary with a confirmation message on success or an
              error message on failure.
    """
    try:
        reddit.redditor(recipient).message(subject=subject, body=message)
        return {"successful": True, "data": {"status": f"Message sent to {recipient}."}}
    except Exception as e:
        return {"successful": False, "error": f"Failed to send message: {str(e)}"}

@mcp.tool()
def get_new_submissions(subreddit: str, limit: int = 5) -> dict:
    """Retrieves the newest posts from a subreddit.

    Fetches a list of the most recent submissions in a given subreddit,
    sorted chronologically.

    Args:
        subreddit (str): The name of the subreddit. (Required)
        limit (int): The maximum number of posts to retrieve. Defaults to 5. (Optional)

    Returns:
        dict: A dictionary containing a list of the newest post objects,
              including title, ID, URL, and author.
    """
    try:
        posts = []
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
def get_user_comments(username: str, limit: int = 10) -> dict:
    """Retrieves the most recent comments made by a user.

    Fetches a list of a user's latest comments from across Reddit, sorted
    chronologically.

    Args:
        username (str): The Reddit username whose comments to retrieve. (Required)
        limit (int): The maximum number of comments to return. Defaults to 10. (Optional)

    Returns:
        dict: A dictionary containing a list of comment objects, including the
              comment ID, subreddit, body, and score.
    """
    try:
        comments = []
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
def get_top_posts(subreddit: str, time_filter: str = 'day', limit: int = 10) -> dict:
    """Retrieves the top-scoring posts from a subreddit for a time period.

    Fetches the highest-scoring posts based on a specified time frame.
    Valid time filters are 'hour', 'day', 'week', 'month', 'year', and 'all'.

    Args:
        subreddit (str): The name of the subreddit. (Required)
        time_filter (str): The time window to filter by. Defaults to 'day'. (Optional)
        limit (int): The maximum number of posts to retrieve. Defaults to 10. (Optional)

    Returns:
        dict: A dictionary containing a list of the top-scoring post objects
              for the specified time frame.
    """
    if time_filter not in ['hour', 'day', 'week', 'month', 'year', 'all']:
        return {"successful": False, "error": "Invalid time_filter. Use 'hour', 'day', 'week', 'month', 'year', or 'all'."}
        
    try:
        posts = []
        for submission in reddit.subreddit(subreddit).top(time_filter=time_filter, limit=limit):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "score": submission.score,
                "author": str(submission.author)
            })
        return {"successful": True, "data": posts}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve top posts: {str(e)}"}
@mcp.tool()
def get_submission_details(submission_id: str) -> dict:
    """Retrieves metadata for a single post using its short ID.

    Fetches key details for a specific Reddit submission (post), such as its
    title, upvote ratio, and comment count, using its base ID (e.g., '1nrzroo').

    Args:
        submission_id (str): The short ID of the post to retrieve. (Required)

    Returns:
        dict: A dictionary containing the post's title, subreddit, upvote ratio,
              number of comments, and whether it is a self-post.
    """
    try:
        submission = reddit.submission(submission_id)
        
        return {
            "successful": True,
            "data": {
                "title": submission.title,
                "subreddit": str(submission.subreddit),
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
                "is_self": submission.is_self
            }
        }
    except Exception as e:
        return {"successful": False, "error": f"Submission lookup failed: {str(e)}"}

@mcp.tool()
def vote_on_content(fullname: str, direction: int = 1) -> dict:
    """Casts a vote on a Reddit post or comment.

    Applies an upvote, downvote, or removes a vote from a specific content
    item identified by its fullname.

    Args:
        fullname (str): The fullname ID of the post (t3_...) or comment (t1_...)
                        to vote on. (Required)
        direction (int): The vote direction: 1 for upvote, -1 for downvote,
                         or 0 to remove a vote. Defaults to 1. (Optional)

    Returns:
        dict: A dictionary containing a confirmation message on success.
    """
    try:
        thing = reddit.comment(fullname) if fullname.startswith('t1_') else reddit.submission(fullname)
        
        if direction == 1:
            thing.upvote()
        elif direction == -1:
            thing.downvote()
        elif direction == 0:
            thing.clear_vote()
        else:
            return {"successful": False, "error": "Invalid direction. Must be 1, -1, or 0."}

        return {"successful": True, "data": {"status": f"Vote of {direction} cast on {fullname}."}}
    except Exception as e:
        return {"successful": False, "error": f"Voting failed: {str(e)}"}

@mcp.tool()
def search_subreddits(query: str, limit: int = 10) -> dict:
    """Searches for subreddits by name or description.

    Finds Reddit communities that match a given search query and returns
    key details about them.

    Args:
        query (str): The text to search for in subreddit names and descriptions. (Required)
        limit (int): The maximum number of subreddits to return. Defaults to 10. (Optional)

    Returns:
        dict: A dictionary containing a list of matching subreddits, each with its
              name, subscriber count, and public description.
    """
    try:
        subreddits = []
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
def get_redditor_trophies(username: str) -> dict:
    """Retrieves the list of trophies awarded to a user.

    Fetches all public trophies and achievements for a specified Reddit user.

    Args:
        username (str): The Reddit username to look up. (Required)

    Returns:
        dict: A dictionary containing a list of the user's trophies, where each
              trophy includes a name, description, and icon URL.
    """
    try:
        user = reddit.redditor(username)
        trophies = []
        
        for trophy in user.trophies():
            trophies.append({
                "name": getattr(trophy, 'name', 'N/A'),
                "description": getattr(trophy, 'description', 'No description'),
                "icon_url": getattr(trophy, 'icon_url', None)
            })
        return {"successful": True, "data": trophies}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve trophies for {username}: {str(e)}"}
@mcp.tool()
def get_subreddit_rules(subreddit: str) -> dict:
    """Retrieves the official rules for a subreddit.

    Fetches the complete set of rules that govern a specified subreddit, which is
    useful for content compliance checks.

    Args:
        subreddit (str): The name of the subreddit whose rules to retrieve. (Required)

    Returns:
        dict: A dictionary containing a list of the subreddit's rules. Each rule
              includes a short name, full description, and violation reason.
    """
    try:
        rules_data = reddit.subreddit(subreddit).rules()
        
        rule_list = []
        for rule in rules_data.get('rules', []):
            rule_list.append({
                "short_name": rule.get('short_name'),
                "description": rule.get('description'),
                "created_utc": rule.get('created_utc'),
                "violation_reason": rule.get('violation_reason')
            })
        
        return {"successful": True, "data": rule_list}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve rules for r/{subreddit}: {str(e)}"}
from typing import Optional

@mcp.tool()
def get_subreddit_listings(subreddit: str, listing_type: str = 'hot', time_filter: Optional[str] = None, limit: int = 10) -> dict:
    """Retrieves posts from a subreddit based on a listing type.

    Fetches posts from a specified listing ('hot', 'top', 'new', 'rising', 
    'controversial'). A time filter ('day', 'week', etc.) can be used for
    'top' and 'controversial' listings.

    Args:
        subreddit (str): The name of the subreddit. (Required)
        listing_type (str): The listing to retrieve posts from. Defaults to 'hot'. (Optional)
        time_filter (Optional[str]): The time window for 'top' or 'controversial'
                                     listings. e.g., 'day', 'week', 'all'. (Optional)
        limit (int): The maximum number of posts to return. Defaults to 10. (Optional)

    Returns:
        dict: A dictionary containing a list of post objects from the specified listing.
    """
    listing_type = listing_type.lower()
    if listing_type not in ['hot', 'top', 'new', 'rising', 'controversial']:
        return {"successful": False, "error": "Invalid listing_type."}
        
    try:
        sub = reddit.subreddit(subreddit)
        
        if listing_type == 'hot':
            submissions = sub.hot(limit=limit)
        elif listing_type == 'new':
            submissions = sub.new(limit=limit)
        elif listing_type == 'rising':
            submissions = sub.rising(limit=limit)
        elif listing_type in ['top', 'controversial']:
            submissions = getattr(sub, listing_type)(time_filter=time_filter or 'day', limit=limit)
        
        posts = [{"title": s.title, "id": s.id, "score": s.score, "author": str(s.author)} for s in submissions]
        
        return {"successful": True, "data": posts}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve {listing_type} posts for r/{subreddit}: {str(e)}"}
@mcp.tool()
def send_mod_mail(subreddit: str, subject: str, message: str) -> dict:
    """Sends a message to the moderators of a subreddit.

    Composes and sends a modmail message on behalf of the authenticated user
    to the moderation team of a specified subreddit.

    Args:
        subreddit (str): The target subreddit for the modmail. (Required)
        subject (str): The subject line of the message. (Required)
        message (str): The body content of the message. (Required)

    Returns:
        dict: A dictionary containing a confirmation message on success.
    """
    try:
        reddit.subreddit(subreddit).message(subject=subject, message=message)
        return {"successful": True, "data": {"status": f"Modmail sent successfully to moderators of r/{subreddit}."}}
    except Exception as e:
        return {"successful": False, "error": f"Failed to send modmail: {str(e)}"}
@mcp.tool()
def get_subreddit_sidebar(subreddit: str) -> dict:
    """Retrieves the content of a subreddit's sidebar.

    Fetches the raw markdown description and the short public description
    from the sidebar (community details) of a specified subreddit.

    Args:
        subreddit (str): The name of the subreddit whose sidebar to retrieve. (Required)

    Returns:
        dict: A dictionary containing the sidebar's markdown content, short
              public description, and the subreddit's subscriber count.
    """
    try:
        sub = reddit.subreddit(subreddit)
        return {
            "successful": True,
            "data": {
                "description_md": getattr(sub, 'description', None),
                "public_description": getattr(sub, 'public_description', None),
                "subscribers": getattr(sub, 'subscribers', None)
            }
        }
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve sidebar content for r/{subreddit}: {str(e)}"}
@mcp.tool()
def get_subreddits_by_topic(topic: str, limit: int = 10) -> dict:
    """Retrieves a list of subreddits related to a topic.

    Searches for and returns Reddit communities whose topic, name, or
    description is related to the given search query.

    Args:
        topic (str): The topic or theme to search for. (Required)
        limit (int): The maximum number of subreddits to return. Defaults to 10. (Optional)

    Returns:
        dict: A dictionary containing a list of related subreddits, each with its
              name, subscriber count, and public description.
    """
    try:
        subreddits = []
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
def get_moderators(subreddit: str) -> dict:
    """Retrieves the list of moderators for a subreddit.

    Fetches a complete list of all moderator usernames for the specified
    subreddit community.

    Args:
        subreddit (str): The name of the subreddit whose moderators to retrieve. (Required)

    Returns:
        dict: A dictionary containing a list of moderator usernames and the
              total count of moderators.
    """
    try:
        mod_list = [str(mod) for mod in reddit.subreddit(subreddit).moderator()]
        
        return {
            "successful": True,
            "data": {"moderators": mod_list, "count": len(mod_list)}
        }
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve moderators for r/{subreddit}: {str(e)}"}
@mcp.tool()
def get_user_flair(subreddit: str, username: str) -> dict:
    """Retrieves a user's flair in a specific subreddit.

    Fetches the assigned flair text and CSS class for a single user within
    a given subreddit.

    Args:
        subreddit (str): The subreddit where the flair is set. (Required)
        username (str): The user whose flair to retrieve. (Required)

    Returns:
        dict: A dictionary containing the user's flair text and CSS class,
              or a status message if no flair is set.
    """
    try:
        flair_generator = reddit.subreddit(subreddit).flair(username=username)
        flair_data_list = list(flair_generator)
        
        if not flair_data_list:
            return {"successful": True, "data": {"status": f"User '{username}' has no flair set in this subreddit."}}

        flair_dict = flair_data_list[0]
        
        return {
            "successful": True,
            "data": {
                "username": flair_dict.get('user'),
                "flair_text": flair_dict.get('flair_text'),
                "flair_css_class": flair_dict.get('flair_css_class')
            }
        }
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve flair for {username} in r/{subreddit}: {str(e)}"}
@mcp.tool()
def list_multireddits() -> dict:
    """Lists the authenticated user's Multireddits (Custom Feeds).

    Retrieves a list of all Multireddits created by the user whose credentials
    are being used for the API session.

    Returns:
        dict: A dictionary containing a list of the user's Multireddits. Each
              includes its name, path, visibility, and a list of subreddits it contains.
    """
    try:
        multis = []
        for multi in reddit.user.multireddits():
            multis.append({
                "name": multi.display_name,
                "path": multi.path,
                "visibility": multi.visibility,
                "subreddits": [str(sub) for sub in multi.subreddits]
            })
        return {"successful": True, "data": multis}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve multireddits: {str(e)}"}
@mcp.tool()
def get_multireddit_posts(multireddit_name: str, limit: int = 10) -> dict:
    """Retrieves hot posts from a user's specific Multireddit.

    Fetches a list of posts from the 'hot' section of one of the authenticated
    user's custom feeds (Multireddits).

    Args:
        multireddit_name (str): The name of the Multireddit to retrieve posts from. (Required)
        limit (int): The maximum number of posts to return. Defaults to 10. (Optional)

    Returns:
        dict: A dictionary containing a list of post objects from the
              specified Multireddit.
    """
    try:
        posts = []
        multi = reddit.multireddit(reddit.user.me().name, multireddit_name)
        
        for submission in multi.hot(limit=limit):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "subreddit": str(submission.subreddit),
                "score": submission.score
            })
        return {"successful": True, "data": posts}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve posts from multireddit '{multireddit_name}': {str(e)}"}
    
@mcp.tool()
def get_multireddit_posts(multireddit_name: str, limit: int = 10) -> dict:
    """Retrieves hot posts from a user's specific Multireddit.

    Fetches a list of posts from the 'hot' section of one of the authenticated
    user's custom feeds (Multireddits).

    Args:
        multireddit_name (str): The name of the Multireddit to retrieve posts from. (Required)
        limit (int): The maximum number of posts to return. Defaults to 10. (Optional)

    Returns:
        dict: A dictionary containing a list of post objects from the
              specified Multireddit.
    """
    try:
        posts = []
        multi = reddit.multireddit(reddit.user.me().name, multireddit_name)
        
        for submission in multi.hot(limit=limit):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "subreddit": str(submission.subreddit),
                "score": submission.score
            })
        return {"successful": True, "data": posts}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve posts from multireddit '{multireddit_name}': {str(e)}"}
@mcp.tool()
def get_blocked_users() -> dict:
    """Retrieves the authenticated user's list of blocked users.

    Fetches a complete list of all Reddit accounts that the authenticated
    user has blocked.

    Returns:
        dict: A dictionary containing a list of blocked users, where each
              user object includes a username and ID, along with the total count.
    """
    try:
        blocked_users = []
        for user in reddit.user.blocked():
            blocked_users.append({
                "username": str(user.name),
                "id": str(user.id)
            })
        return {"successful": True, "data": {"blocked_users": blocked_users, "count": len(blocked_users)}}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve blocked users: {str(e)}"}
@mcp.tool()
def get_moderated_subs(limit: int = 25) -> dict:
    """Lists subreddits the authenticated user moderates.

    Retrieves a list of all communities for which the authenticated user
    has moderator permissions.

    Args:
        limit (int): The maximum number of subreddits to return. Defaults to 25. (Optional)

    Returns:
        dict: A dictionary containing a list of subreddit objects, each including
              the subreddit's name and subscriber count.
    """
    try:
        subs = []
        for sub in reddit.user.me().moderator_of(limit=limit):
            subs.append({
                "name": str(sub.display_name),
                "subscribers": sub.subscribers,
                "is_moderator": True
            })
        return {"successful": True, "data": subs}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve moderated subreddits: {str(e)}"}
@mcp.tool()
def get_unread_messages(limit: int = 10) -> dict:
    """Retrieves unread messages from the user's inbox.

    Fetches a list of all unread items for the authenticated user, which can
    include private messages, comment replies, and other notifications.

    Args:
        limit (int): The maximum number of unread items to return. Defaults to 10. (Optional)

    Returns:
        dict: A dictionary containing a list of unread message objects, each with
              its type, subject, author, and a text preview.
    """
    try:
        messages = []
        for item in reddit.inbox.unread(limit=limit):
            messages.append({
                "type": item.fullname.split('_')[0],
                "subject": getattr(item, 'subject', 'N/A'),
                "author": str(getattr(item, 'author', 'Reddit')),
                "is_new": True,
                "text_preview": getattr(item, 'body', getattr(item, 'subject', ''))[:100]
            })
            
        return {"successful": True, "data": messages}
    except Exception as e:
        return {"successful": False, "error": f"Failed to retrieve unread messages: {str(e)}"}


@mcp.tool()
def get_subreddit_traffic_stats(subreddit: str) -> Dict[str, Any]:
    """Retrieves traffic statistics for a moderated subreddit.

    Fetches daily, monthly, and hourly uniques and pageview data. This tool
    requires the authenticated user to be a moderator of the target subreddit
    with 'traffic' permissions.

    Args:
        subreddit (str): The name of the subreddit to get stats for. (Required)

    Returns:
        Dict[str, Any]: A dictionary containing lists of daily, monthly, and
                        hourly traffic statistics.
    """
    def _get():
        traffic_data = reddit.subreddit(subreddit).traffic()
        return {
            "daily_stats": traffic_data.get('day', []),
            "monthly_stats": traffic_data.get('month', []),
            "hourly_stats": traffic_data.get('hour', [])
        }
    return safe_execute(_get)


@mcp.tool()
def create_post_collection(subreddit: str, title: str, description: str = "") -> Dict[str, Any]:
    """Creates a new post collection in a moderated subreddit.

    Organizes posts into a collection view. This tool requires the authenticated
    user to be a moderator of the target subreddit.

    Args:
        subreddit (str): The subreddit in which to create the collection. (Required)
        title (str): The title for the new collection. (Required)
        description (str): An optional description for the collection. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a success status and the ID
                        and permalink of the newly created collection.
    """
    def _create():
        endpoint = "/api/v1/collections/create_collection"
        payload = {
            "sr_name": subreddit,
            "title": title,
            "description": description
        }
        response = reddit.post(endpoint, data=payload)
        return {
            "status": "Collection created successfully.",
            "collection_id": response.get("collection_id"),
            "permalink": response.get("permalink")
        }
    return safe_execute(_create)


@mcp.tool()
def add_post_to_collection(collection_id: str, post_id: str) -> Dict[str, Any]:
    """Adds a post to an existing collection in a subreddit.

    This action requires the authenticated user to have moderator permissions
    in the subreddit where the collection exists.

    Args:
        collection_id (str): The unique ID of the collection. (Required)
        post_id (str): The full ID of the post (e.g., 't3_abcxyz') to add. (Required)

    Returns:
        Dict[str, Any]: A dictionary with a status confirmation message.
    """
    def _add():
        collection = reddit.subreddit(None).collections(collection_id=collection_id)
        collection.add_post(post_id)
        return {"status": f"Post '{post_id}' added to collection '{collection_id}'."}
    return safe_execute(_add)


@mcp.tool()
def sticky_post(post_id: str, state: bool = True, slot: int = 1) -> Dict[str, Any]:
    """Stickies or un-stickies a post in a subreddit.

    Pins a post to the top of its subreddit or removes the pin. This requires
    moderator permissions.

    Args:
        post_id (str): The ID of the post (e.g., 'abcxyz') to sticky. (Required)
        state (bool): Set to `True` to sticky, `False` to un-sticky. Defaults to `True`. (Optional)
        slot (int): The sticky slot to use, either 1 (top) or 2 (second). Defaults to 1. (Optional)

    Returns:
        Dict[str, Any]: A dictionary with a status confirmation message.
    """
    def _sticky():
        submission = reddit.submission(post_id)
        submission.mod.sticky(state=state, bottom=(slot == 2))
        action = "Stickied" if state else "Un-stickied"
        return {"status": f"Post '{post_id}' has been {action} in slot {slot}."}
    return safe_execute(_sticky)


@mcp.tool()
def add_wiki_editor(subreddit: str, username: str) -> Dict[str, Any]:
    """Grants a user permission to edit a subreddit's wiki.

    Adds a specified user to the list of approved wiki editors. This requires
    the authenticated user to have 'modwiki' moderator permissions.

    Args:
        subreddit (str): The subreddit where the wiki is located. (Required)
        username (str): The username of the user to grant permissions to. (Required)

    Returns:
        Dict[str, Any]: A dictionary with a status confirmation message.
    """
    def _add():
        reddit.subreddit(subreddit).wiki.add(username)
        return {"status": f"User '{username}' can now edit the wiki for r/{subreddit}."}
    return safe_execute(_add)


@mcp.tool()
def list_approved_submitters(subreddit: str) -> Dict[str, Any]:
    """Lists the approved submitters for a subreddit.

    Retrieves the list of users (contributors) who are approved to submit content
    to a private or restricted subreddit. Requires moderator permissions.

    Args:
        subreddit (str): The name of the subreddit. (Required)

    Returns:
        Dict[str, Any]: A dictionary containing a list of approved users, each with
                        their username and the date they were added.
    """
    def _get():
        contributors = []
        for contributor in reddit.subreddit(subreddit).contributor():
            contributors.append({
                "username": str(contributor.name),
                "date": contributor.date
            })
        return contributors
    return safe_execute(_get)

@mcp.tool()
def list_wiki_pages(subreddit: str) -> Dict[str, Any]:
    """Retrieves a list of all wiki pages in a subreddit.

    Fetches the names of all existing wiki pages. This requires the subreddit's
    wiki to be enabled and publicly visible or for the user to have access.

    Args:
        subreddit (str): The name of the subreddit. (Required)

    Returns:
        Dict[str, Any]: A dictionary containing a list of wiki page names.
    """
    def _get():
        return [page.name for page in reddit.subreddit(subreddit).wiki]
    return safe_execute(_get)


@mcp.tool()
def get_moderation_log(subreddit: str, limit: int = 25) -> Dict[str, Any]:
    """Retrieves the moderation log for a subreddit.

    Fetches a list of moderator actions performed in a subreddit. This requires
    the authenticated user to have moderator permissions with 'log' access.

    Args:
        subreddit (str): The name of the subreddit. (Required)
        limit (int): The maximum number of log entries to retrieve. Defaults to 25. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a list of log entries, each with
                        details about the action, target, and moderator.
    """
    def _get():
        log_entries = []
        for log_item in reddit.subreddit(subreddit).mod.log(limit=limit):
            log_entries.append({
                "action": log_item.action,
                "target_author": getattr(log_item, 'target_author', None),
                "target_fullname": getattr(log_item, 'target_fullname', None),
                "description": getattr(log_item, 'description', None),
                "moderator": str(log_item.mod),
                "created_utc": log_item.created_utc
            })
        return log_entries
    return safe_execute(_get)


@mcp.tool()
def list_muted_users(subreddit: str) -> Dict[str, Any]:
    """Lists users muted from a subreddit's modmail.

    Retrieves a list of all users who are currently muted from contacting the
    moderators of a specified subreddit. Requires moderator permissions.

    Args:
        subreddit (str): The name of the subreddit. (Required)

    Returns:
        Dict[str, Any]: A dictionary containing a list of muted users, each with
                        their username, ID, and the date they were muted.
    """
    def _get():
        muted_list = []
        for muted_user in reddit.subreddit(subreddit).muted():
            muted_list.append({
                "username": str(muted_user.name),
                "date": muted_user.date,
                "id": muted_user.id
            })
        return muted_list
    return safe_execute(_get)


@mcp.tool()
def get_controversial_posts(subreddit: str, time_filter: str = 'day', limit: int = 10) -> Dict[str, Any]:
    """Retrieves controversial posts from a subreddit.

    Fetches posts with a high level of both upvotes and downvotes from a subreddit
    within a specified time frame.

    Args:
        subreddit (str): The name of the subreddit. (Required)
        time_filter (str): The time window to filter by ('hour', 'day', 'week',
                           'month', 'year', 'all'). Defaults to 'day'. (Optional)
        limit (int): The maximum number of posts to return. Defaults to 10. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a list of controversial posts,
                        each with its title, ID, score, and author.
    """
    if time_filter not in ['hour', 'day', 'week', 'month', 'year', 'all']:
        return {"successful": False, "data": {}, "error": "Invalid time_filter."}
    
    def _get():
        posts = []
        for submission in reddit.subreddit(subreddit).controversial(time_filter=time_filter, limit=limit):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "author": str(submission.author)
            })
        return posts
    return safe_execute(_get)


@mcp.tool()
def list_user_friends() -> Dict[str, Any]:
    """Retrieves the friend list of the authenticated user.

    Fetches the list of all Reddit users that the currently authenticated user
    has added as a friend.

    Returns:
        Dict[str, Any]: A dictionary containing a list of friend objects, each
                        with a username and ID.
    """
    def _get():
        friends_list = []
        for friend in reddit.user.friends():
            friends_list.append({
                "username": str(friend.name),
                "id": friend.id
            })
        return friends_list
    return safe_execute(_get)


@mcp.tool()
def get_trending_posts(limit: int = 10) -> Dict[str, Any]:
    """Retrieves trending posts from across all of Reddit.

    Fetches the current trending posts by retrieving the 'hot' posts from
    the r/popular subreddit, which aggregates popular content globally.

    Args:
        limit (int): The maximum number of trending posts to return. Defaults to 10. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a list of trending posts, each
                        with its title, subreddit, score, and URL.
    """
    def _get():
        posts = []
        for submission in reddit.subreddit("popular").hot(limit=limit):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "subreddit": str(submission.subreddit),
                "score": submission.score,
                "url": submission.url,
                "author": str(submission.author)
            })
        return posts
    return safe_execute(_get)


@mcp.tool()
def get_my_upvoted_content(limit: int = 25) -> Dict[str, Any]:
    """Retrieves content upvoted by the authenticated user.

    Fetches a list of posts and comments that the currently authenticated user
    has upvoted. This is a private action and only works for your own account.

    Args:
        limit (int): The maximum number of items to return. Defaults to 25. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a list of upvoted items,
                        distinguishing between posts and comments.
    """
    def _get():
        upvoted_items = []
        for item in reddit.user.me().upvoted(limit=limit):
            item_data = {"id": item.id, "subreddit": str(item.subreddit)}
            if hasattr(item, 'title'):
                item_data["type"] = "Post"
                item_data["title"] = item.title
            else:
                item_data["type"] = "Comment"
                item_data["body"] = item.body
            upvoted_items.append(item_data)
        return upvoted_items
    return safe_execute(_get)

@mcp.tool()
def get_my_downvoted_content(limit: int = 25) -> Dict[str, Any]:
    """Retrieves content downvoted by the authenticated user.

    Fetches a list of posts and comments that the currently authenticated user
    has downvoted. This is a private action and only works for your own account.

    Args:
        limit (int): The maximum number of items to return. Defaults to 25. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a list of downvoted items,
                        distinguishing between posts and comments.
    """
    def _get():
        downvoted_items = []
        for item in reddit.user.me().downvoted(limit=limit):
            item_data = {"id": item.id, "subreddit": str(item.subreddit)}
            if hasattr(item, 'title'):
                item_data["type"] = "Post"
                item_data["title"] = item.title
            else:
                item_data["type"] = "Comment"
                item_data["body"] = item.body
            downvoted_items.append(item_data)
        return downvoted_items
    return safe_execute(_get)


@mcp.tool()
def get_reddit_age(name: str, item_type: str) -> Dict[str, Any]:
    """Calculates the age of a Reddit account or a subreddit.

    This tool determines the elapsed time since a user account or a subreddit
    was created, returning a human-readable age string.

    Args:
        name (str): The username or subreddit name. (Required)
        item_type (str): The type of item, must be 'user' or 'subreddit'. (Required)

    Returns:
        Dict[str, Any]: A dictionary containing the item's name, type, creation
                        date, and its formatted age in years, months, and days.
    """
    if item_type.lower() not in ['user', 'subreddit']:
        return {"successful": False, "data": {}, "error": "Invalid item_type. Must be 'user' or 'subreddit'."}

    def _get():
        if item_type.lower() == 'user':
            item = reddit.redditor(name)
        else: # subreddit
            item = reddit.subreddit(name)

        created_utc = item.created_utc
        creation_date = datetime.fromtimestamp(created_utc, tz=timezone.utc)
        current_date = datetime.now(timezone.utc)
        delta = relativedelta(current_date, creation_date)
        age_string = f"{delta.years} years, {delta.months} months, {delta.days} days"
        
        return {
            "name": name,
            "type": item_type,
            "creation_date": creation_date.strftime('%Y-%m-%d %H:%M:%S UTC'),
            "age": age_string
        }
    return safe_execute(_get)

@mcp.tool()
def get_user_gilded_content(username: str, limit: int = 25) -> Dict[str, Any]:
    """Retrieves a user's content that has received awards.

    Fetches a list of posts and comments made by a specific user that have
    been gilded (given awards) by others.

    Args:
        username (str): The username of the user to check. (Required)
        limit (int): The maximum number of gilded items to return. Defaults to 25. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a list of the user's gilded posts
                        and comments, with details for each item.
    """
    def _get():
        gilded_items = []
        for item in reddit.redditor(username).gilded(limit=limit):
            item_data = {
                "id": item.id,
                "subreddit": str(item.subreddit),
                "awards_count": item.total_awards_received,
                "score": item.score
            }
            if hasattr(item, 'title'):
                item_data["type"] = "Post"
                item_data["title"] = item.title
                item_data["url"] = item.url
            else:
                item_data["type"] = "Comment"
                item_data["body_preview"] = item.body[:150] + '...'
                item_data["link"] = f"https://www.reddit.com{item.permalink}"
            gilded_items.append(item_data)
        return gilded_items
    return safe_execute(_get)


@mcp.tool()
def get_user_follower_count(username: str) -> Dict[str, Any]:
    """Retrieves the follower count for a Reddit user.

    Fetches the number of users who are following a specific Redditor's profile.

    Args:
        username (str): The username of the user to check. (Required)

    Returns:
        Dict[str, Any]: A dictionary containing the username and their total
                        number of followers.
    """
    def _get():
        user = reddit.redditor(username)
        follower_count = user.subreddit["subscribers"]
        return {
            "username": user.name,
            "follower_count": follower_count
        }
    return safe_execute(_get)


@mcp.tool()
def get_best_feed(limit: int = 25) -> Dict[str, Any]:
    """Retrieves the authenticated user's personalized "Best" feed.

    Fetches posts from the user's main front page, sorted by Reddit's "Best"
    algorithm, which prioritizes new content from frequently visited communities.

    Args:
        limit (int): The maximum number of posts to return. Defaults to 25. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a list of post objects from the
                        user's "Best" feed.
    """
    def _get():
        posts = []
        for submission in reddit.front.best(limit=limit):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "subreddit": str(submission.subreddit),
                "score": submission.score,
                "url": submission.url,
                "author": str(submission.author)
            })
        return posts
    return safe_execute(_get)

@mcp.tool()
def list_modmail_conversations(subreddit: str, limit: int = 10) -> Dict[str, Any]:
    """Retrieves recent modmail conversations for a subreddit.

    Fetches a list of the most recent modmail threads. This action requires
    the authenticated user to be a moderator of the target subreddit.

    Args:
        subreddit (str): The name of the subreddit. (Required)
        limit (int): The maximum number of conversations to retrieve. Defaults to 10. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a list of modmail conversation
                        objects, with details like subject and participants.
    """
    def _get():
        conversations = []
        for conv in reddit.subreddit(subreddit).mod.conversations(limit=limit):
            conversations.append({
                "conversation_id": conv.id,
                "subject": conv.subject,
                "last_updated": conv.last_updated,
                "participant": str(getattr(conv.user, 'name', 'Unknown User')),
                "is_highlighted": conv.is_highlighted
            })
        return conversations
    return safe_execute(_get)

@mcp.tool()
def ignore_reports_on_content(content_id: str) -> Dict[str, Any]:
    """Ignores all user reports on a post or comment.

    Clears an item from the moderation queue by ignoring any reports made
    against it. This requires moderator permissions.

    Args:
        content_id (str): The full ID of the post (t3_...) or comment (t1_...)
                          to ignore reports on. (Required)

    Returns:
        Dict[str, Any]: A dictionary with a status confirmation message.
    """
    def _ignore():
        item = reddit.submission(content_id) if content_id.startswith('t3_') else reddit.comment(content_id)
        item.mod.ignore_reports()
        return {"status": f"Reports have been ignored for content '{content_id}'."}
    return safe_execute(_ignore)

@mcp.tool()
def delete_flair_template(subreddit: str, flair_template_id: str) -> Dict[str, Any]:
    """Deletes a post flair template from a subreddit.

    Permanently removes a link flair option from a subreddit's settings. Requires
    the authenticated user to have 'modflair' permissions.

    Args:
        subreddit (str): The name of the subreddit. (Required)
        flair_template_id (str): The unique ID of the flair template to delete. (Required)

    Returns:
        Dict[str, Any]: A dictionary with a status confirmation message.
    """
    def _delete():
        reddit.subreddit(subreddit).flair.delete(flair_template_id)
        return {"status": f"Flair template '{flair_template_id}' has been deleted."}
    return safe_execute(_delete)


@mcp.tool()
def crosspost_submission(post_id: str, subreddit: str, title: Optional[str] = None) -> Dict[str, Any]:
    """Crossposts an existing submission to another subreddit.

    Shares an existing post to a different subreddit. The new post will be
    an embed of the original.

    Args:
        post_id (str): The ID of the post (e.g., 'abcxyz') to crosspost. (Required)
        subreddit (str): The name of the target subreddit to crosspost to. (Required)
        title (Optional[str]): A new title for the crosspost. If not provided,
                               the original title is used. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing the status, ID, and URL of the
                        newly created crosspost.
    """
    def _crosspost():
        submission = reddit.submission(post_id)
        crosspost_submission = submission.crosspost(subreddit=subreddit, title=title)
        return {
            "status": "Post crossposted successfully.",
            "new_post_id": crosspost_submission.id,
            "new_post_url": crosspost_submission.permalink
        }
    return safe_execute(_crosspost)

@mcp.tool()
def reply_to_modmail_conversation(conversation_id: str, body: str, is_author_hidden: bool = False) -> Dict[str, Any]:
    """Replies to a modmail conversation.

    Sends a reply within an existing modmail thread. Requires moderator permissions.

    Args:
        conversation_id (str): The unique ID of the modmail conversation. (Required)
        body (str): The content of the reply message. (Required)
        is_author_hidden (bool): If True, sends the reply from the subreddit itself
                                 instead of your personal username. Defaults to False. (Optional)

    Returns:
        Dict[str, Any]: A dictionary with a status confirmation message.
    """
    def _reply():
        conversation = reddit.subreddit(None).mod.conversation(conversation_id)
        conversation.reply(body=body, author_hidden=is_author_hidden)
        return {"status": f"Replied to modmail conversation '{conversation_id}'."}
    return safe_execute(_reply)


@mcp.tool()
def get_my_notifications(filter_type: str = 'unread', limit: int = 10) -> Dict[str, Any]:
    """Retrieves notifications from the authenticated user's inbox.

    Fetches various types of inbox items, such as messages, comment replies,
    and mentions, based on the specified filter.

    Args:
        filter_type (str): The type of notifications to retrieve ('all', 'unread',
                           'comment_replies', 'post_replies', 'mentions', 'messages').
                           Defaults to 'unread'. (Optional)
        limit (int): The maximum number of notifications to return. Defaults to 10. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a list of notification objects
                        matching the filter criteria.
    """
    valid_filters = ['all', 'unread', 'comment_replies', 'post_replies', 'mentions', 'messages']
    if filter_type.lower() not in valid_filters:
        return {"successful": False, "data": {}, "error": f"Invalid filter_type. Use one of: {valid_filters}"}

    def _get():
        inbox_methods = {
            'all': reddit.inbox.all,
            'unread': reddit.inbox.unread,
            'comment_replies': reddit.inbox.comment_replies,
            'post_replies': reddit.inbox.post_replies,
            'mentions': reddit.inbox.mentions,
            'messages': reddit.inbox.messages
        }
        inbox_items = inbox_methods[filter_type.lower()](limit=limit)

        notifications = []
        for item in inbox_items:
            notifications.append({
                "id": item.id,
                "author": str(getattr(item, 'author', 'N/A')),
                "subject": getattr(item, 'subject', 'N/A'),
                "body": getattr(item, 'body', ''),
                "is_new": getattr(item, 'new', False),
                "created_utc": item.created_utc
            })
        return notifications
    return safe_execute(_get)


@mcp.tool()
def find_communities_by_topic(topic: str, limit: int = 10) -> Dict[str, Any]:
    """Finds subreddit communities related to a specific topic.

    Searches for and retrieves a list of subreddits based on a topic query,
    returning key details about each matching community.

    Args:
        topic (str): The topic or theme to search for. (Required)
        limit (int): The maximum number of communities to return. Defaults to 10. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a list of subreddit objects, each
                        with its name, subscriber count, and description.
    """
    def _get():
        communities = []
        sub_generator = reddit.subreddits.search_by_topic(topic)
        
        for sub in itertools.islice(sub_generator, limit):
            communities.append({
                "name": str(sub.display_name),
                "subscribers": sub.subscribers,
                "public_description": sub.public_description
            })
        return communities
    return safe_execute(_get)



@mcp.tool()
def get_community_age_rating(subreddit: str) -> Dict[str, Any]:
    """Checks the age rating (NSFW status) of a subreddit.

    Determines if a subreddit is marked as 'over 18' (Not Safe For Work) and
    returns its classification.

    Args:
        subreddit (str): The name of the subreddit to check. (Required)

    Returns:
        Dict[str, Any]: A dictionary containing the subreddit's name, a boolean
                        for its NSFW status, and a human-readable age rating.
    """
    def _get():
        sub = reddit.subreddit(subreddit)
        is_nsfw = sub.over18
        classification = "18 and Over (NSFW)" if is_nsfw else "All Ages"
        
        return {
            "subreddit_name": sub.display_name,
            "is_nsfw": is_nsfw,
            "age_rating": classification
        }
    return safe_execute(_get)

@mcp.tool()
def update_subreddit_rule(subreddit: str, short_name: str, new_description: Optional[str] = None) -> Dict[str, Any]:
    """Updates the description of an existing subreddit rule.

    Modifies the text of a rule identified by its short name. This requires
    the authenticated user to have 'modconfig' permissions.

    Args:
        subreddit (str): The name of the subreddit. (Required)
        short_name (str): The short name of the rule to update. (Required)
        new_description (Optional[str]): The new description text for the rule. (Optional)

    Returns:
        Dict[str, Any]: A dictionary with a status confirmation message.
    """
    def _update():
        for rule in reddit.subreddit(subreddit).rules:
            if rule.short_name == short_name:
                rule.mod.update(description=new_description)
                return {"status": f"Rule '{short_name}' in r/{subreddit} has been updated."}
        raise ValueError(f"Rule with short_name '{short_name}' not found.")
    return safe_execute(_update)


from typing import Dict, Any

@mcp.tool()
def get_rising_posts(subreddit: str, limit: int = 10) -> Dict[str, Any]:
    """Retrieves posts from a subreddit's "Rising" feed.

    Fetches posts that are new and quickly gaining upvotes, indicating they may
    soon become "hot."

    Args:
        subreddit (str): The name of the subreddit. (Required)
        limit (int): The maximum number of posts to return. Defaults to 10. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing a list of rising posts, each with
                        its title, score, and comment count.
    """
    def _get():
        posts = []
        for submission in reddit.subreddit(subreddit).rising(limit=limit):
            posts.append({
                "title": submission.title,
                "id": submission.id,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "author": str(submission.author)
            })
        return posts
    return safe_execute(_get)


@mcp.tool()
def find_best_answer_in_post(post_id: str, strategy: str = 'top_voted') -> Dict[str, Any]:
    """Finds the most likely 'answer' in a post's comment section.

    Uses a specified strategy to identify a key comment within a post, such as
    the highest-voted comment, a reply from the original poster, or a
    moderator-distinguished comment.

    Args:
        post_id (str): The ID of the post to search within. (Required)
        strategy (str): The method to use: 'top_voted', 'op_reply', or 'mod_reply'.
                        Defaults to 'top_voted'. (Optional)

    Returns:
        Dict[str, Any]: A dictionary containing details of the found comment or
                        a status message if no answer is found.
    """
    valid_strategies = ['top_voted', 'op_reply', 'mod_reply']
    if strategy not in valid_strategies:
        return {"successful": False, "data": {}, "error": f"Invalid strategy. Use one of: {valid_strategies}"}

    def _get():
        submission = reddit.submission(post_id)
        submission.comments.replace_more(limit=None)
        
        found_comment = None

        if strategy == 'top_voted':
            if submission.comments:
                found_comment = submission.comments[0]
        
        elif strategy == 'op_reply':
            for comment in submission.comments.list():
                if comment.author and comment.author == submission.author:
                    found_comment = comment
                    break
                    
        elif strategy == 'mod_reply':
            for comment in submission.comments.list():
                if comment.distinguished == 'moderator':
                    found_comment = comment
                    break

        if found_comment:
            return {
                "strategy_used": strategy,
                "comment_id": found_comment.id,
                "author": str(found_comment.author),
                "body": found_comment.body,
                "score": found_comment.score,
                "is_op": found_comment.author == submission.author,
                "is_mod": found_comment.distinguished == 'moderator'
            }
        else:
            return {"status": f"No answer found using strategy '{strategy}'."}
    return safe_execute(_get)


@mcp.tool()
def get_random_post(subreddit: str) -> Dict[str, Any]:
    """Retrieves a single random submission from a subreddit.

    Fetches a random post from the specified subreddit. Note that this may not
    work if the subreddit has disabled the random post feature.

    Args:
        subreddit (str): The name of the subreddit. (Required)

    Returns:
        Dict[str, Any]: A dictionary containing the details of the random post,
                        or a status message if one could not be found.
    """
    def _get():
        submission = reddit.subreddit(subreddit).random()
        if submission:
            return {
                "title": submission.title,
                "id": submission.id,
                "author": str(submission.author),
                "url": submission.url,
                "score": submission.score
            }
        else:
            return {"status": "Subreddit may not support random mode or is empty."}
    return safe_execute(_get)


if __name__ == "__main__":
    mcp.run()
