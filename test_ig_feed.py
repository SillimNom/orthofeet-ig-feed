from ig_feed import pick_image_url

assert pick_image_url({"media_type": "VIDEO", "media_url": "v.mp4", "thumbnail_url": "t.jpg"}) == "t.jpg"
assert pick_image_url({"media_type": "IMAGE", "media_url": "i.jpg"}) == "i.jpg"
assert pick_image_url({"media_type": "CAROUSEL_ALBUM", "media_url": "c.jpg"}) == "c.jpg"
assert pick_image_url({"media_type": "IMAGE"}) is None
print("ok")
