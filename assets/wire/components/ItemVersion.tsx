import React from 'react';
import PropTypes from 'prop-types';
import {MatchLabel} from './fields/MatchLabel';

import {formatTime, formatDate, wordCount, characterCount, gettext, isDisplayed, getSlugline} from 'utils';

export default function ItemVersion({version, baseClass, showDivider, onClick, displayConfig, matchedIds}: any) {
    return (
        <div className={`${baseClass}__versions__item`} onClick={(event: any) => onClick(version, event)}>
            <div className={`${baseClass}__versions__wrap`}>
                {!matchedIds.includes(version._id) ? null : (
                    <MatchLabel />
                )}
                <div className={`${baseClass}__versions__time`}>
                    <span>{formatTime(version.versioncreated)}</span>
                </div>
                <div className={`${baseClass}__versions__meta`}>
                    <div className={`${baseClass}__item__meta-info`}>
                        <span className="bold">{getSlugline(version, true)}</span>
                        <span>{formatDate(version.versioncreated)}
                            {isDisplayed('wordcount', displayConfig) && [
                                ' // ',
                                <span key='words-count'>{wordCount(version)} </span>,
                                gettext('words')
                            ]}
                            {isDisplayed('charcount', displayConfig) && [
                                ' // ',
                                <span key='char-count'>{characterCount(version)} </span>,
                                gettext('characters')
                            ]}
                        </span>
                    </div>
                </div>
            </div>
            {showDivider && <span className={`${baseClass}__item__divider`}></span> }
            <div className={`${baseClass}__versions__name`}>
                <h5 className={`${baseClass}__versions__headline`}>{version.headline}</h5>
            </div>
        </div>
    );
}

ItemVersion.propTypes = {
    version: PropTypes.object.isRequired,
    baseClass: PropTypes.string.isRequired,
    showDivider: PropTypes.bool,
    onClick: PropTypes.func.isRequired,
    displayConfig: PropTypes.object,
    matchedIds: PropTypes.array,
    withDivider: PropTypes.any,
};

ItemVersion.defaultProps = {
    matchedIds: [],
};
