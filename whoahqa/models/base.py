from pyramid.security import (
    Allow,
    Authenticated,
    ALL_PERMISSIONS,
)

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import desc

from whoahqa.constants import permissions as perms

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class BaseModel(object):

    @classmethod
    def newest(cls):
        return DBSession.query(cls).order_by(desc(cls.id)).first()

    @classmethod
    def get(cls, *criterion):
        return DBSession.query(cls).filter(*criterion).one()

    @classmethod
    def all(cls, *criterion):
        return DBSession.query(cls).filter(*criterion).all()

    @classmethod
    def count(cls, *criterion):
        return DBSession.query(cls).filter(*criterion).count()

    def save(self):
        DBSession.add(self)
        DBSession.flush()

    @classmethod
    def delete(cls, *criterion):
        return DBSession.query(cls).filter(*criterion).delete()

    @classmethod
    def get_or_create(cls, *criterion, **kwargs):
        try:
            instance = cls.get(*criterion)
        except NoResultFound:
            instance = cls(**kwargs)
            instance.save()

        return instance

Base = declarative_base(cls=BaseModel)


class RootFactory(object):
    __acl__ = [
        (Allow, 'g:su', ALL_PERMISSIONS),
        (Allow, Authenticated, perms.AUTHENTICATED)
    ]

    def __init__(self, request):
        self.request = request


class BaseModelFactory(object):

    def __init__(self, request):
        self.request = request

    @property
    def __parent__(self):
        # set root factory as parent to inherit root's acl
        return RootFactory(self.request)
