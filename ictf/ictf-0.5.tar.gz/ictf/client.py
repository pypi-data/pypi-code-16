#
# The iCTF game client.
#
# Written by subwire and the iCTF team, 2015
#
# Because websites are so 1995.
#
from builtins import input
import json
import requests
import base64
import random

DEFAULT_GAME_INTERFACE = "https://api.ictf2017.net/"


class iCTF(object):
    """
    The iCTF client!

    If you're just getting started, you probably want to register a team.
    You can access the interactive registration wizard like this:
    >>> from ictf import iCTF()
    >>> i = iCTF()
    >>> i.register_wizard()

    Afterward, your password will be emailed to the email address you specified.
    With that, you can now login:
    >>> t = i.login('team@acme.edu', 'asdfSLKDFSJL')

    Check out the other methods in this class for all kinds of useful functions.

    Have fun!
    - The iCTF Team
    """

    def __init__(self, game_interface=DEFAULT_GAME_INTERFACE):
        self.game_url = game_interface
        self._token = None

    def _post_json(self,endpoint,j):
        # EG says: Why can't Ubuntu stock a recent version of Requests??? Ugh.
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        resp = requests.post(self.game_url + endpoint, data=json.dumps(j), headers=headers)
        try:
            js = json.loads(resp.content.decode('utf-8'))
            return js, resp.status_code
        except:
            return "", resp.status_code


    def _get_json(self, endpoint):
        resp = requests.get(self.game_url + endpoint)
        try:
            js = json.loads(resp.content.decode('utf-8'))
            return js, resp.status_code
        except:
            return "", resp.status_code

    # Flag parameters, borrowed from the gamebot
    FLAG_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    FLAG_LENGTH = 13
    FLAG_PREFIX = "FLG"
    FLAG_SUFFIX = ""

    @staticmethod
    def generate_flag():
        """Generates flags, in the same manner as the game bot.
           This is useful for creating realistic-looking benign traffic for services.

        :return: Flag following the predefined flag format.
        """
        flag = "".join(random.choice(iCTF.FLAG_ALPHABET)
                   for _ in range(iCTF.FLAG_LENGTH))
        return "{0}{1}{2}".format(iCTF.FLAG_PREFIX, flag, iCTF.FLAG_SUFFIX)


    def get_metadata_labels(self):
        resp, code = self._get_json("api/metadata")
        if code == 200:
            return resp
        if isinstance(resp,dict) and 'message' in resp:
            raise RuntimeError(resp['message'])
        else:
            raise RuntimeError("An unknown error occurred contacting the iCTF server!")

    def register_team(self, name, email, country, logo=None, url="", metadata={}):
        """
        Register a team
        :param name: The team name
        :param email: The team's primary POC email
        :param country: The team's 2-letter ISO country code
        :param url: The team's URL (optional)
        :param logo: File path to the team's PNG logo, 256x256 (optional)
        :param metadata: Dictionary of metadata responses.  See "get_metadata_labels"
        :return: A CAPTCHA! (Yes! Really!)
        """

        args = {'name':name,
                'team_email': email,
                'country': country,
                'url': url,
                'metadata': metadata}
        if logo:
            try:
                with open(logo,'rb') as f:
                    logo_data = base64.b64encode(f.read())
                    args['logo'] = logo_data
            except:
                raise RuntimeError("Could not open logo file!")

        resp, code = self._post_json('api/team', args)
        if code == 200:
            return resp['captcha']
        if isinstance(resp,dict) and 'message' in resp:
            raise RuntimeError(resp['message'])
        else:
            raise RuntimeError("An unknown error occurred contacting the iCTF server!")

    def verify(self, response):
        """
        Verify a captcha response, and sign up your team!
        This will send an email to your POCs with your team password!
        :param response: The CAPTCHA response
        :return: None
        """
        args = {'response': response.strip()}
        ret, code = self._post_json('api/team/verify', args)
        return ret

    def register_wizard(self):
        """
        The interactive iCTF setup wizard! OMFG!!
        Walks you through signup, including entering metadata,
        CAPTCHA, etc
        :return: none
        """
        labels_ret = self.get_metadata_labels()
        if not labels_ret:
            print("Error connecting to iCTF server")
            return
        labels = labels_ret['labels']
        print("Hi! Welcome to iCTF! ")
        args = {}
        args['name'] = input("Please enter your team name: ")
        args['team_email'] = input("Please enter your team's primary POC email.  "
                                   "We will send the game password here: ")
        args['url'] = input("[optional] Please enter a URL for your team (e.g., team's web page): ")
        while True:
            try:
                logo_fp = input("[optional] Please enter the local file path to your team's logo (a 256x256 PNG): ")
                if not logo_fp.strip():
                    print("OK fine, going without a logo.")
                    break
                with open(logo_fp,'rb') as f:
                    args['logo'] = base64.b64encode(f.read()).decode('utf-8')
                    break
            except:
                print("Couldn't open logo! Try again.")

        args['country'] = input("Please enter your two-letter ISO country code. (eg. US, DE, JP, etc): ").upper()
        print("Great.  Now take our short registration survey.")
        metadata = {}
        for q in labels:
            metadata[q['id']] = input(q['description'] + " ")
        args['metadata'] = metadata
        resp, code = self._post_json("api/team", args)
        if code != 200:
            print(resp['message'])
            return
        print("Cool! Now prove you're human.")
        print(resp['captcha'])
        print("Yeah.  That's seriously a CAPTCHA.")
        while True:
            captcha_resp = input("Enter the 8 uppercase letters you see:")
            answer = self.verify(captcha_resp)
            if 'message' in answer and answer['message'].startswith('Account creation failed'):
                raise RuntimeError(answer['message'])
            elif 'message' in answer and answer['message'].startswith('Incorrect'):
                print(answer['message'])
            else:
                print(answer['message'])
                break
            print("Oops! Try again.")
        print("Great! You're done.  Go check your email for your password!  Then try iCTF.login()")

    def login(self, username, password):
        """
        Log into iCTF
        :param username: The team's username (email address)
        :param password: The team's password, sent via email
        :return: An auth token (Which is also saved to the iCTF object)
        """
        args = {'email': username, 'password': password}
        resp, code = self._post_json('api/login', args)
        if code != 200:
            if isinstance(resp,dict) and 'message' in resp:
                raise RuntimeError(resp['message'])
            else:
                raise RuntimeError("An unknown error occurred contacting the iCTF server!")

        self._token = resp['token']
        return Team(self._token, username, game_url=self.game_url)

    def reset_password(self, team_email):
        args = {}
        args['team_email'] = team_email
        ret, code =  self._post_json("api/reset", args)
        return ret


