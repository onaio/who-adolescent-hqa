from pyramid.security import (
    Allow,
    ALL_PERMISSIONS)

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import and_
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import (
    backref,
    relationship,
    synonym,
)

from whoahqa.constants import groups
from whoahqa.models import (
    Base,
    BaseModelFactory,
    DBSession,
    Location,
    ReportingPeriod)
from whoahqa.security import pwd_context

LOCATION_MAP = {
    groups.MUNICIPALITY_MANAGER: 'municipality',
    groups.STATE_OFFICIAL: 'state',
    groups.USER: ''
}

user_clinics = Table(
    'user_clinics',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('clinic_id', Integer, ForeignKey('clinics.id'), nullable=False),
    PrimaryKeyConstraint('user_id', 'clinic_id')
)


user_groups = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('group_id', Integer, ForeignKey('groups.id'), nullable=False),
    PrimaryKeyConstraint('user_id', 'group_id')
)


user_locations = Table(
    'user_locations',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('location_id', Integer, ForeignKey('locations.id'), nullable=False),
    PrimaryKeyConstraint('user_id', 'location_id')
)


def delete_user_clinics(clinic_id_list):
    statement = user_clinics.delete(
        user_clinics.c.clinic_id.in_(clinic_id_list))
    statement.execute()


def delete_user_locations(user, location):
    statement = user_locations.delete()\
                              .where(and_(
                                  user_locations.c.user_id == user.id,
                                  user_locations.c.location_id == location.id))
    statement.execute()


def delete_user_groups(user, group):
    statement = user_groups.delete()\
                           .where(and_(user_groups.c.group_id == group.id,
                                  user_groups.c.user_id == user.id))
    statement.execute()


class UpdateableUser(object):
    def update(self, values):
        group_name = values['group']

        # check if new group is the same as previous group
        # add new location selected to location table
        # if group is clinic manager, add clinics selected to clinics list

        if self.user.group is None or self.user.group.name != group_name:
            group_criteria = Group.name == group_name
            group_params = {'name': group_name}
            group = Group.get_or_create(
                group_criteria,
                **group_params)

            self.user.group = group
        if group_name == groups.SUPER_USER:
            # remove any location/clinic references
            if self.user.location:
                delete_user_locations(self.user, self.user.location)
            if self.user.clinics:
                delete_user_clinics([c.id for c in self.user.clinics])

        elif group_name == groups.CLINIC_MANAGER:
            # Remove existing location mapping
            if self.user.location:
                delete_user_locations(self.user, self.user.location)

            from whoahqa.models import Clinic

            clinic_id_list = values['clinics']
            clinics = Clinic.all(Clinic.id.in_(clinic_id_list))

            self.user.clinics = clinics
            # add clinics to user
        else:
            # Remove existing clinic mapping
            if self.user.clinics:
                delete_user_clinics([c.id for c in self.user.clinics])

            location_id = values.get(LOCATION_MAP[group_name], '')

            if location_id != '':
                self.user.location = Location.get(Location.id == location_id)

        self.save()


class User(Base, UpdateableUser):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    clinics = relationship("Clinic", secondary=user_clinics)
    group = relationship("Group", secondary=user_groups, uselist=False)
    location = relationship('Location',
                            secondary=user_locations,
                            backref=backref('user', uselist=False),
                            cascade="save-update",
                            uselist=False)

    def get_clinics(self):
        from whoahqa.models import Clinic
        clinics = DBSession.query(Clinic).join(user_clinics).filter(
            user_clinics.columns.user_id == self.id).all()
        return clinics

    def get_municipality_from_clinics(self):
        if self.clinics:
            return self.clinics[0].municipality

    @property
    def user(self):
        return self

    @property
    def username(self):
        username = ""

        if self.ona_user is not None:
            username = self.ona_user.username
        else:
            username = self.profile.username

        return username

    @property
    def __acl__(self):
        return [
            (Allow, "u:{}".format(self.id), ALL_PERMISSIONS),
        ]

    def __str__(self):
        if self.username != "":
            return self.username

    @property
    def settings(self):
        user_settings = UserSettings.get_or_create(user=self)
        return user_settings

    def __getitem__(self, item):
        # retrieve the reporting period
        try:
            period_id = int(item)
            period = ReportingPeriod.get(ReportingPeriod.id == period_id)
        except (ValueError, NoResultFound):
            raise KeyError
        else:
            period.__parent__ = self
            period.__name__ = item
            return period

    @property
    def appstruct(self):
        municipality_id = None
        state_id = None

        if self.location:
            if self.location.location_type == Location.MUNICIPALITY:
                municipality_id = self.location.id
            else:
                state_id = self.location.id

        return {
            'group': self.group,
            'clinics': [c.id for c in self.clinics],
            'municipality': municipality_id,
            'state': state_id
        }

    def update(self, values):
        # Create user object and save
        super(User, self).update(values)

        user_profile = UserProfile(username=values['username'],
                                   email=values['email'],
                                   password=values['password'],
                                   user=self)
        user_profile.save()


class UserProfile(Base):
    __tablename__ = 'user_profiles'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True,
                     autoincrement=False)
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(50), nullable=True, unique=True)
    pwd = Column(String(255), nullable=False)
    user = relationship('User', backref=backref('profile', uselist=False))

    def check_password(self, password):
        # always return false if password is greater than 255 to avoid
        # spoofing attacks
        if len(password) > 255:
            return False
        return pwd_context.verify(password, self.pwd)

    @property
    def password(self):
        return self.pwd

    @password.setter
    def password(self, value):
        from whoahqa.security import pwd_context
        self.pwd = pwd_context.encrypt(value)

    password = synonym('_password', descriptor=password)


class UserSettings(Base):
    __tablename__ = 'user_settings'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True,
                     autoincrement=False)
    language = Column(String(2), default='pt')
    user = relationship('User')


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    def __str__(self):
        return self.name


class OnaUser(Base, UpdateableUser):
    __tablename__ = 'ona_users'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True,
                     autoincrement=False)
    username = Column(String(255), nullable=False, unique=True)
    refresh_token = Column(String(255), nullable=False)
    user = relationship('User', backref=backref('ona_user', uselist=False))

    @classmethod
    def get_or_create_from_api_data(cls, user_data, refresh_token):
        username = user_data.get('username', "")
        if username is None or (not username.strip()):
            raise ValueError("Invalid user profile data")

        username = user_data['username']
        try:
            ona_user = OnaUser.get(OnaUser.username == username)
            ona_user.refresh_token = refresh_token
        except NoResultFound:
            # By Default, all new users are in the user group
            group_criteria = Group.name == groups.USER
            group_params = {'name': groups.USER}
            user_group = Group.get_or_create(
                group_criteria,
                **group_params)

            user = User()
            user.group = user_group
            ona_user = OnaUser(username=username, refresh_token=refresh_token)
            ona_user.user = user
        DBSession.add(ona_user)
        return ona_user

    @property
    def id(self):
        return self.user_id

    def __str__(self):
        return self.username


class UserFactory(BaseModelFactory):
    __acl__ = []

    def __getitem__(self, item):
        # try to retrieve the user whose id matches item
        try:
            user_id = int(item)
            user = DBSession.query(User).filter_by(id=user_id).one()
        except (ValueError, NoResultFound):
            raise KeyError
        else:
            user.__parent__ = self
            user.__name__ = item
            return user
