from Products.CMFCore.utils import getToolByName
from bika.health import bikaMessageFactory as _
from bika.lims import bikaMessageFactory as _b
from bika.lims.browser import BrowserView
from bika.lims.permissions import *
import json
import plone

class ajaxGetBatchInfo(BrowserView):
    """ Grab the details for Doctor, Patient, Hospital (Titles).
    These are displayed onload next to the ID fields, but they are not part of the schema.
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)

        bpc = getToolByName(self.context, 'bika_patient_catalog')
        batch = self.context
        patientids = ''

        client = batch.Schema()['Client'].get(batch)
        doctor = batch.Schema()['Doctor'].get(batch)
        patient = batch.Schema()['Patient'].get(batch)
        if patient:
            value = patient.getPatientIdentifiersStr()
            patientids = len(value) > 0 and "("+value+")" or ''

        ret = {'Client': client and "<a class='edit_client' href='%s/base_edit'>%s</a>"%(client.absolute_url(), client.Title()) or '',
               'ClientID': client and client.getClientID() or '',
               'ClientUID': client and client.UID() or '',
               'ClientTitle': client and client.Title() or '',
               'Patient': patient and "<a class='edit_patient' href='%s/edit'>%s</a> %s"%(patient.absolute_url(), patient.Title(), patientids) or '',
               'PatientID': patient and patient.getPatientID() or '',
               'PatientUID': patient and patient.getPatientID() or '',
               'PatientTitle': patient and patient.Title() or '',
               'Doctor': doctor and "<a class='edit_doctor' href='%s/edit'>%s</a>"%(doctor.absolute_url(), doctor.Title()) or '',
               'DoctorID': doctor and doctor.getDoctorID(),
               'DoctorUID': doctor and doctor.UID() or '',
               'DoctorTitle': doctor and doctor.Title() or '',
               }

        return json.dumps(ret)

