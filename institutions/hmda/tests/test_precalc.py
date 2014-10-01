from django.test import TestCase
from mock import Mock

from geo.models import Geo
from hmda.models import HMDARecord, LendingStats
from respondants.models import Institution


class PrecalcTest(TestCase):
    fixtures = ['agency', 'fake_respondents']

    def setUp(self):
        self.respondent = Institution.objects.get(pk=1234567)
        tract_params = {
            'geo_type': Geo.TRACT_TYPE, 'minlat': 0.11, 'minlon': 0.22,
            'maxlat': 1.33, 'maxlon': 1.44, 'centlat': 45.4545,
            'centlon': 67.67, 'geom': "MULTIPOLYGON (((0 0, 0 1, 1 1, 0 0)))"}
        self.city_tract1 = Geo.objects.create(
            name='City Tract 1', cbsa='99999', geoid='11111111',
            **tract_params)
        self.city_tract2 = Geo.objects.create(
            name='City Tract 2', cbsa='99999', geoid='11111112',
            **tract_params)
        self.city_tract3 = Geo.objects.create(
            name='City Tract 3', cbsa='99999', geoid='11111113',
            **tract_params)
        # also create a tract with no loans
        self.city_tract4 = Geo.objects.create(
            name='City Tract 4', cbsa='99999', geoid='11111114',
            **tract_params)

        self.non_city_tract1 = Geo.objects.create(
            name='Non-City Tract 5', geoid='11111115', **tract_params)
        self.non_city_tract2 = Geo.objects.create(
            name='Non-City Tract 6', geoid='11111116', **tract_params)
        del tract_params['geo_type']
        self.metro = Geo.objects.create(
            name='City', geoid='99999', geo_type=Geo.METRO_TYPE,
            **tract_params)
        hmda_params = {
            'as_of_year': 2010, 'respondent_id': self.respondent.ffiec_id,
            'agency_code': str(self.respondent.agency_id),
            'loan_amount_000s': 100, 'action_taken': 1, 'statefp': '11',
            'countyfp': '111'}
        self.hmdas = []
        self.hmdas.append(HMDARecord.objects.create(
            geoid=self.city_tract1, **hmda_params))
        for i in range(3):
            self.hmdas.append(HMDARecord.objects.create(
                geoid=self.city_tract2, **hmda_params))
        for i in range(8):
            self.hmdas.append(HMDARecord.objects.create(
                geoid=self.city_tract3, **hmda_params))
        for i in range(7):
            self.hmdas.append(HMDARecord.objects.create(
                geoid=self.non_city_tract1, **hmda_params))
        for i in range(11):
            self.hmdas.append(HMDARecord.objects.create(
                geoid=self.non_city_tract2, **hmda_params))

        hmda_params['respondent_id'] = 'other'
        # these should not affect the results, since they are another lender
        for i in range(3):
            self.hmdas.append(HMDARecord.objects.create(
                geoid=self.city_tract2, **hmda_params))

    def tearDown(self):
        for hmda in self.hmdas:
            hmda.delete()
        self.city_tract1.delete()
        self.city_tract2.delete()
        self.city_tract3.delete()
        self.city_tract4.delete()
        self.non_city_tract1.delete()
        self.non_city_tract2.delete()
        self.metro.delete()