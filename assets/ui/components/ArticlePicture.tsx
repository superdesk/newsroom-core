import classNames from 'classnames';
import {get} from 'lodash';
import PropTypes from 'prop-types';
import React from 'react';

import {getConfig, gettext} from 'assets/utils';
import {getCaption, getDetailRendition, getPreviewRendition} from 'assets/wire/utils';


function formatCredits(picture: any) {
    const copyrightholder = get(picture, 'copyrightholder', '');
    const copyrightnotice = get(picture, 'copyrightnotice', '');

    if (copyrightholder || copyrightnotice) {
        return (
            <span>
                {copyrightholder && <b>{copyrightholder} </b>}
                {copyrightnotice && copyrightnotice}
            </span>
        );
    }
    return null;
}


export default function ArticlePicture({isKilled, picture, isItemDetails, isCustomRendition}: any) {
    const getRenditions = isItemDetails ? getDetailRendition : getPreviewRendition;
    const renditions = getRenditions(picture, isCustomRendition);

    if (!renditions || isKilled) {
        return null;
    }

    const classes = classNames({'wire-column__preview__image--custom': isCustomRendition});
    const caption = getCaption(picture);
    const byline = get(picture, 'byline') ? `(${picture.byline})`.replace('((', '(').replace('))', ')') :
        null;
    const searchUrl = getConfig('multimedia_website_search_url', '');
    const bylineHref = searchUrl && byline ? `${searchUrl}${get(picture, 'guid')}` : '';
    let credits = null;
    if (getConfig('display_credits')) {
        credits = formatCredits(picture);
    }

    return (<figure className='wire-column__preview__image'>
        {isItemDetails &&
        <span><img src={renditions.href} className={classes} alt={caption} /></span> ||
        <img src={renditions.href} className={classes} alt={caption} />}
        <figcaption className='wire-column__preview__caption'>
            {caption}
            {bylineHref && <a href={bylineHref} target='_blank'> {byline}</a>}
            {!bylineHref && picture.byline && (
                <div>{picture.byline}</div>
            )}
            {credits && <p>{`${gettext('Credits ')} `}{credits}</p>}
        </figcaption>
    </figure>);
}

ArticlePicture.propTypes = {
    isKilled: PropTypes.bool.isRequired,
    picture: PropTypes.object.isRequired,
    isItemDetails: PropTypes.bool,
    isCustomRendition: PropTypes.bool,
};

ArticlePicture.defaultProps = {isCustomRendition: false};
