import React from 'react';
import {IArticle, IListConfig} from 'interfaces';

import {gettext, shortDate, fullDate, isDisplayed} from 'utils';
import {characterCount, wordCount} from 'utils';
import WireListItemIcons from 'wire/components/WireListItemIcons';

interface IProps {
    item: IArticle;
    displayDivider?: boolean;
    slugline?: string;
    listConfig?: IListConfig;
}

function CardMeta({item, displayDivider, slugline, listConfig}: IProps) {
    return (<div className="wire-articles__item__meta">
        <WireListItemIcons item={item} divider={displayDivider} />
        <div className="wire-articles__item__meta-info">
            {slugline && <span className='bold'>{slugline}</span>}
            <span>
                {item.source && item.source}
                {isDisplayed('wordcount', listConfig) &&
                <span>{'  //  '}<span>{wordCount(item)}</span> {gettext('words')}</span>}
                {isDisplayed('charcount', listConfig) &&
                <span>{'  //  '}<span>{characterCount(item)}</span> {gettext('characters')}</span>}
                {item.versioncreated && ' // '}
                {item.versioncreated &&
                    <time dateTime={fullDate(item.versioncreated)}>{shortDate(item.versioncreated)}</time>
                }
            </span>
        </div>
    </div>);
}

export default CardMeta;
