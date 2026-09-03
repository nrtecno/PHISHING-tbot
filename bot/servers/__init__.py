from .cam_server import register_cam_routes
from .insta_server import register_insta_routes
from .face_server import register_face_routes
from .twit_server import register_twit_routes  # <-- ADD
from .snap_server import register_snap_routes
from .gmail_server import register_gmail_routes
from .free_server import register_free_routes
from .base import forward_to_user_and_channel
