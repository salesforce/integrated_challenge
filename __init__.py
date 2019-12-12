# Copyright (c) 2020, salesforce.com, inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
from __future__ import division  # Use floating point for math calculations
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.flags import get_flag_class
from CTFd.models import (
    db,
    Solves,
    Fails,
    Flags,
    Challenges,
    ChallengeFiles,
    Tags,
    Hints,
)
from CTFd.utils.user import get_ip
from CTFd.utils.uploads import delete_file
from CTFd.utils.modes import get_model
from flask import Blueprint
import math
from os import environ
import base64
import requests
import hmac
import hashlib
from time import time
from flask import (
    request,
    url_for,
    json
)
import uuid



class IntegratedChallengeClass(BaseChallenge):
    id = "integrated"  # Unique identifier used to register challenges
    name = "integrated"  # Name of a challenge type
    templates = {  # Templates used for each aspect of challenge editing & viewing
        "create": "/plugins/integrated_challenges/assets/create.html",
        "update": "/plugins/integrated_challenges/assets/update.html",
        "view": "/plugins/integrated_challenges/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/integrated_challenges/assets/create.js",
        "update": "/plugins/integrated_challenges/assets/update.js",
        "view": "/plugins/integrated_challenges/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/integrated_challenges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "integrated", __name__, template_folder="templates", static_folder="assets"
    )

    @staticmethod
    def create(request):
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        data = request.form or request.get_json()
        challenge = IntegratedChallenge(**data)

        db.session.add(challenge)
        db.session.commit()

        return challenge

    @staticmethod
    def read(challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = IntegratedChallenge.query.filter_by(id=challenge.id).first()
        returnTo = str.format("{0}{1}**result**#{2}",request.url_root, url_for('challenges.listing'), challenge.name).replace("//","/")
        nonces= uuid.uuid4().hex
        eventId = environ.get('EVENT_ID')
        messages = nonces+eventId+challenge.challengeName+returnTo
        sig = hmac.new(str(environ.get('CTF_KEY')).encode('utf-8'), msg=messages.encode('utf-8'),digestmod=hashlib.sha256).hexdigest()
        validatorURL=str(environ.get('VALIDATOR_URL'))
        testResult = request.args.get('testResult')
        success = False
        flag = ""
        if not testResult:
            try: 
                data = json.loads(testResult)
                if data['success']==True:
                    flag = data['flag']
            except:
                print(str.format("Error loading: {0}", testResult))
        data = {
            'id': challenge.id,
            'name': challenge.name,
            'value': challenge.value,
            'challengeName': challenge.challengeName,
            'description': challenge.description,
            'category': challenge.category,
            'state': challenge.state,
            'max_attempts': challenge.max_attempts,
            'type': challenge.type,
            'returnTo' : returnTo,
            'eventId' : eventId,
            'sig' : sig,
            'validatorURL' : validatorURL,
            'nonce' : nonces,
            'testResult' : testResult,
            'success' : success,
            'flag' : flag,
            'type_data': {
                'id': IntegratedChallengeClass.id,
                'name': IntegratedChallengeClass.name,
                'templates': IntegratedChallengeClass.templates,
                'scripts': IntegratedChallengeClass.scripts,
            }
        }
        return data

    @staticmethod
    def update(challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()
        for attr, value in data.items():
            setattr(challenge, attr, value)

        db.session.commit()
        return challenge

    @staticmethod
    def delete(challenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge:
        :return:
        """
        Fails.query.filter_by(challenge_id=challenge.id).delete()
        Solves.query.filter_by(challenge_id=challenge.id).delete()
        Flags.query.filter_by(challenge_id=challenge.id).delete()
        files = ChallengeFiles.query.filter_by(challenge_id=challenge.id).all()
        for f in files:
            delete_file(f.id)
        ChallengeFiles.query.filter_by(challenge_id=challenge.id).delete()
        Tags.query.filter_by(challenge_id=challenge.id).delete()
        Hints.query.filter_by(challenge_id=challenge.id).delete()
        IntegratedChallenge.query.filter_by(id=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()
        db.session.commit()

    @staticmethod
    def attempt(challenge, request):
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param challenge: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()
        for flag in flags:
            if get_flag_class(flag.type).compare(flag, submission):
                return True, "Correct"
        return False, "Incorrect"

    @staticmethod
    def solve(user, team, challenge, request):
        """
        This method is used to insert Solves into the database in order to mark a challenge as solved.

        :param team: The Team object from the database
        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        chal = IntegratedChallenge.query.filter_by(id=challenge.id).first()
        data = request.form or request.get_json()
        submission = data['submission'].strip()

        Model = get_model()

        solve = Solves(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(req=request),
            provided=submission
        )
        db.session.add(solve)


        db.session.commit()
        db.session.close()

    @staticmethod
    def fail(user, team, challenge, request):
        """
        This method is used to insert Fails into the database in order to mark an answer incorrect.

        :param team: The Team object from the database
        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        wrong = Fails(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(request),
            provided=submission,
        )
        db.session.add(wrong)
        db.session.commit()
        db.session.close()


def get_chal_class(class_id):
    """
    Utility function used to get the corresponding class from a class ID.

    :param class_id: String representing the class ID
    :return: Challenge class
    """
    cls = CHALLENGE_CLASSES.get(class_id)
    if cls is None:
        raise KeyError
    return cls


class IntegratedChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "integrated"}
    id = db.Column(None, db.ForeignKey("challenges.id"), primary_key=True)
    challengeName = db.Column(db.String(200))

    def __init__(self, *args, **kwargs):
        super(IntegratedChallenge, self).__init__(**kwargs)
        self.initial = kwargs["value"]


def load(app):
    # upgrade()
    app.db.create_all()
    CHALLENGE_CLASSES["integrated"] = IntegratedChallengeClass
    register_plugin_assets_directory(
        app, base_path="/plugins/integrated_challenges/assets/"
    )
