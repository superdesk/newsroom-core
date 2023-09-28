import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import {getHighlightedDescription} from '../utils';


export default function AgendaLongDescription({item, plan}: {item: any, plan: any}) {
    const description = item.es_highlight
        ? getHighlightedDescription(item, plan)
        : get(plan, 'description_text') || item.definition_long || item.definition_short;

    if (!description) {
        return null;
    }

    function isHTML(value: string) {
        const doc = new DOMParser().parseFromString(value, 'text/html');
        return Array.from(doc.body.childNodes).some(node => node.nodeType === 1);
    }

    return (
        <div className="wire-column__preview__text wire-column__preview__text--pre">
            {isHTML(description)
                ? <div style={{whiteSpace: 'pre-line'}} dangerouslySetInnerHTML={{__html: description}} />
                : description.split('\n').map((lineOfHTML: string, index: number) => {
                    return (
                        <div  dangerouslySetInnerHTML={{__html: lineOfHTML}} key={index} />
                    );
                })
            }
        </div>
    );
}

AgendaLongDescription.propTypes = {
    item: PropTypes.object.isRequired,
    plan: PropTypes.object,
};
