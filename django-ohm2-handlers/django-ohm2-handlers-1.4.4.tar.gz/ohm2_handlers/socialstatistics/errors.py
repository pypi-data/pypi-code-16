BASE_ERROR_CODE = 239360

TWITTER_AUTHORIZATION_URL_FAILED = {
	"code" : BASE_ERROR_CODE | 1,
	"message" : "Error getting Twitters authorization url"
}

TWITTER_INVALID_REQUEST_TOKEN = {
	"code" : BASE_ERROR_CODE | 2,
	"message" : "Invalid request token"
}

TWITTER_INVALID_OAUTH_TOKEN = {
	"code" : BASE_ERROR_CODE | 3,
	"message" : "Invalid oauth token"
}

TWITTER_INVALID_OAUTH_VERIFIER = {
	"code" : BASE_ERROR_CODE | 4,
	"message" : "Invalid oauth verifier"
}

FACEBOOK_INVALID_ACCESS_TOKEN_REQUEST = {
	"code" : BASE_ERROR_CODE | 5,
	"message" : "facebook_invalid_access_token_request"
}

FACEBOOK_INVALID_ACCESS_TOKEN = {
	"code" : BASE_ERROR_CODE | 6,
	"message" : "facebook_invalid_access_token"
}

FACEBOOK_INVALID_PAGE_ID = {
	"code" : BASE_ERROR_CODE | 7,
	"message" : "facebook invalid page id"
}