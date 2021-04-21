""" CIVO REST API Stub
"""
from json import load
import os
from flask import Flask, abort, jsonify, request, render_template

app = Flask(__name__)
base_path = os.path.dirname(__file__)


def load_json(path):
    """ Load json from the file: `path`
    """
    try:
        with open(path) as f_obj:
            return load(f_obj)
    except IOError:
        return None


def load_response_json(method, resource):
    """ Load the HTTP Response given a http method and resource

    :param method: HTTP Method
    :param resource: API Resource
    :return:
    """
    path = os.path.join(base_path, 'responses', f"{method}_{resource}.json")
    resp = load_json(path)
    if resp:
        return resp
    return abort(404)


@app.errorhandler(404)
def resource_not_found(err):
    """ Handle missing resources as JSON"""
    return jsonify({'error': err.name, 'detail': err.description}), 404


def responses():
    """ List HTTP Resources
    """
    data = [(item.split('.')[0].split('_'), item)
            for item
            in os.listdir(os.path.join(base_path, 'responses'))
            if '.' in item and '_' in item
            ]
    return [(item[0][0].upper(),
             item[0][1],
             f'{request.base_url}{item[0][1]}',
             item[1])
            for item in data]


@app.route('/')
def index():
    return render_template('index.html',
                           data=responses(),
                           title="CIVO API Stub")


@app.route('/v2')
def list_responses():
    """ Convert: create_clusters.json -> (create, clusters)
    """
    return jsonify(responses())


@app.route('/responses/<string:filename>')
def show_response(filename):
    return jsonify(load_json(os.path.join(base_path, 'responses', filename)))


@app.route('/v2/instances')
def list_instances():
    return jsonify(load_response_json('get', 'instances'))


@app.route('/v2/kubernetes/applications')
def list_k8s_apps():
    return jsonify(load_response_json('get', 'apps'))


@app.route('/v2/kubernetes/clusters')
def list_k8s():
    return jsonify(load_response_json('get', 'clusters'))


@app.route('/v2/kubernetes/clusters/<uuid:cluster>')
def get_k8s(cluster):
    _ = cluster
    return jsonify(load_response_json('get', 'clusters'))


@app.route('/v2/kubernetes/clusters', methods=['POST'])
def create_k8s():
    cluster = {}
    requires_data = ["name",
                     "num_target_nodes",
                     "target_nodes_size",
                     "network_id",
                     "kubernetes_version",
                     "tags",
                     "applications",
                     "node_destroy"
                     ]

    for item in requires_data:
        value = request.args.get(item, None)
        if value is not None:
            cluster[item] = value
        else:
            abort(400, "Missing data item: %s" % item)

    return jsonify(load_response_json('create', 'clusters'))


@app.route('/v2/kubernetes/clusters', methods=['PUT'])
def update_k8s():
    return jsonify(load_response_json('create', 'clusters'))


@app.route('/v2/kubernetes/clusters', methods=['DELETE'])
def delete_k8s():
    return jsonify(load_response_json('delete', 'clusters'))


@app.route('/v2/networks')
def get_networks():
    return jsonify(load_response_json('get', 'networks'))


@app.route('/v2/regions')
def get_regions():
    return jsonify(load_response_json('get', 'regions'))


@app.route('/v2/versions')
def get_versions():
    return jsonify(load_response_json('get', 'versions'))


if __name__ == '__main__':
    app.run()
