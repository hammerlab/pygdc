from cohorts import Cohort, Patient
import json

from .api import get_cases
from .filters import and_filter, equals_filter
from .fields import CASE_DEFAULT_FIELDS, CASE_DIAGNOSIS_FIELDS, CASE_SAMPLE_FIELDS, CASE_EXPOSURE_FIELDS

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
            **[equals_filter(k, v) for (k, v) in kwargs]
        )
    )

    filter_fields = ['project.primary_site'] + kwargs.keys()

    # Automatically include the filter fields in the output
    fields = list(CASE_DEFAULT_FIELDS) + filter_fields

    if with_diagnosis: 
        fields += CASE_DIAGNOSIS_FIELDS
    if with_samples: 
        fields += CASE_SAMPLE_FIELDS
    if with_exposures: 
        fields += CASE_EXPOSURE_FIELDS

    results = get_cases(filters=filters, fields=','.join(fields))

    patients = []
    for result in results:
        submitter_id = result['submitter_id']
        diagnoses = result['diagnoses']

        assert len(diagnoses) == 1, "Patient {} had multiple diagnoses".format(submitter_id)
        diagnosis = result['diagnoses'][0]
        deceased = diagnosis['vital_status'] == 'dead'
        progressed = diagnosis['progression_or_recurrence'] == 'progression'
        patient = Patient(
                id=submitter_id,
                deceased=deceased,
                progressed=progressed,
                os=diagnosis['days_to_death'] if deceased else diagnosis['days_to_last_follow_up'],
                pfs=diagnosis['days_to_recurrence'] if progressed else diagnosis['days_to_last_follow_up'],
                benefit=False,
            )
        patients.append(patient)

    cohort = Cohort(
        patients=patients,
        cache_dir=cohort_cache_dir
    )

    return cohort