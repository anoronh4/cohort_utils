import unittest
import pandas as pd
import json
import cohort_utils

MAF  = "./data/mut_somatic.maf"
MAF2 = "./data/mut_somatic_2samples.maf"
COHORT_REQUEST_JSON = "./data/json/COHORT1.cohort.json"

class TestSendMessage(unittest.TestCase):
    def test_send_bam_update(self):
        inputs = {"id":"12346_A_1","status":"PASS","date":"2022-10-30 16:05"}
        cohort_utils.generate_updates.bam_complete_event(**inputs)
    
    def test_send_maf_update(self):
        inputs = {"id":"12346_A_1","normalId":"12346_A_3","status":"PASS","date":"2022-10-30 16:05"}
        cohort_utils.generate_updates.maf_complete_event(**inputs)

    def test_send_qc_update(self):
        inputs = {
            "id":"12346_A_1",
            "status":"PASS",
            "result":"pass",
            "reason":"Tumor Contamination",
            "date":"2022-10-30 16:05"
        }
        cohort_utils.generate_updates.qc_complete_event(**inputs)

    def test_send_cohort_update(self):
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
        cohort_complete_json = newcohort.cohort_complete_generate(status="PASS",date="2022-10-30 16:05")
        cohort_utils.generate_updates.cohort_complete_event(cohort_complete_json)

    def test_send_bam_update_invalid(self):
        """
        invalid timestamp
        """
        inputs = {"id":"12346_A_1","status":"PASS","date":"2022-10-3000 16:05"}
        self.assertRaises(Exception, cohort_utils.generate_updates.bam_complete_event,**inputs)

    def test_send_cbio_maf_update(self):
        cohort_utils.generate_updates.cbio_multisample_event(MAF)
    
    def test_send_cbio_mixed_maf_update(self):
        cohort_utils.generate_updates.cbio_multisample_event(MAF2)




if __name__ == "__main__":
    unittest.main()