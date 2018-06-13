import praw
import datetime

class RedditManager():
    def __init__(self, reddit_config):
        self.reddit = praw.Reddit(client_id=reddit_config['client_id'],
                     client_secret=reddit_config['client_secret'],
                     password=reddit_config['password'],
                     user_agent=reddit_config['user_agent'],
                     username=reddit_config['username'])

    def get_sub(self, sub_name):
        return self.reddit.subreddit(sub_name)

    def get_posts_from_sub(self, sub, lim = 10):
        yield from sub.hot(limit=lim)
    
    def get_comments_from_post(self, post):
        return post.comments.list()

    def make_comment(self, post, message, allow_multiple_comments = False):
        if allow_multiple_comments or not self.already_made_comment(post):
            post.reply(message)

    def already_made_comment(self, post):
        for c in self.get_comments_from_post(post):
            if c.author == self.reddit.user.me():
                return True
        return False

    def find_posts_by_title(self, title, sub, time_filt = 'all', sort_type = 'relevance', syntax_type = 'lucene'):
        yield from sub.search(title, time_filter=time_filt, sort=sort_type, syntax=syntax_type)

    def is_repost(self, post, sub):
        for p in self.find_posts_by_title(post.title, sub):
            if p.id != post.id and p.title == post.title and post.created > p.created:
                return True
        return False