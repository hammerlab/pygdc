from cohorts import Cohort, Patient
import logging
import json


from .api import get_cases
from .filters import and_filter, equals_filter
from .fields import CASES_DEFAULT_FIELDS, CASES_DIAGNOSES_FIELDS, CASES_SAMPLE_FIELDS, CASES_EXPOSURE_FIELDS

def build_cohort(primary_site,
                 cohort_cache_dir,
                 disease_type=None,
                 only_tcga=True,
                 with_diagnosis=True,
                 with_samples=False,
                 with_exposures=False,
                 additional_fields=[],
                 **kwargs):

    filters = json.dumps(
        and_filter(
            equals_filter('project.primary_site', primary_site),
            equals_filter('project.diesase_type', disease_type) if disease_type else None,
            equals_filter('project.program.name', 'TCGA') if only_tcga else None,
            *[equals_filter(k, v) for (k, v) in kwargs.items()]
        )
    )

    filter_fields = ['project.primary_site'] + list(kwargs.keys())

    # Automatically include the filter fields in the output
    fields = list(CASES_DEFAULT_FIELDS) + filter_fields

    if with_diagnosis: 
        fields += CASES_DIAGNOSES_FIELDS
    if with_samples: 
        fields += CASES_SAMPLE_FIELDS
    if with_exposures: 
        fields += CASES_EXPOSURE_FIELDS

    results = get_cases(filters=filters, fields=','.join(fields))

    patients = []
    for result in results:
        submitter_id = result['submitter_id']
   
        if 'diagnoses' in result:
            diagnoses = result['diagnoses']

            assert len(diagnoses) == 1, "Patient {} had multiple diagnoses".format(submitter_id)
            
            diagnosis = diagnoses[0]
            deceased = diagnosis['vital_status'] == 'dead'
            progressed = diagnosis['progression_or_recurrence'] == 'progression'
            censor_time = diagnosis['days_to_last_follow_up']
            censor_time = censor_time or 0

            os = (diagnosis['days_to_death'] if deceased else censor_time) or 0 # TODO: support NA
            pfs = (diagnosis['days_to_recurrence'] if progressed else censor_time) or 0 # TODO: support NA

            patient = Patient(
                    id=submitter_id,
                    deceased=deceased,
                    progressed=progressed,
                    os=os,
                    pfs=max(pfs, os),
                    benefit=False,
                    additional_data=result,
                )
            patients.append(patient)
        else:
            logging.warn("No diagnoses found for {}".format(submitter_id))

    cohort = Cohort(
        patients=patients,
        cache_dir=cohort_cache_dir
    )

    return cohort