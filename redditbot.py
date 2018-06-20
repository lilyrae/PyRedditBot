import configparser
from RedditManager import RedditManager 

config = configparser.ConfigParser()
config.read('config.ini')

reddit_manager = RedditManager(config['Reddit'])
sub = reddit_manager.get_sub('WeAllLoveChocoRoti')
all_posts = reddit_manager.get_posts_from_sub(sub, 100)

for post in all_posts:
	if reddit_manager.is_repost(post, sub):
		reply = "Hello! This post seems familiar...\n\n"
		for similar_post in reddit_manager.get_most_similar_posts(post, all_posts):
			p = similar_post[1][1]
			score = int(similar_post[1][0])
			reply += f"- [{p.title}]({p.url}) - **{score}**% Similar.\n\n"
		reddit_manager.make_comment(post, reply)