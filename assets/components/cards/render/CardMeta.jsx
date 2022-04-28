import React from 'react';
import PropTypes from 'prop-types';
import {gettext, shortDate, fullDate, isDisplayed} from 'utils';
import {characterCount, wordCount} from 'utils';
import WireListItemIcons from 'wire/components/WireListItemIcons';

function CardMeta({item, pictureAvailable, displayDivider, slugline, listConfig}) {
    return (<div className="wire-articles__item__meta">
        <WireListItemIcons item={item} picture={pictureAvailable ? {} : null} divider={displayDivider} />
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

CardMeta.propTypes = {
    item: PropTypes.object.isRequired,
    pictureAvailable: PropTypes.bool,
    displayDivider: PropTypes.bool,
    slugline: PropTypes.string,
    listConfig: PropTypes.object,
};

CardMeta.defaultProps = {
    displayDivider: false,
};

export default CardMeta;
