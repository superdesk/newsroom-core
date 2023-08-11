import PropTypes from 'prop-types';

const user = PropTypes.string;

const item = PropTypes.shape({
    slugline: PropTypes.string,
});

const actions = PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string.isRequired,
    action: PropTypes.func,
    url: PropTypes.func,
}));

const topic = PropTypes.shape({
    _id: PropTypes.string,
    _created: PropTypes.string,
    name: PropTypes.string,
    label: PropTypes.string.isRequired,
    description: PropTypes.string,
    is_global: PropTypes.bool,
    user: PropTypes.string,
    company: PropTypes.string,
    query: PropTypes.string,
});

const topics = PropTypes.arrayOf(topic);

const previewConfig = PropTypes.shape({

});

const types: any = {
    user,
    item,
    topic,
    topics,
    actions,
    previewConfig,
};

export default types;