class Team(object):
    """
    This object represents a logged-in iCTF team.
    This object can be used to perform actions on behalf of the team, such as submitting game artifacts
    """

    def __init__(self, token, email, game_url=DEFAULT_GAME_INTERFACE):
        self._token = token
        self._email = email
        self.game_url = game_url

    def __str__(self):
        return "<Team %s>" % self._email

    def _post_json(self,endpoint,j):
        # EG says: Why can't Ubuntu stock a recent version of Requests??? Ugh.
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        resp = requests.post(self.game_url + endpoint, auth=(self._token, ""), data=json.dumps(j), headers=headers)
        try:
            js = json.loads(resp.content)
            return js, resp.status_code
        except:
            return "", resp.status_code


    def _get_json(self,endpoint):
        assert (self._token is not None)
        resp = requests.get(self.game_url + endpoint, auth=(self._token, ""))
        try:
            js = resp.json()
        except:
            return "", resp.status_code
        return resp.json(), resp.status_code

    def _get_large_file_authenticated(self, endpoint, save_to):
        r = requests.get(self.game_url + endpoint, auth=(self._token, ""), stream=True)
        if r.status_code != 200:
            raise RuntimeError("Error downloading file!")
        with open(save_to, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    def get_vpn_config(self, fname):
        """
        Download and save your team's VPN configuration.

        The resulting file will be an OpenVPN configuration file, complete with certificate.
        Just run it with 'openvpn [configfile]', and you're in!
        (HINT: you might need to be root)
        :param fname: File name to save the Tar-Gzipped service bundle to
        :return: None
        """

        resp,code = self._get_json("api/vpnconfig")
        if code != 200:
            if isinstance(resp,dict) and 'message' in resp:
                raise RuntimeError(resp['message'])
            else:
                raise RuntimeError("An unknown error occurred getting the OpenVPN config!")
        with open(fname,'wb') as f:
            f.write(base64.b64decode(resp['vpnconfig']))

    def submit_service(self, name, service_bundle_fp):
        """
        Submit a service
        :param name: The service's name
        :param service_bundle_fp: Path to the Service Bundle.  See the documentation for details
        :return:
        """
        """
        args = {}
        args['name'] = name

        with open(service_bundle_fp, 'rb') as f:
            args['payload'] = base64.b64encode(f.read())

        resp, code = self._post_json("api/service", args)
        if code != 200:
            raise RuntimeError(repr(resp))
        return resp['upload_id']
        """
        raise RuntimeError("Not needed this year.  Submitting services so 2015 :) ")

    def submit_dashboard(self, name, dashboard_bundle_fp):
        """
        Submit a dashboard for the dashboard contest!
        :param name: The dashboard's name
        :param dashboard_bundle_fp: Path to the Dashboard Bundle.  See the documentation for details
        :return:
        """
        """
        args = {}
        args['name'] = name

        with open(dashboard_bundle_fp, 'rb') as f:
            args['archive'] = base64.b64encode(f.read())

        resp, code = self._post_json("api/dashboard", args)
        if code != 200:
            raise RuntimeError(repr(resp))
        print("Done.")
        """
        raise RuntimeError("Not needed this year.  The dashboard is like Highlander, there can be only one!")

    def get_service_status(self):
        """
        Get the service status and possible error message for the submitted service
        :return:
        """
        """
        resp, code = self._get_json("api/service")
        if code == 200:
            return resp['uploads']
        else:
            if isinstance(resp,dict) and 'message' in resp:
                raise RuntimeError(resp['message'])
            else:
                raise RuntimeError("An unknown error occurred getting the service status!!")

        """
        raise RuntimeError("Not needed this year.  Submitting services so 2015 :) ")

    def get_vm_bundle(self, save_to):
        """
        Download the team's VM bundle, and save it to the given file.

        :param save_to: Path to save the bundle to
        :return: None
        """
        self._get_large_file_authenticated("api/vmbundle",save_to)


    def get_test_vm_bundle(self, save_to):
        """
        Download the team's VM bundle, and save it to the given file.
        :param save_to: Path to save the bundle to
        :return: None
        """
        self._get_large_file_authenticated("api/testvmbundle",save_to)

    def get_team_list(self):
        """
        Return the list of teams!
        """
        resp, code = self._get_json("api/teams")
        if code == 200:
            return resp['teams']
        else:
            if isinstance(resp,dict):
                raise RuntimeError(resp['message'])
            else:
                raise RuntimeError("An unknown error occurred getting the team list")


    def get_tick_info(self):
        """
        Return information about the current game "tick".

        The iCTF game is divided into rounds, called "ticks".  Scoring is computed at the end of each tick.
        New flags are set only at the next tick.

        If you're writing scripts or frontends, you should use this to figure out when to
        run them.

        The format looks like:
        {u'approximate_seconds_left': <int seconds>,
        u'created_on': Timestamp, like u'2015-12-02 12:28:03',
        u'tick_id': <int tick ID>}
        """
        resp, code = self._get_json("api/status/tick")
        if code == 200:
            return resp
        else:
            if isinstance(resp,dict):
                raise RuntimeError(resp['message'])
            else:
                raise RuntimeError("An unknown error occurred getting the tick info.")

    def submit_flag(self, flags):
        """
        Submit a list of one or more flags
        :param flags: A list of flags
        :return: List containing a response for each flag, either:
        	"correct" | "ownflag" (do you think this is defcon?)
                      | "incorrect"
                      | "alreadysubmitted"
                      | "notactive",
                      | "toomanyincorrect",

        """
        if not isinstance(flags,list):
            raise TypeError("Flags should be in a list!")
        resp, code = self._post_json("api/flag", {'flags': flags})
        if code == 200:
            return resp
        else:
            if isinstance(resp,dict):
                raise RuntimeError(resp['message'])
            else:
                raise RuntimeError("An unknown error occurred submitting flags.")

    def get_targets(self, service):
        """
        Get a list of teams, their IP addresses, and the currently valid flag_ids.
        Your exploit should then try to exploit each team, and steal the flag with the given ID.

        You can/should use this to write scripts to run your exploits!

        :param service: The name or ID of a service (see get_service_list() for IDs and names)
        :return: A list of targets:
            [
                {
                    'team_name' : "Team name",
                    'ip_address' : "10.7.<team_id>.2",
                    'port' : <int port number>,
                    'flag_id' : "Flag ID to steal"
                },
                ...
            ]
        """
        service_id = None
        if isinstance(service,str):
            services = self.get_service_list()
            svc = filter(lambda x: x['service_name'] == service, services)
            if not svc:
                raise RuntimeError("Unknown service " + service)
            service_id = int(svc[0]['service_id'])
        else:
            service_id = service
        resp, code = self._get_json("api/targets/" + str(service_id))
        if code == 200:
            return resp
        else:
            if isinstance(resp,dict):
                raise RuntimeError(resp['message'])
            else:
                raise RuntimeError("Something went wrong getting targets.")

    def get_service_list(self):
        """
        Returns the list of services, and some useful information about them.

        The output will look like:

        [
            {
                'service_id' : <int service id>,
                'team_id' : <team_id which created that service>
                'service_name' : "string service_name",
                'description' : "Description of the service",
                'flag_id_description' : "Description of the 'flag_id' in this service, indicating which flag you should steal",
                'port' : <int port number>
            }
        ]
        """
        resp, code = self._get_json("api/services")
        if code == 200:
            return resp['services']
        else:
            if isinstance(resp,dict):
                raise RuntimeError(resp['message'])
            else:
                raise RuntimeError(repr(resp))

    def get_game_status(self):
        """
        Return a dictionary containing game status information.
        This will include:
            - The scores of all teams
            - Game timing information
            - Information about services, including their status, number of exploitations, etc

        This API is suitable for use in the creation of frontends.

        The return value is a large dictionary, containing the following:
        - 'teams' : Basic team info, name, country, latitude, longitude, etc
        - 'service_states': For each team and service, provides its "state" (up/down/etc)
        - 'exploited_services': For each service that has been exploited, list who exploited it
        - 'first_bloods': For each service, which team scored on it first (they get extra points!)
        - 'scores': The scoring data for each team.
        - 'tick': Info about the game's current "tick" -- see get_tick_info()
        It will look something like:

        {
            'teams' :
                {
                    <team_id> :
                        {
                            'country' : "ISO 2 letter country code",
                            'logo' : <base64 logo>,
                            'name' : "1338-offbyone"
                            'url' : "http://teamurl.here"
                        }					}
                }
            'exploited_services' :
                {
                    <service_id> :
                        {
                            'service_name' : "string_service_name",
                            'teams' :
                                [
                                    {
                                        'team_id' : <team_id>,
                                        'team_name' : "string team name"
                                    },
                                    ...
                                ],
                            'total_stolen_flags' : <integer>
                        }
                }
            'service_states' :
                {
                    <team_id> :
                        {
                            <service_id> :
                                {
                                    'service_name' : "string_service_name"
                                    'service_state' : "untested" | "up" | "down"
                                }
                    }
                },
            'first_bloods' :
                {
                    <service_id> :
                        {
                            'created_on' : Timestamp eg. '2015-12-02 10:57:49',
                            'team_id' : <ID of exploiting team>
                        }
                },
            'scores' :
                {
                    <team_id> :
                        {
                            'attack_points' : <float number of points scored through exploitation>,
                            'service_points' : <float number of points for having a "cool" service, see rules for details>,
                            'sla' : <float SLA score>
                            'total_points' : <float normalized final score>
                        }
                },
            'tick' :
                {
                    'approximate_seconds_left': <int seconds>,
                    'created_on': Timestamp, like '2015-12-02 12:28:03',
                    'tick_id': <int tick ID>
                }
        }

        """
        resp, code = self._get_json("api/status")
        if code == 200:
            return resp
        else:
            if isinstance(resp,dict) and 'message' in resp:
                raise RuntimeError(resp['message'])
            else:
                raise RuntimeError("An unknown error occurred contacting the game status! Perhaps try again?")

    def submit_service_vote(self, service_1, service_2, service_3):
        """
        Submit your team's vote for the "Best service" prize!

        :param service_1:
        :param service_2:
        :param service_3: Names of services, as listed in get_game_status() (in order, 1 = best)
        :return: None

        """
        """
        resp, code = self._post_json("api/vote", {'service_1':service_1,'service_2':service_2,'service_3':service_3})
        if code == 200:
            return
        else:
            if not resp:
                raise RuntimeError("An unknown error occurred submitting your vote")
            raise RuntimeError(resp['message'])
        """
        raise RuntimeError("Nope, not necessary this year.")

    def get_team_status(self):
        """
        Get your team's current status, including whether your
        team has been verified, metadata submitted, service submitted, etc
        :return: String
        """
        pass
