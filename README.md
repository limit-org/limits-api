# limits-api
The limits API.

This is the entire API codebase behind the Limits forum.
All notes can be found at the bottom of this file.
Written by Reiko (https://github.com/acreiko)

## Features:
### Users
 - [x] User creation with an email address
 - [ ] User creation without an email address
 - [x] Logging in
 - [x] Logging out
 - [ ] Modifying personal details (to add + what PD's should we add?)
 - [ ] Changing password
 - [ ] Adding a profile picture
 - [ ] Adding an alias/name (Should we do??)
 - [ ] Currently online/offline
 - [ ] Custom status (???)

### Posts
 - [x] Send text only posts (see note #0)
 - [ ] Send text posts with media
 
### Topics
 - [ ] Create topics for users to post to (THey work like e.g: "hacking/osint", "networking/LAN", etc..)

### Moderation
 - [ ] Banned domains/links database
 - [ ] Add a way for mods to ban users
 - [ ] Add a way for mods to warn users
 - [ ] Add a way to block other users
 - [ ] Add a way for mods and selves to delete user's posts
 - [ ] Make site rules (What can users do/not do? What is/isn't allowed to be said or done?)
 - [ ] Block certain users from being able to upload media.

### Media/Documents
 - [ ] Allow users to upload media
 - [ ] Allow users to upload documents
 - [ ] AI NSFW detection in images (Should we do?? plus, will it be accurate enough? maybe NSFWJS?)

### To test
 - [ ] SQL injection and if it's possible (Top priority)
 - [ ] All/most cases of a user typing invalid parameters (Very important)
 

### Notes
 - Note #0: media attachment works, but this is not verified if this method will stay the same, or if it even currently works.
