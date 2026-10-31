# Root social posts
Push a folder `posts/<date>-<slug>/` with `image.jpg` and `post.json` (`"status": "approved"`) to publish it on
Instagram and the Facebook Page. The Action writes `published.json` with the links. Drafts use `"status": "draft"`.
The Meta token is stored only as the repository secret `META_TOKEN`.
