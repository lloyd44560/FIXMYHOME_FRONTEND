# =============== Agent Views ===============
from .agentHome import AgentHomeView
from .agentRegister import AgentRegistrationCreateView
from .agentSecurity import AgentEditSecurityView
from .agentUpdate import AgentEditProfileView
from .agentGetBidding import get_bidding
# =============== Bidding Views ===============
from .biddingApproval import BiddingApprovalView
from .biddingList import AgentBidListView
# =============== Job Request Views ===============
from .jobRequestList import ActiveJobsListView
from .jobRequestRegister import AgentJobCreateView
# =============== Property Views ===============
from .propertyRegister import PropertyCreateView
from .propertyUpdate import PropertyUpdateView
from .propertyArchive import archive_property, delete_property
from .propertyDetails import PropertyDetailView
from .propertyList import PropertiesListView
# =============== Renter Views ===============
from .renterInvite import InviteRenterView
from .rentersList import RenterListView
from .renterUpdate import RenterUpdateView
# =============== Room Views ===============
from .roomRegister import RoomCreateView