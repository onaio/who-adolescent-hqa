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
from whoahqa.models import Base
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


class Municipality(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.MUNICIPALITY
    }

    __acl__ = [
        (Allow, groups.SUPER_USER, ALL_PERMISSIONS),
        (Allow, Authenticated, perms.CAN_VIEW_MUNICIPALITY)
    ]


class State(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.STATE
    }

    __acl__ = [
        (Allow, groups.SUPER_USER, ALL_PERMISSIONS),
        (Allow, Authenticated, perms.CAN_VIEW_STATE)
    ]
