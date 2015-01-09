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
    ReportingPeriod)
from whoahqa.security import pwd_context

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


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    clinics = relationship("Clinic", secondary=user_clinics)
    group = relationship("Group", secondary=user_groups, uselist=False)

    def get_clinics(self):
        from whoahqa.models import Clinic
        clinics = DBSession.query(Clinic).join(user_clinics).filter(
            user_clinics.columns.user_id == self.id).all()
        return clinics

    @property
    def __acl__(self):
        return [
            (Allow, "u:{}".format(self.id), ALL_PERMISSIONS),
        ]

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
        return {
            'group': self.group
        }


class UserProfile(Base):
    __tablename__ = 'user_profiles'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True,
                     autoincrement=False)
    username = Column(String(100), nullable=False, unique=True)
    pwd = Column(String(255), nullable=False)
    user = relationship('User')

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


class OnaUser(Base):
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

    def __str__(self):
        return self.username

    @property
    def group(self):
        return self.user.group.name

    def update(self, group_name):
        group_criteria = Group.name == group_name
        group_params = {'name': group_name}
        group = Group.get_or_create(
            group_criteria,
            **group_params)

        self.user.group = group

        self.save()


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
