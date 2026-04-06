# CRM & Engagement: Contacts, Conversations, Forms, Events, Media & Libraries

---

## Contacts

### List Contacts
```
GET /api/company/contacts
```

### Create Contact
```
POST /api/company/contacts
```

```json
{
  "contact": {
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@example.com",
    "phone": "+15551234567",
    "source": "website"
  }
}
```

### Get Contact
```
GET /api/company/contacts/:id
```

### Find Contact by Email
```
GET /api/company/contacts/find_by_email?email=jane@example.com
```

### Update Contact
```
PUT /api/company/contacts/:id
```

### Delete Contact
```
DELETE /api/company/contacts/:id
```

### Append Contact Metadata
```
PATCH /api/company/contacts/:id/append_metadata
```

### Export Contacts CSV
```
POST /api/company/contacts/export_csv
```

---

## Customer Notes

### List Customer Notes
```
GET /api/customer_notes
```
Query params: `customer_id`

### Create Customer Note
```
POST /api/customer_notes
```

```json
{
  "customer_note": {
    "customer_id": 123,
    "body": "Called about order #456 — wants to upgrade shipping",
    "note_type": "general"
  }
}
```

---

## Conversations & Messages

### List Conversations
```
GET /api/company/messaging/conversations
```

### Create Conversation
```
POST /api/company/messaging/conversations.json
```

```json
{
  "conversation": {
    "participant_ids": [123, 456],
    "subject": "Order follow-up"
  }
}
```

### Get Conversation
```
GET /api/company/messaging/conversations/:id.json
```

### Send Message
```
POST /api/company/messaging/conversations/:conversation_id/messages.json
```

```json
{
  "message": {
    "body": "Your order has shipped! Tracking: 1Z999AA1",
    "message_type": "text"
  }
}
```

### List Messages
```
GET /api/company/messaging/conversations/:conversation_id/messages.json
```

---

## Forms

### List Forms
```
GET /api/forms
```

### Create Form
```
POST /api/forms
```

```json
{
  "title": "Customer Feedback Survey",
  "description": "Help us improve your experience"
}
```

### Get Form
```
GET /api/forms/:id
```

### Update Form
```
PUT /api/forms/:id
```

### Delete Form
```
DELETE /api/forms/:id
```

### Duplicate Form
```
POST /api/forms/:id/duplicate
```

### Get Form Respondents
```
GET /api/forms/:id/respondents
```

### Respond to Form
```
POST /api/forms/:id/respond
```

### Send Form via Email
```
POST /api/forms/:id/send_mail
```

### Get Form Statistics
```
GET /api/forms/statistics
```

### Export Form Respondents CSV
```
POST /api/forms/:id/export_csv
```

### List Form Elements
```
GET /api/forms/:form_id/form_elements
GET /api/forms/:form_id/form_elements/:id
```

---

## Events

### List Events
```
GET /api/company/events
```

### Create Event
```
POST /api/company/events
```

```json
{
  "event": {
    "title": "Summer Product Launch",
    "description": "Join us for our new collection reveal",
    "start_date": "2024-06-15T18:00:00Z",
    "end_date": "2024-06-15T20:00:00Z",
    "location": "Virtual",
    "event_url": "https://zoom.us/j/123456",
    "image_url": "https://ik.imagekit.io/fluid/.../event.jpg",
    "active": true
  }
}
```

### Get Event
```
GET /api/company/events/:id
```

### Update Event
```
PATCH /api/company/events/:id
```

### Delete Event
```
DELETE /api/company/events/:id
```

### Send Event Notifications
```
GET /api/company/events/:id/send_notifications
```

---

## Announcements

### List Announcements
```
GET /api/company/announcements
```

### Create Announcement
```
POST /api/company/announcements
```

```json
{
  "title": "New Commission Structure",
  "description": "We're excited to announce updated commission rates...",
  "active": true,
  "image_url": "https://ik.imagekit.io/fluid/.../announcement.jpg",
  "video_url": "",
  "media_type": "image",
  "display_comments": true,
  "rank_ids": [1, 2, 3]
}
```

**Key fields:**
- `rank_ids` — Limit visibility to specific ranks
- `application_theme_template_id` — Associate with theme template
- `available_countries` — Limit by country
- `media_type` — `"image"`, `"video"`, `"pdf"`, `"powerpoint"`

### Get Announcement
```
GET /api/company/announcements/:id
```

### Update Announcement
```
PUT /api/company/announcements/:id
```

### Delete Announcement
```
DELETE /api/company/announcements/:id
```

### Bulk Delete Announcements
```
DELETE /api/company/announcements
```

---

## Notifications

### Get Notifications
```
GET /api/company/notifications
```
Returns notifications for the current authenticated user.

---

## Labels

Organization tags for categorizing content.

### List Labels
```
GET /api/company/labels
```

### Create Label
```
POST /api/company/labels
```

```json
{
  "label": {
    "name": "Featured",
    "color": "#FF6B35"
  }
}
```

### Get Label
```
GET /api/company/labels/:id
```

### Update Label
```
PUT /api/company/labels/:id
```

### Delete Label
```
DELETE /api/company/labels/:id
```

### Clear Label Cache
```
POST /api/company/labels/clear_cache
```

---

## Media

### List Media
```
GET /api/company/media
GET /api/media
```

### Create Media
```
POST /api/company/media
POST /api/company/media/create
```

```json
{
  "media": {
    "title": "Product Tutorial",
    "description": "How to use our flagship product",
    "media_type": "video",
    "url": "https://youtube.com/watch?v=...",
    "image_url": "https://ik.imagekit.io/fluid/.../thumbnail.jpg",
    "active": true
  }
}
```

### Get Media
```
GET /api/company/media/:id
```

### Update Media
```
PUT /api/company/media/:id
PATCH /api/company/media/:id
```

### Delete Media
```
DELETE /api/company/media/:id
```

### Prioritize Media (Send to Top)
```
GET /api/company/media/:id/send_to_top
```

### Send Media Notifications to Affiliates
```
GET /api/company/media/:id/send_notifications
```

---

## Libraries

Collections of media content for rep access.

### List Libraries
```
GET /api/company/libraries
```

### Create Library
```
POST /api/company/libraries
```

```json
{
  "library": {
    "title": "Product Training Materials",
    "description": "Everything reps need to know about our products"
  }
}
```

### Get Library
```
GET /api/company/libraries/:id
```

### Update Library
```
PATCH /api/company/libraries/:id
```

### Delete Library
```
DELETE /api/company/libraries/:id
```

### Add Item to Library
```
PUT /api/company/libraries/:library_id/add_item_to_library
```

### Delete Library Item
```
DELETE /api/company/libraries/:id/destroy_library_item
```

### Clone Library
```
POST /api/company/libraries/:id/clone_company_library
```

### Available Playlist Resources
```
GET /api/company/libraries/available_resources_for_playlists
```
