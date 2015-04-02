from whoahqa.views.auth import oauth_authorize, oauth_callback  # noqa
from whoahqa.views.clinics import ClinicViews  # noqa
from whoahqa.views.default_views import default  # noqa
from whoahqa.views.default_views import set_locale  # noqa
from whoahqa.views.request_methods import get_request_user, can_list_clinics  # noqa
from whoahqa.views.request_methods import can_view_clinics  # noqa
from whoahqa.views.request_methods import is_super_user  # noqa
from whoahqa.views.request_methods import can_access_clinics  # noqa
from whoahqa.views.request_methods import can_view_municipality  # noqa
from whoahqa.views.request_methods import can_view_state  # noqa
from whoahqa.views.submissions import SubmissionViews  # noqa
from whoahqa.views.users import UserViews  # noqa
from whoahqa.views.municipalities import MunicipalityViews  # noqa
from whoahqa.views.states import StateViews  # noqa
