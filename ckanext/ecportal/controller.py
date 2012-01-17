from ckan.lib.base import c, model
from ckan.authz import Authorizer
from ckan.lib.navl.validators import (ignore_missing,
                                      not_empty,
                                      empty,
                                      ignore,
                                      keep_extras,
                                     )
import ckan.logic.validators as val
from ckan.logic.converters import convert_from_extras, convert_to_extras
import ckan.logic.schema as default_schema
from ckan.controllers.package import PackageController
from field_values import type_of_dataset, publishers, geographical_granularity,\
    update_frequency, temporal_granularity 
from validators import use_other, extract_other, ecportal_date_to_db

import logging
log = logging.getLogger(__name__)


class ECPortalController(PackageController):
    package_form = 'package_ecportal.html'

    def _setup_template_variables(self, context, data_dict=None):
        c.licences = [('', '')] + model.Package.get_license_options()
        c.type_of_dataset = type_of_dataset
        c.publishers = publishers
        c.update_frequency = update_frequency
        c.temporal_granularity = temporal_granularity 
        c.geographical_granularity = geographical_granularity
        c.is_sysadmin = Authorizer().is_sysadmin(c.user)
        c.resource_columns = model.Resource.get_columns()

        # This is messy as auths take domain object not data_dict
        pkg = context.get('package') or c.pkg
        if pkg:
            c.auth_for_change_state = Authorizer().am_authorized(
                c, model.Action.CHANGE_STATE, pkg)

    def _form_to_db_schema(self):
        schema = {
            'title': [not_empty, unicode],
            'name': [not_empty, unicode, val.name_validator, val.package_name_validator],
            'notes': [not_empty, unicode],
            'url': [unicode],
            'author': [ignore_missing, unicode],
            'author_email': [ignore_missing, unicode],
            'license_id': [ignore_missing, unicode],

            'type_of_dataset': [ignore_missing, unicode, convert_to_extras],
            'responsible_department': [ignore_missing, unicode, convert_to_extras],
            'published_by': [ignore_missing, unicode, convert_to_extras],
            'release_date': [ignore_missing, ecportal_date_to_db, convert_to_extras],
            'modified_date': [ignore_missing, ecportal_date_to_db, convert_to_extras],
            'update_frequency': [use_other, unicode, convert_to_extras],
            'update_frequency-other': [],
            'temporal_coverage_from': [ignore_missing, ecportal_date_to_db, convert_to_extras],
            'temporal_coverage_to': [ignore_missing, ecportal_date_to_db, convert_to_extras],
            'temporal_granularity': [use_other, unicode, convert_to_extras],
            'temporal_granularity-other': [],
            'geographical_coverage': [ignore_missing, unicode, convert_to_extras],
            'geographical_granularity': [use_other, unicode, convert_to_extras],
            'geographical_granularity_other': [],
            'nr_of_values': [ignore_missing, unicode, convert_to_extras],
            'unit_used': [ignore_missing, unicode, convert_to_extras],
            'eurovoc_theme': [ignore_missing, unicode, convert_to_extras],
            'eurovoc_tag': [ignore_missing, unicode, convert_to_extras],

            'code': [ignore_missing, unicode, convert_to_extras],
            'type': [ignore_missing, unicode, convert_to_extras],
            'theme': [ignore_missing, unicode, convert_to_extras],
            'license_link': [ignore_missing, unicode, convert_to_extras],
            'support': [ignore_missing, unicode, convert_to_extras],

            'data_quality': [ignore_missing, unicode, convert_to_extras],

            'resources': default_schema.default_resource_schema(),
            'tag_string': [ignore_missing, val.tag_string_convert],
            'state': [val.ignore_not_admin, ignore_missing],
            'log_message': [unicode, val.no_http],
            '__extras': [ignore],
            '__junk': [empty],
        }
        return schema
    
    def _db_to_form_schema(data):
        schema = {
            'type_of_dataset': [convert_from_extras, ignore_missing],
            'responsible_department': [convert_from_extras, ignore_missing],
            'published_by': [convert_from_extras, ignore_missing],
            'release_date': [convert_from_extras, ignore_missing],
            'modified_date': [convert_from_extras, ignore_missing],
            'update_frequency': [convert_from_extras, ignore_missing, extract_other(update_frequency)],
            'temporal_coverage_from': [convert_from_extras, ignore_missing],
            'temporal_coverage_to': [convert_from_extras, ignore_missing],
            'temporal_granularity': [convert_from_extras, ignore_missing, extract_other(temporal_granularity)],
            'geographical_coverage': [convert_from_extras, ignore_missing],
            'geographical_granularity': [convert_from_extras, ignore_missing, extract_other(geographical_granularity)],
            'nr_of_values': [convert_from_extras, ignore_missing],
            'unit_used': [convert_from_extras, ignore_missing],
            'eurovoc_theme': [convert_from_extras, ignore_missing],
            'eurovoc_tag': [convert_from_extras, ignore_missing],

            'code': [convert_from_extras, ignore_missing],
            'type': [convert_from_extras, ignore_missing],
            'theme': [convert_from_extras, ignore_missing],
            'license_link': [convert_from_extras, ignore_missing],
            'support': [convert_from_extras, ignore_missing],

            'data_quality': [convert_from_extras, ignore_missing],

            'resources': default_schema.default_resource_schema(),
            'extras': {
                'key': [],
                'value': [],
                '__extras': [keep_extras]
            },
            'tags': {
                '__extras': [keep_extras]
            },
            '__extras': [keep_extras],
            '__junk': [ignore],
        }
        return schema

    def _check_data_dict(self, data_dict):
        return

