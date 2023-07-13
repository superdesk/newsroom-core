import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import {getHighlightedDescription} from '../utils';


export default function AgendaLongDescription({item, plan}) {
    const description = item.es_highlight ? getHighlightedDescription(item, plan) : get(
        plan, 'description_text') || item.definition_long || item.definition_short;

    if (!description) {
        return null;
    }

    return description[0] !== '<' ? (
        <p className="wire-column__preview__text wire-column__preview__text--pre">
            {item.es_highlight ? (
                <span dangerouslySetInnerHTML={{__html: description}} /> ) : description}
        </p>
    ) : (
        <div dangerouslySetInnerHTML={{__html: description}} />
    );
}

AgendaLongDescription.propTypes = {
    item: PropTypes.object.isRequired,
    plan: PropTypes.object,
};
