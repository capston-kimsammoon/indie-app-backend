"""적당한 메시지

Revision ID: f65a67fd7cee
Revises:
Create Date: 2025-09-16 00:52:00.243261
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "f65a67fd7cee"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(insp: inspect, name: str) -> bool:
    return insp.has_table(name)


def _has_index(insp: inspect, table: str, index_name: str) -> bool:
    try:
        idx = insp.get_indexes(table)
    except Exception:
        return False
    return any(i.get("name") == index_name for i in idx)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    insp = inspect(bind)

    # artist
    if not _has_table(insp, "artist"):
        op.create_table(
            "artist",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("image_url", sa.String(length=300), nullable=True),
            sa.Column("spotify_url", sa.String(length=300), nullable=True),
            sa.Column("instagram_account", sa.String(length=100), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(insp, "artist", op.f("ix_artist_id")):
        op.create_index(op.f("ix_artist_id"), "artist", ["id"], unique=False)
    if not _has_index(insp, "artist", op.f("ix_artist_name")):
        op.create_index(op.f("ix_artist_name"), "artist", ["name"], unique=False)

    # magazine
    if not _has_table(insp, "magazine"):
        op.create_table(
            "magazine",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(insp, "magazine", op.f("ix_magazine_id")):
        op.create_index(op.f("ix_magazine_id"), "magazine", ["id"], unique=False)

    # user
    if not _has_table(insp, "user"):
        op.create_table(
            "user",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("kakao_id", sa.String(length=100), nullable=False),
            sa.Column("nickname", sa.String(length=100), nullable=True),
            sa.Column("profile_url", sa.String(length=300), nullable=True),
            sa.Column("alarm_enabled", sa.Boolean(), nullable=False),
            sa.Column("location_enabled", sa.Boolean(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("nickname"),
        )
    if not _has_index(insp, "user", op.f("ix_user_id")):
        op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)
    if not _has_index(insp, "user", op.f("ix_user_kakao_id")):
        op.create_index(op.f("ix_user_kakao_id"), "user", ["kakao_id"], unique=True)

    # venue
    if not _has_table(insp, "venue"):
        op.create_table(
            "venue",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("address", sa.String(length=200), nullable=False),
            sa.Column("region", sa.String(length=100), nullable=False),
            sa.Column("instagram_account", sa.String(length=100), nullable=False),
            sa.Column("image_url", sa.String(length=200), nullable=True),
            sa.Column("latitude", sa.Float(), nullable=False),
            sa.Column("longitude", sa.Float(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(insp, "venue", op.f("ix_venue_id")):
        op.create_index(op.f("ix_venue_id"), "venue", ["id"], unique=False)

    # magazine_block
    if not _has_table(insp, "magazine_block"):
        op.create_table(
            "magazine_block",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("magazine_id", sa.Integer(), nullable=False),
            sa.Column("order", sa.Integer(), nullable=False),
            sa.Column(
                "type",
                sa.Enum("text", "image", "quote", "embed", "divider", name="mag_block_type"),
                server_default="text",
                nullable=False,
            ),
            sa.Column("text", sa.Text(), nullable=True),
            sa.Column("image_url", sa.String(length=500), nullable=True),
            sa.Column("caption", sa.String(length=300), nullable=True),
            sa.Column(
                "align",
                sa.Enum("left", "center", "right", name="mag_img_align"),
                server_default="center",
                nullable=True,
            ),
            sa.Column("meta", sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(["magazine_id"], ["magazine.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(insp, "magazine_block", op.f("ix_magazine_block_magazine_id")):
        op.create_index(
            op.f("ix_magazine_block_magazine_id"),
            "magazine_block",
            ["magazine_id"],
            unique=False,
        )

    # notification
    if not _has_table(insp, "notification"):
        op.create_table(
            "notification",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("type", sa.String(length=32), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("link_url", sa.String(length=300), nullable=True),
            sa.Column("payload_json", sa.String(length=64), nullable=True),
            sa.Column("is_read", sa.Boolean(), server_default=sa.text("0"), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "type", "payload_json", name="uq_notification_user_type_payload"),
        )
    if not _has_index(insp, "notification", "ix_notification_user_created"):
        op.create_index("ix_notification_user_created", "notification", ["user_id", "created_at"], unique=False)

    # performance
    if not _has_table(insp, "performance"):
        op.create_table(
            "performance",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("venue_id", sa.Integer(), nullable=False),
            sa.Column("date", sa.Date(), nullable=False),
            sa.Column("time", sa.Time(), nullable=False),
            sa.Column("ticket_open_date", sa.Date(), nullable=True),
            sa.Column("ticket_open_time", sa.Time(), nullable=True),
            sa.Column("online_onsite", sa.String(length=100), nullable=False),
            sa.Column("price", sa.Integer(), nullable=False),
            sa.Column("image_url", sa.String(length=300), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("shortcode", sa.String(length=100), nullable=True),
            sa.Column("detail_url", sa.String(length=300), nullable=False),
            sa.ForeignKeyConstraint(["venue_id"], ["venue.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(insp, "performance", op.f("ix_performance_id")):
        op.create_index(op.f("ix_performance_id"), "performance", ["id"], unique=False)

    # post
    if not _has_table(insp, "post"):
        op.create_table(
            "post",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(length=200), nullable=True),
            sa.Column("content", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("thumbnail_filename", sa.String(length=200), nullable=True),
            sa.Column("is_reported", sa.Boolean(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(insp, "post", op.f("ix_post_id")):
        op.create_index(op.f("ix_post_id"), "post", ["id"], unique=False)

    # review
    if not _has_table(insp, "review"):
        op.create_table(
            "review",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("venue_id", sa.Integer(), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["venue_id"], ["venue.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(insp, "review", op.f("ix_review_id")):
        op.create_index(op.f("ix_review_id"), "review", ["id"], unique=False)

    # user_artist_ticketalarm
    if not _has_table(insp, "user_artist_ticketalarm"):
        op.create_table(
            "user_artist_ticketalarm",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("artist_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["artist_id"], ["artist.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("user_id", "artist_id"),
        )

    # user_favorite_artist
    if not _has_table(insp, "user_favorite_artist"):
        op.create_table(
            "user_favorite_artist",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("artist_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["artist_id"], ["artist.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("user_id", "artist_id"),
        )

    # comment
    if not _has_table(insp, "comment"):
        op.create_table(
            "comment",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("post_id", sa.Integer(), nullable=False),
            sa.Column("parent_comment_id", sa.Integer(), nullable=True),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["parent_comment_id"], ["comment.id"]),
            sa.ForeignKeyConstraint(["post_id"], ["post.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(insp, "comment", op.f("ix_comment_id")):
        op.create_index(op.f("ix_comment_id"), "comment", ["id"], unique=False)

    # performance_artist
    if not _has_table(insp, "performance_artist"):
        op.create_table(
            "performance_artist",
            sa.Column("performance_id", sa.Integer(), nullable=False),
            sa.Column("artist_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["artist_id"], ["artist.id"]),
            sa.ForeignKeyConstraint(["performance_id"], ["performance.id"]),
            sa.PrimaryKeyConstraint("performance_id", "artist_id"),
        )

    # post_image
    if not _has_table(insp, "post_image"):
        op.create_table(
            "post_image",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("post_id", sa.Integer(), nullable=False),
            sa.Column("image_url", sa.String(length=300), nullable=False),
            sa.ForeignKeyConstraint(["post_id"], ["post.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(insp, "post_image", op.f("ix_post_image_id")):
        op.create_index(op.f("ix_post_image_id"), "post_image", ["id"], unique=False)

    # post_like
    if not _has_table(insp, "post_like"):
        op.create_table(
            "post_like",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("post_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["post_id"], ["post.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "post_id", name="unique_user_post_like"),
        )
    if not _has_index(insp, "post_like", op.f("ix_post_like_id")):
        op.create_index(op.f("ix_post_like_id"), "post_like", ["id"], unique=False)

    # stamp
    if not _has_table(insp, "stamp"):
        op.create_table(
            "stamp",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("performance_id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["performance_id"], ["performance.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("user_id", "performance_id"),
        )

    # user_favorite_performance
    if not _has_table(insp, "user_favorite_performance"):
        op.create_table(
            "user_favorite_performance",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("performance_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["performance_id"], ["performance.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("user_id", "performance_id"),
        )

    # user_performance_open_alarm
    if not _has_table(insp, "user_performance_open_alarm"):
        op.create_table(
            "user_performance_open_alarm",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("performance_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["performance_id"], ["performance.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("user_id", "performance_id"),
        )
    if not _has_index(insp, "user_performance_open_alarm", op.f("ix_user_performance_open_alarm_performance_id")):
        op.create_index(
            op.f("ix_user_performance_open_alarm_performance_id"),
            "user_performance_open_alarm",
            ["performance_id"],
            unique=False,
        )
    if not _has_index(insp, "user_performance_open_alarm", op.f("ix_user_performance_open_alarm_user_id")):
        op.create_index(
            op.f("ix_user_performance_open_alarm_user_id"),
            "user_performance_open_alarm",
            ["user_id"],
            unique=False,
        )

    # user_performance_ticketalarm
    if not _has_table(insp, "user_performance_ticketalarm"):
        op.create_table(
            "user_performance_ticketalarm",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("performance_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["performance_id"], ["performance.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("user_id", "performance_id"),
        )


def downgrade() -> None:
    """Downgrade schema (best-effort: only drop if exists)."""
    bind = op.get_bind()
    insp = inspect(bind)

    def _drop_index_if_exists(table: str, name: str):
        if _has_index(insp, table, name):
            op.drop_index(name, table_name=table)

    def _drop_table_if_exists(name: str):
        if _has_table(insp, name):
            op.drop_table(name)

    _drop_table_if_exists("user_performance_ticketalarm")
    _drop_index_if_exists("user_performance_open_alarm", op.f("ix_user_performance_open_alarm_user_id"))
    _drop_index_if_exists("user_performance_open_alarm", op.f("ix_user_performance_open_alarm_performance_id"))
    _drop_table_if_exists("user_performance_open_alarm")
    _drop_table_if_exists("user_favorite_performance")
    _drop_table_if_exists("stamp")
    _drop_index_if_exists("post_like", op.f("ix_post_like_id"))
    _drop_table_if_exists("post_like")
    _drop_index_if_exists("post_image", op.f("ix_post_image_id"))
    _drop_table_if_exists("post_image")
    _drop_table_if_exists("performance_artist")
    _drop_index_if_exists("comment", op.f("ix_comment_id"))
    _drop_table_if_exists("comment")
    _drop_table_if_exists("user_favorite_artist")
    _drop_table_if_exists("user_artist_ticketalarm")
    _drop_index_if_exists("review", op.f("ix_review_id"))
    _drop_table_if_exists("review")
    _drop_index_if_exists("post", op.f("ix_post_id"))
    _drop_table_if_exists("post")
    _drop_index_if_exists("performance", op.f("ix_performance_id"))
    _drop_table_if_exists("performance")
    _drop_index_if_exists("notification", "ix_notification_user_created")
    _drop_table_if_exists("notification")
    _drop_index_if_exists("magazine_block", op.f("ix_magazine_block_magazine_id"))
    _drop_table_if_exists("magazine_block")
    _drop_index_if_exists("venue", op.f("ix_venue_id"))
    _drop_table_if_exists("venue")
    _drop_index_if_exists("user", op.f("ix_user_kakao_id"))
    _drop_index_if_exists("user", op.f("ix_user_id"))
    _drop_table_if_exists("user")
    _drop_index_if_exists("magazine", op.f("ix_magazine_id"))
    _drop_table_if_exists("magazine")
    _drop_index_if_exists("artist", op.f("ix_artist_name"))
    _drop_index_if_exists("artist", op.f("ix_artist_id"))
    _drop_table_if_exists("artist")
