from collections import defaultdict
from pyramid.security import (
    Allow,
    Authenticated,
    ALL_PERMISSIONS
)

from sqlalchemy import (
    Column,
    Integer,
    Text,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound
from whoahqa.models import (
    Base,
    BaseModelFactory)
from whoahqa.constants import permissions as perms, groups


class Location(Base):
    __tablename__ = 'locations'

    MUNICIPALITY = 'municipality'
    STATE = 'state'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey('locations.id'), nullable=True)

    location_type = Column(Enum(MUNICIPALITY, STATE,
                           name='LOCATION_TYPES'),
                           nullable=False, index=True)
    parent = relationship("Location", remote_side=[id])

    __mapper_args__ = {
        'polymorphic_on': location_type,
        'polymorphic_identity': 'location'
    }

    def key_indicators(self, period):
        return defaultdict(int)


class Municipality(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.MUNICIPALITY
    }

    __acl__ = [
        (Allow, groups.SUPER_USER, ALL_PERMISSIONS),
        (Allow, Authenticated, perms.CAN_VIEW_MUNICIPALITY),
        (Allow, Authenticated, perms.CAN_LIST_MUNICIPALITY)
    ]

    def get_url(self, request, period):
        return request.route_url('municipalities',
                                 traverse=(self.id),
                                 _query={'period': period.id})


class State(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.STATE
    }

    __acl__ = [
        (Allow, groups.SUPER_USER, ALL_PERMISSIONS),
        (Allow, Authenticated, perms.CAN_VIEW_STATE)
    ]


class LocationFactory(BaseModelFactory):
    def __getitem__(self, item):
        try:
            location_id = int(item)
            location = Location.get(Location.id == location_id)
        except(ValueError, NoResultFound):
            raise KeyError
        else:
            location.__parent__ = self
            location.__name__ = item
            return location
