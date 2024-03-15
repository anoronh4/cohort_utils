from cohort_utils import parsers
from cohort_utils.model import Pairing
import unittest
from cohort_utils.parsers.crj import CRJ_Handler
import cohort_utils
import json,jsonschema
import pandas as pd
import tempfile
#import cohort_utils.schema.CRJ_JSON_SCHEMA as CRJ_JSON_SCHEMA

COHORT_COMPLETE_JSON  = "./data/json/cohort-complete.example.json"
COHORT_REQUEST_JSON   = "./data/json/COHORT1.cohort.json"
COHORT_REQUEST_JSON2  = "./data/json/COHORT2.cohort.json"

class TestCRJ(unittest.TestCase):
    def test_crj_obj(self):
        with open(COHORT_COMPLETE_JSON, 'r') as f:
            crj_data = json.load(f)
        mycohort = cohort_utils.model.Cohort(crj = crj_data)
        assert len(mycohort) == 3
        assert mycohort.cohort["projectSubtitle"] == "A longer description"
        assert mycohort.cohort["cohortId"] == "CCS_PPPQQQQ"

    def test_cohort_fillinids(self):
        with open(COHORT_REQUEST_JSON, 'r') as f:
            crj_data = json.load(f)
        mycohort = cohort_utils.model.Cohort(crj = crj_data)
        assert len(mycohort) == 2
        metadata_table = pd.DataFrame(
            {
                'cmoSampleName': ["s_C_AAAAAA_P001_d","s_C_BBBBBB_P001_d","s_C_AAAAAA_N001_d","s_C_BBBBBB_N001_d"],
                'primaryId': ['78787_AB_1','78787_1','95959_8','96785_G_4']
            }
        )
        newcohort = mycohort.update_ids(metadata_table)
        assert newcohort.cohort['samples'][0]['primaryId'] == '78787_AB_1'

    def test_cohort_addnormals(self):
        with open(COHORT_REQUEST_JSON2, 'r') as f:
            crj_data = json.load(f)
        mycohort = cohort_utils.model.Cohort(crj = crj_data)
        assert len(mycohort) == 2
        pairing_table = pd.DataFrame(
            {
                'TUMOR_ID':['s_C_AAAAAA_P001_d','s_C_BBBBBB_P001_d'],
                'NORMAL_ID':['s_C_AAAAAA_N001_d','s_C_BBBBBB_N001_d']
            }
        )
        with tempfile.NamedTemporaryFile(mode='w+t', suffix='.csv',delete=False) as f:
            pairing_table.to_csv(f,index=False,sep="\t")
            pairing_file = f.name
        pairing_obj = Pairing(file = pairing_file)
        newcohort = mycohort.fillin_normals(pairing_obj)
        jsonschema.validators.validate(instance=newcohort.cohort, schema=cohort_utils.schema.COHORT_REQUEST_JSON_SCHEMA)
        metadata_table = pd.DataFrame(
            {
                'cmoSampleName': ["s_C_AAAAAA_P001_d","s_C_BBBBBB_P001_d","s_C_AAAAAA_N001_d","s_C_BBBBBB_N001_d"],
                'primaryId': ['78787_AB_1','78787_1','95959_8','96785_G_4']
            }
        )
        newercohort = newcohort.update_ids(metadata_table)
        jsonschema.validators.validate(instance=newercohort.cohort, schema=cohort_utils.schema.COHORT_REQUEST_JSON_SCHEMA)
        x = newercohort.cohort_complete_generate(date="2022-11-12 21:59",status="PASS")
        # keep the following assertion to make sure cohort_complete_generate doesn't modify the original object.
        assert "holdBamsAndFastqs" in newercohort.cohort
        jsonschema.validators.validate(instance=newercohort.cohort_complete_generate(date="2022-11-12 21:59",status="PASS"), schema=cohort_utils.schema.COHORT_COMPLETE_JSON_SCHEMA)

if __name__ == "__main__":
    unittest.main()