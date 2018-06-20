import praw
import datetime
import Levenshtein

class RedditManager():
    def __init__(self, reddit_config):
        self.reddit = praw.Reddit(client_id=reddit_config['client_id'],
                     client_secret=reddit_config['client_secret'],
                     password=reddit_config['password'],
                     user_agent=reddit_config['user_agent'],
                     username=reddit_config['username'])
        self.skip_selftext = bool(reddit_config['skip_selftext'])
        self.skip_url = bool(reddit_config['skip_url'])
        self.selftext_weight = float(reddit_config['selftext_weight'])
        self.url_weight = float(reddit_config['url_weight'])
        self.title_weight = float(reddit_config['title_weight'])
        self.minimum_similarity_percentage = float(reddit_config['minimum_similarity_percentage'])
        self.number_similar_posts = int(reddit_config['number_similar_posts'])

    def get_sub(self, sub_name):
        return self.reddit.subreddit(sub_name)

    def get_posts_from_sub(self, sub, lim = 10):
        yield from sub.new(limit=lim)
    
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
            if p.id != post.id and post.created > p.created and self.calculate_post_similarity(p, post) >= self.minimum_similarity_percentage:
                return True
        
        return False

    def calculate_post_similarity(self, p1, p2):
        used_weights = self.title_weight
        total_ratio = self.calculate_levenshtein_distance(p1.title, p2.title) * self.title_weight

        if not self.skip_selftext:
            used_weights += self.selftext_weight
            total_ratio += self.calculate_levenshtein_distance(p1.selftext, p2.selftext) * self.selftext_weight

        if not self.skip_url:
            used_weights += self.url_weight
            total_ratio += self.calculate_url_distance(p1.url, p2.url) * self.url_weight
        
        return total_ratio / used_weights * 100

    def calculate_levenshtein_distance(self, s1, s2):
        return Levenshtein.ratio(s1, s2)

    def calculate_url_distance(self, s1, s2):
        return 1.0 if s1 == s2 else 0.0

    def get_most_similar_posts(self, p, all_posts):
        ordered_posts = {}
        for post in all_posts:
            if p.id == post.id:
                continue
            score = self.calculate_post_similarity(p, post)
            if score >= self.minimum_similarity_percentage:
                ordered_posts[post.id] = [score, post]
        
        return sorted(ordered_posts.items(), key=lambda k: k[0], reverse=True)[0:self.number_similar_posts]