from .resource import List, Find, Create, Delete, Update


class ExpenseAllocations(List, Find):
    path = "api/v3.0/expense/allocations"


class AttendeeType(List, Find, Update):
    path = "api/v3.0/expense/attendeetypes"


class Attendee(List, Find, Create, Update):
    path = "api/v3.0/expense/attendees"


class ConnectionRequest(List, Find, Create, Update):
    path = "api/v3.2/common/connectionrequest"


class DigitalTaxInvoice(List, Find, Update):
    path = "api/v3.0/expense/digitaltaxinvoices"


class Report(Create, Find, Update):
    path = "api/v3.0/expense/reports"


class Vendor(Delete, List, Create, Update):
    path = "api/v3.0/invoice/vendors"


class VendorGroup(Delete, Update):
    path = "api/v3.0/invoice/vendor/groups"


class VendorBank(Update):
    path = "api/v3.0/invoice/vendor/banks"


class User(List):
    path = "api/v3.0/common/users"


class Supplier(List, Find):
    path = "api/v3.0/common/suppliers"


class SalesTaxValidationRequest(List, Update):
    path = "api/v3.0/invoice/salestaxvalidationrequest"


class Request(List, Find, Update, Create):
    path = "api/v3.1/travelrequest/requests"

    def submit(self):
        self.api.post_request("{0}/{1}/submit".format(self.path, self['ID']))

    def recall(self):
        self.api.post_request("{0}/{1}/recall".format(self.path, self['ID']))


class Receipt(Create):
    path = "api/v3.0/common/receipts"


class ReceiptImage(List, Find, Create, Update):
    path = "api/v3.0/expense/receiptimages"


class QuickExpense(List, Find, Create, Update):
    path = "api/v3.0/expense/quickexpenses"


class PurchaseOrder(Create, Update, Find):
    path = "api/v3.0/invoice/purchaseorders"


class PurchaseOrderReceipt(Delete, List, Create, Update):
    path = "api/v3.0/invoice/purchaseorderreceipts"


class PaymentRequestDiget(List, Find):
    path = "api/v3.0/invoice/paymentrequestdigests"


class PaymentRequest(Find, Create, Update):
    path = "api/v3.0/invoice/paymentrequest"


class Opportunity(List):
    path = "api/v3.0/insights/opportunities"


class Location(List, Find):
    path = "api/v3.0/common/locations"


class LocalizedData(List):
    path = "api/v3.0/invoice/localizeddata"


class CommonList(List, Create, Find):
    path = "api/v3.0/common/lists"


class CommonListItem(List, Create, Delete, Find, Update):
    path = "api/v3.0/common/listitems"


class LatestBooking(List):
    path = "api/v3.0/insights/latestbookings"


class Itemization(List, Create, Delete, Find, Update):
    path = "api/v3.0/expense/itemizations"


class ExpenseGroupConfiguration(List, Find):
    path = "api/v3.0/expense/expensegroupconfigurations"


class EntryAttendeeAssociation(List, Find, Create, Update, Delete):
    path = "api/v3.0/expense/entryattendeeassociations"