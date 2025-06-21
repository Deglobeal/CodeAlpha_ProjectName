API-based backend for an Event Registration System with these core features:

Events and User Registrations Models

Endpoints: view all events, single event detail, register for an event, view/cancel your registrations

User linking (authenticated users)

Optional Admin and Organizer role

api endpoints 

1. Authentication Endpoints
Method	Endpoint	Description	Auth Required
POST	/api/token/	Obtain JWT access/refresh tokens	No
POST	/api/token/refresh/	Refresh access token	No
2. Event Management
Method	Endpoint	Description	Auth Required
GET	/api/events/	List all events	No
POST	/api/events/	Create new event	Yes
GET	/api/events/<int:pk>/	Get event details	Yes
PUT	/api/events/<int:pk>/	Update event	Yes
DELETE	/api/events/<int:pk>/	Delete event	Yes
3. Registration Management
Method	Endpoint	Description	Auth Required
POST	/api/register/	Register for an event	Yes
GET	/api/my-registrations/	List user's active registrations	Yes
PATCH	/api/cancel-registration/<int:pk>/	Cancel a registration	Yes