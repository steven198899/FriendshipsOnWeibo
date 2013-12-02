import oauth2
from bind import bind_method

MEDIA_ACCEPT_PARAMETERS = ["count", "max_id"]
SEARCH_ACCEPT_PARAMETERS = ["q", "count"]

#SUPPORTED_FORMATS = ['json']


class InstagramAPI(oauth2.OAuth2API):

    host = "api.instagram.com"
    base_path = "/v1"
    access_token_field = "access_token"
    authorize_url = "https://api.instagram.com/oauth/authorize"
    access_token_url = "https://api.instagram.com/oauth/access_token"
    protocol = "https"
    api_name = "Instagram"

    def __init__(self, *args, **kwargs):
        self.format = 'json'
        super(InstagramAPI, self).__init__(*args, **kwargs)

    media_popular = bind_method(
        path="/media/popular",
        accepts_parameters=MEDIA_ACCEPT_PARAMETERS)

    media_search = bind_method(
        path="/media/search",
        accepts_parameters=SEARCH_ACCEPT_PARAMETERS + ['lat', 'lng', 'min_timestamp', 'max_timestamp'])

    media_likes = bind_method(
        path="/media/{media_id}/likes",
        accepts_parameters=['media_id'])

    like_media = bind_method(
        path="/media/{media_id}/likes",
        method="POST",
        accepts_parameters=['media_id'])

    unlike_media = bind_method(
        path="/media/{media_id}/likes",
        method="DELETE",
        accepts_parameters=['media_id'])

    create_media_comment = bind_method(
        path="/media/{media_id}/comments",
        method="POST",
        accepts_parameters=['media_id', 'text'])

    delete_comment = bind_method(
        path="/media/{media_id}/comments/{comment_id}",
        method="DELETE",
        accepts_parameters=['media_id', 'comment_id'])

    media_comments = bind_method(
        path="/media/{media_id}/comments",
        method="GET",
        accepts_parameters=['media_id'])

    media = bind_method(
        path="/media/{media_id}",
        accepts_parameters=['media_id'])

    user_media_feed = bind_method(
        path="/users/self/feed",
        accepts_parameters=MEDIA_ACCEPT_PARAMETERS,
        paginates=True)

    user_liked_media = bind_method(
        path="/users/self/media/liked",
        accepts_parameters=MEDIA_ACCEPT_PARAMETERS,
        paginates=True)

    user_recent_media = bind_method(
        path="/users/{user_id}/media/recent",
        accepts_parameters=MEDIA_ACCEPT_PARAMETERS + ['user_id'],
        paginates=True)

    user_search = bind_method(
        path="/users/search",
        accepts_parameters=SEARCH_ACCEPT_PARAMETERS)

    user_follows = bind_method(
        path="/users/{user_id}/follows",
        accepts_parameters=["user_id", "count"],
        paginates=True)

    user_followed_by = bind_method(
        path="/users/{user_id}/followed-by",
        accepts_parameters=["user_id", "count"],
        paginates=True)

    user = bind_method(
        path="/users/{user_id}",
        accepts_parameters=["user_id"])

    location_recent_media = bind_method(
        path="/locations/{location_id}/media/recent",
        accepts_parameters=MEDIA_ACCEPT_PARAMETERS + ['location_id'],
        paginates=True)

    location_search = bind_method(
        path="/locations/search",
        accepts_parameters=SEARCH_ACCEPT_PARAMETERS + ['lat', 'lng', 'foursquare_id'])

    location = bind_method(
        path="/locations/{location_id}",
        accepts_parameters=["location_id"])

    geography_recent_media = bind_method(
        path="/geographies/{geography_id}/media/recent",
        accepts_parameters=MEDIA_ACCEPT_PARAMETERS + ["geography_id"],
        paginates=True)

    tag_recent_media = bind_method(
        path="/tags/{tag_name}/media/recent",
        accepts_parameters=MEDIA_ACCEPT_PARAMETERS + ['tag_name'],
        paginates=True)

    tag_search = bind_method(
        path="/tags/search",
        accepts_parameters=SEARCH_ACCEPT_PARAMETERS,
        paginates=True)

    tag = bind_method(
        path="/tags/{tag_name}",
        accepts_parameters=["tag_name"],
        response_type="entry")

    user_incoming_requests = bind_method(
        path="/users/self/requested-by")

    change_user_relationship = bind_method(
        method="POST",
        path="/users/{user_id}/relationship",
        accepts_parameters=["user_id", "action"],
        paginates=True,
        requires_target_user=True)

    user_relationship = bind_method(
        method="GET",
        path="/users/{user_id}/relationship",
        accepts_parameters=["user_id"],
        paginates=False,
        requires_target_user=True)

    def _make_relationship_shortcut(action):
      def _inner(self, *args, **kwargs):
        return self.change_user_relationship(user_id=kwargs.get("user_id"),
            action=action)
        return _inner

    follow_user = _make_relationship_shortcut('follow')
    unfollow_user = _make_relationship_shortcut('unfollow')
    block_user = _make_relationship_shortcut('block')
    unblock_user = _make_relationship_shortcut('unblock')
    approve_user_request = _make_relationship_shortcut('approve')
    ignore_user_request = _make_relationship_shortcut('ignore')

    def _make_subscription_action(method, include=None, exclude=None):
      accepts_parameters = ["object",
          "aspect",
          "object_id", # Optional if subscribing to all users
          "callback_url",
          "lat", # Geography
          "lng", # Geography
          "radius", # Geography
          "verify_token"]

      if include:
        accepts_parameters.extend(include)
        if exclude:
          accepts_parameters = [x for x in accepts_parameters if x not in exclude]
        return bind_method(
            path="/subscriptions",
            method=method,
            accepts_parameters=accepts_parameters,
            include_secret=True,
            objectify_response=False
            )

    create_subscription = _make_subscription_action('POST')
    list_subscriptions = _make_subscription_action('GET')
    delete_subscriptions = _make_subscription_action('DELETE', exclude=['object_id'], include=['id'])
