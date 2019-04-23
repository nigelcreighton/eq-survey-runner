from aws_xray_sdk.core import xray_recorder

from app.storage.errors import ItemAlreadyExistsError


class RedisStorage:

    def __init__(self, redis):
        self.redis = redis

    @xray_recorder.capture()
    def put_jti(self, jti):
        record_created = self.redis.set(name=jti.jti_claim,
                                        value=int(jti.used_at.timestamp()),
                                        ex=int((jti.expires - jti.used_at).total_seconds()),
                                        nx=True)

        if not record_created:
            raise ItemAlreadyExistsError()
