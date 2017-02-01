
BASE_ERROR_CODE = 32768

INVALID_JSON_OBJECT = {
	"code": BASE_ERROR_CODE | 1, "message": "Invalid JSON object",
}
INVALID_DB_TYPE = {
	"code": BASE_ERROR_CODE | 2, "message": 'invalid db type',
}
INVALID_STRING = {
	"code": BASE_ERROR_CODE | 3, "message": 'invalid string'
}
INVALID_EMAIL = {
	"code" : BASE_ERROR_CODE | 4, "message":  'invalid email',
}
INVALID_PASSWORD = {
	"code": BASE_ERROR_CODE | 5, "message": 'invalid password'
}
INVALID_BOOL = {
	"code": BASE_ERROR_CODE | 6, "message" : 'invalid bool',
}
WRONG_TYPE = {
	"code": BASE_ERROR_CODE | 7, "message" : 'wrong type'
}
INVALID_FILE = {
	"code" : BASE_ERROR_CODE | 8, "message" : 'invalid file',
}
INVALID_UPLOAD_FILE = {
	"code" : BASE_ERROR_CODE | 9, "message" : 'invalid upload file',
}
INVALID_IP_ADDRESS = {
	"code" : BASE_ERROR_CODE | 10, "message" : 'invalid ip address',
}
INVALID_REQUEST = {
	"code" : BASE_ERROR_CODE | 11, "message" : 'invalid request'
}
INVALID_CUSTOM_REQUEST = {
	"code" : BASE_ERROR_CODE | 12, "message" : 'invalid custom request'
}
INVALID_USERNAME = {
	"code" : BASE_ERROR_CODE | 13, "message" : 'invalid username',
}
INVALID_MIX_TYPE = {
	"code" : BASE_ERROR_CODE | 15, "message" : 'invalid mix type',
}
INVALID_REGEX = {
	"code" : BASE_ERROR_CODE | 16, "message" : 'invalid regex',
}
INVALID_TYPE = {
	"code" : BASE_ERROR_CODE | 17, "message" : 'invalid type',
}
QUERY_SET = {
	"code" : BASE_ERROR_CODE | 18, "message" : 'error processing queryset'
}
NO_UNIQUE_STRING_FOUND = {
	"code" : BASE_ERROR_CODE | 19, "message" : 'no unique string found',
}
NO_UNIQUE_RANDOM_FOUND = {
	"code" : BASE_ERROR_CODE | 20, "message" : 'no unique random found',
}
ERROR_SENDING_REQUEST = {
	"code" : BASE_ERROR_CODE | 21, "message" : 'Error sending request',
}
INVALID_URL = {
	"code" : BASE_ERROR_CODE | 22, "message" : 'invalid url',
}
INVALID_NUMBER = {
	"code" : BASE_ERROR_CODE | 23, "message" : 'invalid number',
}
INVALID_DEVICE = {
	"code" : BASE_ERROR_CODE | 24, "message" : 'invalid device',
}
NO_EMAIL_HANDLER_PROVIDED = {
	"code" : BASE_ERROR_CODE | 25, "message" : 'no email handler provided',
}