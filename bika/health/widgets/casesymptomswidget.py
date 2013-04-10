from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from Products.ATExtensions.widget import RecordsWidget as ATRecordsWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFCore.utils import getToolByName
from operator import itemgetter
import json


class CaseSymptomsWidget(ATRecordsWidget):
    security = ClassSecurityInfo()
    _properties = ATRecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_health_widgets/casesymptomswidget",
        'helper_js': ("bika_health_widgets/casesymptomswidget.js",),
        'helper_css': ("bika_health_widgets/casesymptomswidget.css",),
        'gender': None,
        'allowDelete': False,
        'readonly': False,
        'combogrid_options': '',
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        outvalues = []
        values = form.get(field.getName(), empty_marker)
        for value in values:
            if 'Assigned' in value and int(value['Assigned']) == 1:
                outvalues.append({'UID': value['UID'],
                                  'Title': value.get('Title', ''),
                                  'Description': value.get('Description', ''),
                                  'Severity': value.get(value['UID'], '0'),
                                  'SeverityAllowed':value.get('SeverityAllowed', '0'),
                                  'Gender':value.get('Gender', 'dk')})
        return outvalues, {}

    def jsondumps(self, val):
        return json.dumps(val)

    def getSymptoms(self, gender=None):
        """ Returns the symptoms from the instance merged with those symptoms
            active from bika setup, with severity values assigned to default 0
        """
        outsymptoms = {}
        field = self.aq_parent.Schema()['Symptoms']
        value = field.get(self.aq_parent)
        casesymptoms = value and value or []

        casegender = 'dk'
        field = self.aq_parent.Schema()['PatientID']
        patientid = field.get(self.aq_parent)
        if patientid:
            bpc = getToolByName(self, 'bika_patient_catalog')
            patient = bpc(portal_type='Patient', id=patientid)
            gender = 'dk'
            if len(patient) > 0:
                patient = patient[0].getObject()
                gender = patient.getGender()
            casegender = gender

        symptoms = self.bika_setup_catalog(portal_type='Symptom',
                                         inactive_state='active')
        for symptom in symptoms:
            symptom = symptom.getObject()
            s_gender = symptom.getGender()
            if not gender or s_gender == 'dk' or s_gender == gender:
                outsymptoms[symptom.UID()] = {
                    'UID': symptom.UID(),
                    'Title': symptom.Title(),
                    'Description':symptom.Description(),
                    'SeverityAllowed':symptom.getSeverityAllowed() and 1 or 0,
                    'Severity':'0',
                    'Assigned':0,
                    'Gender':symptom.getGender(),
                    'Visible':symptom.getGender()=='dk' or symptom.getGender()==casegender}
        for symptom in casesymptoms:
            if 'UID' in symptom:
                if symptom['UID'] in outsymptoms \
                    and ('Severity' in symptom \
                         and symptom['Severity'] is not None \
                         and symptom['Severity'] != '0'):
                    sym = outsymptoms[symptom['UID']]
                    sym['Severity'] = symptom['Severity']
                    sym['Assigned'] = 1
                else:
                    outsymptoms[symptom['UID']] = {'UID': symptom['UID'],
                                                   'Title': symptom.get('Title',''),
                                                   'Description': symptom.get('Description',''),
                                                   'SeverityAllowed': 'SeverityAllowed' in symptom and symptom['SeverityAllowed'] or 0,
                                                   'Severity': symptom.get('Severity','0'),
                                                   'Assigned': 1,
                                                   'Gender':symptom.get('Gender', 'dk'),
                                                   'Visible':symptom.get('Gender', 'dk')=='dk' or symptom.get('Gender', 'dk')==casegender}
        items=[]
        for symptom in outsymptoms.values():
            items.append(symptom)
        items.sort(lambda x, y: cmp(x['Title'].lower(), y['Title'].lower()))
        return items

registerWidget(CaseSymptomsWidget,
               title='CaseSymptomsWidget',
               description='Experiencing symptoms and severity',
               )
