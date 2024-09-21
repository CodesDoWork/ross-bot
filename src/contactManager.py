import vobject  # Library to create vCards

class ContactManager:
    def __init__(self, data_source):
        # Load contacts from the provided DataFrame source
        self.contacts = data_source

    def get_contact_by_email(self, email: str):
        # Search for the contact based on the email address
        contact = self.contacts[self.contacts['email'].str.contains(email, case=False, na=False)]
        
        if not contact.empty:
            # If a match is found, return the first result (assuming emails are unique)
            contact = contact.iloc[0]
            return {
                "name": contact["name"],
                "department": contact["department"],
                "position": contact["position"],
                "responsibilities": contact["responsibilities"],
                "email": contact["email"],
                "phone_number": contact["phone"],
                "location": contact["location"],
                "programs": contact["programs"]
            }
        else:
            return None  # No matching contact found

    def create_vcard(self, contact):
        # Create a vCard for the contact
        vcard = vobject.vCard()
        vcard.add('fn').value = contact['name']
        vcard.add('org').value = contact['department']
        vcard.add('title').value = contact['position']
        vcard.add('email').value = contact['email']
        vcard.add('tel').value = contact['phone_number']
        vcard.add('note').value = contact['responsibilities']
        return vcard.serialize()

    def send_contact_by_email(self, bot, chat_id: int, email: str):
        contact = self.get_contact_by_email(email)
        if contact:
            # Send the contact's information as a message
            bot.send_message(
                chat_id=chat_id,
                text=(
                    f"Name: {contact['name']}\n"
                    f"Department: {contact['department']}\n"
                    f"Position: {contact['position']}\n"
                    f"Phone: {contact['phone_number']}\n"
                    f"Email: {contact['email']}\n"
                    f"Location: {contact['location']}\n"
                    f"Responsibilities: {contact['responsibilities']}\n"
                    f"Programs: {contact['programs']}"
                )
            )

            # Create and send the vCard
            vcard = self.create_vcard(contact)
            bot.send_document(chat_id, vcard.encode('utf-8'), caption=f"vCard for {contact['name']}")
        else:
            bot.send_message(chat_id, "Sorry, I couldn't find a contact with that email address.")
