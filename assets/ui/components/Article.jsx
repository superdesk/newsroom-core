import React from 'react';
import PropTypes from 'prop-types';
import {bem} from '../utils';
import {hasCoverages} from '../../agenda/utils';
import AgendaName from '../../agenda/components/AgendaName';
import AgendaMap from '../../agenda/components/AgendaMap';
import AgendaTime from '../../agenda/components/AgendaTime';
import AgendaListItemLabels from '../../agenda/components/AgendaListItemLabels';

export default function Article({image, item, children}) {
    return (
        <article id='preview-article' className="wire-column__preview__content--item-detail-wrap">
            <div className={bem('wire-column__preview', 'content', {covering: hasCoverages(item)})}>
                <AgendaName item={item} />
                <AgendaTime item={item}>
                    <AgendaListItemLabels
                        item={item}
                    />
                </AgendaTime>
                <AgendaMap image={image} />
                <div className="wire-column__preview__content--item-detail-text-wrap">
                    {children}
                </div>
            </div>
        </article>
    );
}

Article.propTypes = {
    image: PropTypes.element,
    item: PropTypes.object,
    children: PropTypes.node,
};