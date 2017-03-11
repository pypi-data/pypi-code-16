from tempemail import Mailbox

box = Mailbox()
print("Your address is " + box.address)
print("But " + box.get_alt_address() + " also works")
