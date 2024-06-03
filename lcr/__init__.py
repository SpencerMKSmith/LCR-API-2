#!/usr/bin/env python3

import re
import json
import logging
import requests
import time



_LOGGER = logging.getLogger(__name__)
HOST = "churchofjesuschrist.org"
BETA_HOST = f"beta.{HOST}"
LCR_DOMAIN = f"lcr.{HOST}"
FFE_DOMAIN = f"lcrffe.{HOST}"

if _LOGGER.getEffectiveLevel() <= logging.DEBUG:
    import http.client as http_client
    http_client.HTTPConnection.debuglevel = 1


class InvalidCredentialsError(Exception):
    pass


class API():
    def __init__(
            self, username, password, unit_number, beta=False,
            driver=None, cookies=None):
        self.unit_number = unit_number
        self.session = requests.Session()
        self.driver = driver
        self.beta = beta
        self.host = BETA_HOST if beta else HOST

        if cookies is None:
            from .selenium_login import login
            login(self, username, password)
        else:
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])

    def _make_request(self, request):
        if self.beta:
            request['cookies'] = {'clerk-resources-beta-terms': '4.1',
                                  'clerk-resources-beta-eula': '4.2'}

        response = self.session.get(**request)
        response.raise_for_status()  # break on any non 200 status
        return response

    def birthday_list(self, month, months=1):
        _LOGGER.info("Getting birthday list")
        request = {
            'url': 'https://{}/api/report/birthday-list'.format(
                LCR_DOMAIN
            ),
            'params': {
                'lang': 'eng',
                'month': month,
                'months': months
            }
        }

        result = self._make_request(request)
        return result.json()

    def members_moved_in(self, months):
        _LOGGER.info("Getting members moved in")
        request = {
            'url': 'https://{}/api/report/members-moved-in/unit/{}/{}'.format(
                LCR_DOMAIN,
                self.unit_number,
                months
            ),
            'params': {'lang': 'eng'}
        }

        result = self._make_request(request)
        return result.json()


    def members_moved_out(self, months):
        _LOGGER.info("Getting members moved out")
        request = {
            'url': 'https://{}/api/report/members-moved-out/unit/{}/{}'.format(
                LCR_DOMAIN,
                self.unit_number,
                    months
            ),
            'params': {'lang': 'eng'}
        }

        result = self._make_request(request)
        return result.json()


    def member_list(self):
        _LOGGER.info("Getting member list")
        request = {
            'url': 'https://{}/api/umlu/report/member-list'.format(LCR_DOMAIN),
            'params': {
                'lang': 'eng',
                'unitNumber': self.unit_number
            }
        }

        result = self._make_request(request)
        return result.json()
    

    def member_profile(self, member_id):
        _LOGGER.info("Getting member profile")
        request = {
            'url': 'https://{}/api/records/member-profile/service/{}'.format(LCR_DOMAIN, member_id),
            'params': {'lang': 'eng'}
        }

        result = self._make_request(request)
        return result.json()


    def individual_photo(self, member_id):
        """
        member_id is not the same as Mrn
        """
        _LOGGER.info("Getting photo for {}".format(member_id))
        request = {
            'url': 'https://{}/api/avatar/{}/MEDIUM'.format(LCR_DOMAIN, member_id),
            'params': {
                'lang': 'eng',
                'status': 'APPROVED'
            }
        }

        result = self._make_request(request)
        scdn_url = result.json()['tokenUrl']
        return self._make_request({'url': scdn_url}).content


    def callings(self):
        _LOGGER.info("Getting callings for all organizations")
        request = {
            'url': 'https://{}/api/orgs/sub-orgs-with-callings'.format(LCR_DOMAIN),
            'params': {'lang': 'eng'}
        }

        result = self._make_request(request)
        return result.json()


    def members_with_callings_list(self):
        _LOGGER.info("Getting callings for all organizations")
        request = {
            'url': 'https://{}/api/report/members-with-callings'.format(LCR_DOMAIN),
            'params': {'lang': 'eng'}
        }

        result = self._make_request(request)
        return result.json()


    def ministering(self):
        """
        API parameters known to be accepted are lang type unitNumber and quarter.
        """
        _LOGGER.info("Getting ministering data")
        request = {
            'url': 'https://{}/api/umlu/v1/ministering/data-full'.format(LCR_DOMAIN),
            'params': {
                'lang': 'eng',
                'unitNumber': self.unit_number,
                'type': 'ALL'
            }
        }

        result = self._make_request(request)
        return result.json()


    def access_table(self):
        """
        Once the users role id is known this table could be checked to selectively enable or disable methods for API endpoints.
        """
        _LOGGER.info("Getting info for data access")
        request = {
            'url': 'https://{}/api/access-table'.format(LCR_DOMAIN),
            'params': {'lang': 'eng'}
        }

        result = self._make_request(request)
        return result.json()


    def recommend_status(self):
        """
        Obtain member information on recommend status
        """
        _LOGGER.info("Getting recommend status")
        request = {
            'url': 'https://{}/api/recommend/recommend-status'.format(LCR_DOMAIN),
            'params': {
                'lang': 'eng',
                'unitNumber': self.unit_number
            }
        }
        result = self._make_request(request)
        return result.json()
    

    def unit_details(self, unit_number):
        _LOGGER.info("Getting unit details")
        request = {
            'url': 'https://{}/api/cdol/details/unit/{}'.format(LCR_DOMAIN, unit_number),
            'params': {'lang': 'eng'}
        }
        result = self._make_request(request)
        return result.json()
    

    def accessible_units(self):
        _LOGGER.info("Getting accessible units")
        request = {
            'url': 'https://{}/api/accessible-units'.format(FFE_DOMAIN),
        }
        result = self._make_request(request)
        return result.json()
    
    
    def financial_statement(self, internal_account_id, from_date, to_date):
        graphql_body = {"operationName":"internalTransactionDetailLinesByPostedDate","variables":{"criteria":{"internalAccountIds":[internal_account_id],"postedDateFrom":from_date,"postedDateTo":to_date,"adjustmentCodes":["ACTIVE"],"donationBatchCodes":["ACTIVE"]}},"query":"query internalTransactionDetailLinesByPostedDate($criteria: IntTransDetailLineCriteria!) {\n  internalTransactionDetailLinesByPostedDate(criteria: $criteria) {\n    id\n    postedDate\n    donationSlipLine {\n      id\n      slip {\n        id\n        amount\n        donor {\n          id\n          membershipId\n          names {\n            localUnitDisplayName\n            __typename\n          }\n          birthDate\n          __typename\n        }\n        donation {\n          id\n          date\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    internalAccount {\n      id\n      bus {\n        id\n        currency {\n          id\n          isoCode\n          __typename\n        }\n        __typename\n      }\n      org {\n        id\n        __typename\n      }\n      financialTransactionMethods {\n        id\n        financialTransactionMethod {\n          id\n          financialTransactionType\n          financialTransactionTypeId\n          transactionMethodDescriptionId\n          financialTransactionMethodFinancialInstruments {\n            id\n            financialInstrument {\n              id\n              type\n              typeId\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    category {\n      id\n      sortOrder\n      __typename\n    }\n    subcategory {\n      id\n      sortOrder\n      name\n      category {\n        id\n        sortOrder\n        name\n        __typename\n      }\n      __typename\n    }\n    unitSubcategory {\n      id\n      name\n      __typename\n    }\n    amount\n    donationBatch {\n      id\n      date\n      status\n      source\n      submittedBy\n      submittedDate\n      approvedRejectedBy\n      approvedRejectedDate\n      __typename\n    }\n    __typename\n  }\n}\n"}

        _LOGGER.info("Getting financial statement")
        request = {
            'url': 'https://{}/api/graphql'.format(FFE_DOMAIN),
            'json': graphql_body
        }
        result = self._make_request(request)
        return result.json()
    

    def financial_participant_list(self, orgId):
        graphql_body = {"operationName":"orgParticipantsList","variables":{"criteria":{"orgId":orgId,"includeChildUnitParticipants":False,"includeInactive":True}},"query":"query orgParticipantsList($criteria: OrgParticipantListCriteria!) {\n  orgParticipantsList(criteria: $criteria) {\n    id\n    maxDonationDate\n    maxPaymentDate\n    maxRecipientDate\n    participant {\n      id\n      birthDate\n      gender\n      membershipId\n      isMember\n      isDonor\n      isPayee\n      isRecipient\n      taxId\n      address {\n        composed\n        __typename\n      }\n      emailAddress\n      names {\n        localUnitDisplayName\n        __typename\n      }\n      org {\n        id\n        name\n        localName1\n        parent {\n          id\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}

        _LOGGER.info("Getting financial participant list")
        request = {
            'url': 'https://{}/api/graphql'.format(FFE_DOMAIN),
            'json': graphql_body
        }
        result = self._make_request(request)
        return result.json()


class MemberData():
    def __init__(self, legacyMemberId, fullName, sex, birthdate, callings, recommendStatus):
        self.legacyMemberId = legacyMemberId
        self.fullName = fullName
        self.sex = sex
        self.birthdate = birthdate
        self.callings = callings
        self.recommendStatus = recommendStatus

    def __iter__(self):
        return iter([self.legacyMemberId, self.fullName, self.sex, self.birthdate, self.callings, self.recommendStatus])
