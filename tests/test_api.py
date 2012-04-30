from ckan import model
from ckan import plugins
from ckan.tests import WsgiAppCase
from create_test_data import CreateTestData
import ckan.lib.helpers as h

try:
    import json
except ImportError:
    import simplejson as json


class TestAPI(WsgiAppCase):
    @classmethod
    def setup_class(cls):
        CreateTestData.create("publisher")

        model.repo.new_revision()

        usr = model.User(name="ectest", apikey="ectest", password=u'ectest')
        model.Session.add(usr)
        model.Session.commit()

        g = model.Group.get('david')
        g.type = 'organization'
        model.Session.add(g)

        p = model.Package.get('warandpeace')
        mu = model.Member(table_id=usr.id, table_name='user', group=g)
        mp = model.Member(table_id=p.id, table_name='package', group=g)
        model.Session.add(mu)
        model.Session.add(mp)
        model.Session.commit()

        plugins.load('ecportal')

    @classmethod
    def teardown_class(cls):
        model.repo.rebuild_db()
        plugins.unload('ecportal')

    def test_package_rdf_create_ns_update(self):
        rdf = ('<rdf:RDF '
               'xmlns:foaf="http://xmlns.com/foaf/0.1/" '
               'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
               'xmlns:dct="http://purl.org/dc/terms/" '
               'xmlns:dcat="http://www.w3.org/ns/dcat#"> '
               '<dcat:Dataset rdf:about="http://localhost"></dcat:Dataset> '
               '</rdf:RDF>')
        dataset_json = json.dumps({
            'name': u'rdfpackage2',
            'title': u'RDF Package2',
            'description': u'RDF package 2 description',
            'published_by': u'david',
            'status': u'http://purl.org/adms/status/Completed',
            'contact_name': u'Eurostat',
            'rdf': json.dumps(rdf)
        })
        response = self.app.post('/api/action/package_create',
                                 params=dataset_json,
                                 extra_environ={'Authorization': 'ectest'})
        dataset = json.loads(response.body)['result']
        assert 'owl=' in dataset['rdf']

        # Fetch RDF page
        response = self.app.get(h.url_for(
            controller='package', action='read', id='rdfpackage2'
        ) + ".rdf")
        assert '/dataset/rdfpackage2' in response.body, response.body

    def test_package_rdf_create_ns_new(self):
        rdf = ('<rdf:RDF '
               'xmlns:foaf="http://xmlns.com/foaf/0.1/" '
               'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
               'xmlns:dcat="http://www.w3.org/ns/dcat#"> '
               '<dcat:Dataset rdf:about="http://localhost"></dcat:Dataset> '
               '</rdf:RDF>')
        dataset_json = json.dumps({
            'name': u'rdfpackage1',
            'title': u'RDF Package1',
            'description': u'RDF package 2 description',
            'published_by': u'david',
            'status': u'http://purl.org/adms/status/Completed',
            'contact_name': u'Eurostat',
            'rdf': json.dumps(rdf)
        })
        response = self.app.post('/api/action/package_create',
                                 params=dataset_json,
                                 extra_environ={'Authorization': 'ectest'})
        dataset = json.loads(response.body)['result']
        assert 'owl=' in dataset['rdf'], dataset['rdf']

        # Fetch RDF page
        response = self.app.get(h.url_for(
            controller='package', action='read', id='rdfpackage1'
        ) + ".rdf")
        assert '/dataset/rdfpackage1' in response.body, response.body

    def test_keywords_create(self):
        tag = u'test-keyword'
        dataset_json = json.dumps({
            'name': u'test_keywords_dataset',
            'title': u'Test Keywords Dataset',
            'description': u'test description',
            'published_by': u'david',
            'status': u'http://purl.org/adms/status/Completed',
            'contact_name': json.dumps(u'Eurostat'),
            'keywords': [{u'name': tag}]
        })
        response = self.app.post('/api/action/package_create',
                                 params=dataset_json,
                                 extra_environ={'Authorization': 'ectest'})
        dataset = json.loads(response.body)['result']

        tags = [t['name'] for t in dataset['keywords']]
        assert len(tags) == 1
        assert tag in tags

    def test_keywords_update(self):
        params = json.dumps({'id': u'warandpeace'})
        response = self.app.post('/api/action/package_show', params=params)
        dataset = json.loads(response.body)['result']
        old_tags = dataset.pop('keywords')
        new_tag_names = [u'test-keyword1', u'test-keyword2']
        new_tags = old_tags + [{'name': name} for name in new_tag_names]
        dataset['keywords'] = new_tags
        dataset['description'] = u'test description'
        dataset['status'] = u'http://purl.org/adms/status/Completed'
        dataset['contact_name'] = u'Eurostat'

        params = json.dumps(dataset)
        response = self.app.post('/api/action/package_update', params=params,
                                 extra_environ={'Authorization': 'ectest'})
        updated_dataset = json.loads(response.body)['result']

        old_tags = [tag['name'] for tag in old_tags]
        updated_tags = [tag['name'] for tag in updated_dataset['keywords']]

        for tag in old_tags:
            assert tag in updated_tags
        for tag in new_tag_names:
            assert tag in updated_tags

    def test_convert_publisher_to_groups(self):
        params = json.dumps({'id': u'warandpeace'})
        response = self.app.post('/api/action/package_show', params=params)
        dataset = json.loads(response.body)['result']
        assert dataset['published_by'] == u'david'

        dataset['description'] = u'test description'
        dataset['status'] = u'http://purl.org/adms/status/Completed'
        dataset['contact_name'] = u'Eurostat'
        dataset['published_by'] = u'roger'
        params = json.dumps(dataset)
        response = self.app.post('/api/action/package_update', params=params,
                                 extra_environ={'Authorization': 'ectest'})
        updated_dataset = json.loads(response.body)['result']
        assert updated_dataset['published_by'] == u'david', updated_dataset
