from elasticsearch import exceptions as es_exceptions
from eve_elastic import get_es
from superdesk.commands.flush_elastic_index import FlushElasticIndex

from .manager import manager, app


@manager.command
def elastic_rebuild():
    """
    It removes elastic index, creates a new one(s) and index it from mongo.

    Example:
    ::

        $ python manage.py elastic_rebuild

    """
    delete_elastic(app.config["ELASTICSEARCH_INDEX"])
    delete_elastic(app.config["CONTENTAPI_ELASTICSEARCH_INDEX"])
    FlushElasticIndex().run(sd_index=True, capi_index=True)


def delete_elastic(index_prefix: str):
    """Delete all elastic indices for the given prefix

    Copied from superdesk.commands.flush_elastic_index:_delete_elastic (from v2.6)
    So we can have it here without relying on superdesk/develop branch
    """

    es = get_es(app.config["ELASTICSEARCH_URL"])
    indices = list(es.indices.get_alias("{}_*".format(index_prefix)).keys())
    print(f"Configured indices with prefix '{index_prefix}': " + ", ".join(indices))

    for es_resource in app.data.get_elastic_resources():
        alias = app.data.elastic._resource_index(es_resource)
        print(f"- Attempting to delete alias {alias}")
        for index in indices:
            if index.rsplit("_", 1)[0] == alias or index == alias:
                try:
                    print('- Removing elastic index "{}"'.format(index))
                    es.indices.delete(index=index)
                except es_exceptions.NotFoundError:
                    print('\t- "{}" elastic index was not found. Continue without deleting.'.format(index))
                except es_exceptions.TransportError as e:
                    raise SystemExit('\t- "{}" elastic index was not deleted. Exception: "{}"'.format(index, e.error))
                else:
                    print('\t- "{}" elastic index was deleted.'.format(index))
                    break
