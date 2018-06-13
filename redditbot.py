import configparser
from RedditManager import RedditManager 

config = configparser.ConfigParser()
config.read('config.ini')

reddit_manager = RedditManager(config['Reddit'])
sub = reddit_manager.get_sub('WeAllLoveChocoRoti')
all_posts = reddit_manager.get_posts_from_sub(sub)

for p in all_posts:
	if reddit_manager.is_repost(p, sub):
		reddit_manager.make_comment(p, 'Repost!!')
	else:
		reddit_manager.make_comment(p, 'Freshly Baked from the toilet!!')