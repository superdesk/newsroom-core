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

    return (
        <div className="wire-column__preview__text wire-column__preview__text--pre">
            {description.split('\n').map((element: string, index: number) => {
                return element[0] !== '<'
                    ? (
                        <div>
                            {item.es_highlight
                                ? (
                                    <span dangerouslySetInnerHTML={{__html: element}} />
                                )
                                : element
                            }
                        </div>
                    )
                    : (
                        <div  dangerouslySetInnerHTML={{__html: element}} key={index} />
                    );
            })}
        </div>
    )
}

AgendaLongDescription.propTypes = {
    item: PropTypes.object.isRequired,
    plan: PropTypes.object,
};
