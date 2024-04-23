import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {bem} from '../utils';
import {hasCoverages} from '../../agenda/utils';
import AgendaName from '../../agenda/components/AgendaName';
import AgendaMap from '../../agenda/components/AgendaMap';
import AgendaTime from '../../agenda/components/AgendaTime';
import AgendaListItemLabels from '../../agenda/components/AgendaListItemLabels';
import TopStoryLabel from 'agenda/components/TopStoryLabel';
import ToBeConfirmedLabel from 'agenda/components/ToBeConfirmedLabel';
import {LabelGroup} from 'agenda/components/LabelGroup';

export default function Article({image, item, children, disableTextSelection, detailsConfig}: any) {  
    return (
        <article
            id='preview-article'
            className={classNames(
                'wire-column__preview__content--item-detail-wrap',
                {noselect: disableTextSelection}
            )}
        >
            <div className={bem('wire-column__preview', 'content', {covering: hasCoverages(item)})}>
                <hgroup className='mt-4'>
                    <LabelGroup>
                        <TopStoryLabel item={item} config={detailsConfig} size='big' />
                        <ToBeConfirmedLabel item={item} size='big' />
                    </LabelGroup>
                    <AgendaName item={item} noMargin />
                </hgroup>
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
    group: PropTypes.any,
    children: PropTypes.node,
    disableTextSelection: PropTypes.bool,
    detailsConfig: PropTypes.any,
};

Article.defaultProps = {disableTextSelection: false};
