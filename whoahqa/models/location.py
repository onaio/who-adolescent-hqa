from collections import defaultdict
from pyramid.security import (
    Allow,
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
from whoahqa.constants import characteristics
from whoahqa.utils import translation_string_factory as _
from whoahqa.utils import clinics_report
from whoahqa.models import (
    Base,
    BaseModelFactory)

from whoahqa.constants import permissions as perms, groups
from ..utils import format_location_name as fmt

AVERAGE_SCORE_KEY = 'average_score'
INITIAL_SCORE_MAP = {characteristics.EQUITABLE: 0,
                     characteristics.ACCESSIBLE: 0,
                     characteristics.ACCEPTABLE: 0,
                     characteristics.APPROPRIATE: 0,
                     characteristics.EFFECTIVE: 0}


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

    _key_indicators = None

    __mapper_args__ = {
        'polymorphic_on': location_type,
        'polymorphic_identity': 'location'
    }

    def key_indicators(self, period):
        clinics = self.clinics
        clinics = [c for c in clinics
                   if c.has_clinic_submissions_for_period(period.form_xpath)]

        if self._key_indicators:
            return self._key_indicators
        else:
            self._key_indicators = clinics_report(clinics, period)

            self._key_indicators = {
                key: (value / len(clinics))
                for key, value in self._key_indicators.items()
                if value is not 0}

            if not self._key_indicators:
                self._key_indicators = defaultdict(int)

            return self._key_indicators

    def __str__(self):
        return fmt(self.name)

    @property
    def appstruct(self):
        return {
            'name': fmt(self.name),
            'location_type': self.location_type,
            'parent_id': self.parent.id if self.parent else None,
        }

    def update(self, **kwargs):
        self.name = kwargs['name']
        self.location_type = kwargs['location_type']
        self.parent = Location.get(Location.id == kwargs['parent_id'])

        self.save()


class Municipality(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.MUNICIPALITY
    }

    child_type = _('Municipality')

    @property
    def __acl__(self):
        acl = [
            (Allow, groups.SUPER_USER, ALL_PERMISSIONS),
        ]
        if self.user is not None:
            acl.append((Allow, "u:{}".format(self.user.id),
                        perms.CAN_VIEW_MUNICIPALITY))

        return acl

    def get_url(self, request, period):
        return request.route_url('municipalities',
                                 traverse=(self.id),
                                 _query={'period': period.id})

    def children(self):
        return self.clinics


class State(Location):
    __mapper_args__ = {
        'polymorphic_identity': Location.STATE
    }

    child_type = _('State')

    @property
    def __acl__(self):
        acl = [
            (Allow, groups.SUPER_USER, ALL_PERMISSIONS),
            (Allow, groups.NATIONAL_OFFICIAL, perms.CAN_VIEW_STATE),
        ]
        if self.user is not None:
            children_perms = [
                (Allow, "u:{}".format(
                    self.user.id), perms.CAN_VIEW_MUNICIPALITY),
                (Allow, "u:{}".format(
                    self.user.id), perms.CAN_LIST_MUNICIPALITY)
            ]
            acl.append((Allow, "u:{}".format(self.user.id),
                        perms.CAN_VIEW_STATE))
            acl.extend(children_perms)

        return acl

    def children(self):
        return Municipality.all(Municipality.parent_id == self.id)

    @property
    def clinics(self):
        municipalities = self.children()
        clinics = [clinic for m in municipalities for clinic in m.clinics]
        return clinics

    def get_url(self, request, period):
        return request.route_url('states',
                                 traverse=(self.id),
                                 _query={'period': period.id})


class LocationFactory(BaseModelFactory):

    @property
    def __parent__(self):
        # reset Parent
        return None

    @property
    def __acl__(self):
        acl = super(LocationFactory, self).__parent__.__acl__

        try:
            traversal_args = self.request.traversed
            location_id = traversal_args[0]
            location = self[location_id]
        except (IndexError, KeyError):
            return acl
        else:
            acl.extend(location.__acl__)
            acl.extend(location.parent.__acl__)

        return acl

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
