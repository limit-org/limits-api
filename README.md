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
 - [x] Modifying personal details
 - [ ] Modifying email
 - [x] Changing password
 - [x] Adding a profile picture
 - [x] Remove a profile picture
 - [x] Adding an alias/name
 - [ ] Currently online/offline
 - [ ] Custom status (should we do??)
 - [ ] Make it so users cant sign up from certain IP addresses. for e.g: common abuse ips (NOT TOR OR VPNS UNLESS THEY BECOME AN ISSUE.)

### Posts
 - [x] Send text only posts (see note #0)
 - [x] Send text posts with media (see note #0)
 
### Site Usability
 - [x] Add search capabilities using Meilisearch (see note #2)
 - [ ] Add topics for users to post to (They work like e.g: "hacking/osint", "networking/LAN", etc..) (see note #1)

### Moderation
 - [ ] Banned domains/links database
 - [ ] Add a way for mods to ban users
 - [ ] Add a way for mods to warn users
 - [ ] Add a way to block other users
 - [ ] Add a way for mods and selves to delete user's posts
 - [ ] Make site rules (What can users do/not do? What is/isn't allowed to be said or done?)
 - [ ] Block certain users from being able to upload media.

### Media/Documents
 - [x] Allow users to upload media
 - [ ] Add media "sidecar" files. These store the information about some media like filename, size, pixels, who uploaded it, duration (if audio or video), etc.
 - [ ] Send alt/description text with media (stored in sidecar files.)
 - [x] Enforce a media size limit.
 - [ ] Allow users to upload documents (What file formats should we support? .pdf,.docx is a must.)
 - [ ] AI NSFW detection in images (Should we do?? plus, will it be accurate enough? maybe NSFWJS?)

### To test
 - [ ] SQL injection and if it's possible (Top priority)
 - [ ] All/most cases of a user typing invalid parameters (Very important)
 
### Security
- [ ] Secure hashing/salting/encryption algorithms for sensitive stored & transferred data (SHA-256 & AES-256) (Need to test)
- [ ] User-supplied input field sanitization (XSS/SQLi)                                                        (Need to test)
- [x] User password minimums (at least 8 chars, 2 special chars, etc.)
- [ ] User-uploaded document/media validation                                                                  (Requires more context)
- [ ] Proper access controls for accounts/posts/admin pages
- [ ] API whitelists for accessing urls/ports                                                                  (Requires more context)
- [ ] No weak/default passwords for admin accounts                                                             (To check/fix, ONLY AFTER TESTING PASSWORD HASHING SECURITY)
- [ ] No plain-text passwords in DB or source code                                                             (To check)
- [ ] No sensitive system information in user-accessible pages (source, github, api, etc.)                      (To check)
- [ ] Use LIMIT or equivalent database controls to limit mass disclosure of records.
- [ ] Use signatures to verify software/data integrity                                                         (Requires more context)
- [ ] Users can add some sort of 2FA authentication.                                                           (How to implement??)

### Notes
 - Note #0: media attachment works, but this is not verified if this method will stay the same, or if it even currently works.
 - Note #1: mostly done, a lot of topics exist, and they need to be imported into CrDB with descriptions, how many posts there are in them, etc.
 - Note #2: done, indexing and searching users and posts works, but may need to add more search capabilities in the future.