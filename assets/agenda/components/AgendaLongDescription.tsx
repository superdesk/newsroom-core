import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';


export default function AgendaLongDescription({item, plan}) {
    const description = get(plan, 'description_text') || item.definition_long || item.definition_short;

    if (!description) {
        return null;
    }

    return description[0] !== '<' ? (
        <p className="wire-column__preview__text wire-column__preview__text--pre">
            {description}
        </p>
    ) : (
        <div dangerouslySetInnerHTML={{__html: description}} />
    );
}

AgendaLongDescription.propTypes = {
    item: PropTypes.object.isRequired,
    plan: PropTypes.object,
};
