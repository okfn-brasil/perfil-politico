from perfil.utils.management.commands import ImportCsvCommand

from perfil.election.management.commands import politician_keys
from perfil.mandate.models import Politician, Tweet


class Command(ImportCsvCommand):

    to_cache = (Politician, politician_keys),
    model = Tweet
    bulk_size = 2 ** 10
    slice_csv = False
    headers = (
        'nbr_retweet',
        'user_id',
        'url',
        'text',
        'usernameTweet',
        'datetime',
        'is_reply',
        'is_retweet',
        'ID',
        'nbr_reply',
        'nbr_favorite',
        'medias',
        'has_media',
        'congressperson_name',
        'congressperson_id',
        'twitter_profile',
        'secondary_twitter_profile',
        'facebook_page',
    )

    def serialize(self, reader, total, progress_bar):
        for row in reader:
            politician_id = self.cache.get(politician_keys(row))
            if politician_id:
                yield Tweet(
                    politician_id=politician_id,
                    url=row['url'],
                    num_retweets=row['nbr_retweet'],
                    num_replys=row['nbr_reply'],
                    num_favorites=row['nbr_favorite'],
                    text=row['text'],
                    is_reply=row['is_reply'],
                    is_retweet=row['is_retweet'],
                    twitter_id=row['ID'],
                )
            else:
                yield None
