BASE_ERROR_CODE = 179264

USER_ALREADY_LOGGED_IN = {
	"code" : BASE_ERROR_CODE | 1,
	"message" : "the user is already logged in",
}
USERNAME_TOO_LONG = {
	"code" : BASE_ERROR_CODE | 2,
	"message" : "the username is too long"
}
USER_ALREADY_EXIST = {
	"code" : BASE_ERROR_CODE | 3,
	"message" : "the user already exist"
}
THE_PASSWORD_IS_NOT_SECURE = {
	"code" : BASE_ERROR_CODE | 4,
	"message" : "the password is not secure"
}
INVALID_EMAIL = {
	"code" : BASE_ERROR_CODE | 5,
	"message" : "the email is not valid"
}
INVALID_PASSWORD_RESET = {
	"code" : BASE_ERROR_CODE | 6,
	"message" : "Invalid password reset",
}
PASSWORD_RESET_ALREADY_ACTIVATED = {
	"code" : BASE_ERROR_CODE | 7,
	"message" : "Reset code already activated",
}
SIGNUPS_DISABLED = {
	"code" : BASE_ERROR_CODE | 8,
	"message" : "Signups are currently disabled"
}
INVALID_CURRENT_PASSWORD = {
	"code" : BASE_ERROR_CODE | 9,
	"message" : "Your current password is incorrect"
}
INVALID_USERNAME = {
	"code" : BASE_ERROR_CODE | 10,
	"message" : "Invalid username"
}
PRESIGNUPS_ENABLED = {
	"code" : BASE_ERROR_CODE | 11,
	"message" : "Presignups enabled",
}
PRESIGNUPS_DISABLED = {
	"code" : BASE_ERROR_CODE | 12,
	"message" : "Presignups are disabled",
}
PRESIGNUP_ALREADY_ACTIVATED = {
	"code" : BASE_ERROR_CODE | 13,
	"message" : "Presignup already activated",
}
PRESIGNUPS_FAILED = {
	"code" : BASE_ERROR_CODE | 14,
	"message" : "Presignup failed",
}
WRONG_CREDENTIALS = {
	"code" : BASE_ERROR_CODE | 15,
	"message" : "Wrong credentials",
}
INVALID_FACEBOOK_ACCESS_TOKEN = {
	"code" : BASE_ERROR_CODE | 16,
	"message" : "Invalid Facebook access token",
}
FACEBOOK_CONNECTION_ERROR = {
	"code" : BASE_ERROR_CODE | 17,
	"message" : "An error occured when trying to connect to Facebook",
}
FACEBOOK_EMAIL_PERMISSION_NOT_SETTED = {
	"code" : BASE_ERROR_CODE | 18,
	"message" : "Email permission must be enabled",
}
FACEBOOK_EXPIRED_ACCESS_TOKEN = {
	"code" : BASE_ERROR_CODE | 19,
	"message" : "facebook expired access token",
}
EMAIL_LOGIN_DISABLED = {
	"code" : BASE_ERROR_CODE | 20,
	"message" : "Email login is disabled",
}
EMAIL_ALREADY_REGISTERED = {
	"code" : BASE_ERROR_CODE | 21,
	"message" : "Email already registered",
}
USER_NOT_LOGGED_IN = {
	"code" : BASE_ERROR_CODE | 22,
	"message" : "User must be logged in",
}
ALIAS_ALREADY_TAKEN = {
	"code" : BASE_ERROR_CODE | 23,
	"message" : "This alias is already taken",
}
SIGNUP_PIPELINE_FAILED = {
	"code" : BASE_ERROR_CODE | 24,
	"message" : "Signup pipeline failed",
}