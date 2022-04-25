import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import {getOriginalRendition} from 'wire/utils';

export default function ArticleMedia({isKilled, media, download}) {
    const rendition = getOriginalRendition(media);

    return (
        (rendition && !isKilled) && (
            <div className='wire-column__preview__video'>
                <span className='wire-column__preview__video-headline'>{media.headline || media.description_text}</span>
                {media.type === 'video' && (
                    <video controls>
                        <source src={rendition.href} type={rendition.mimetype} />
                        {gettext('Your browser does not support playing video')}
                    </video>
                )}
                {media.type === 'audio' && (
                    <audio controls>
                        <source src={rendition.href} type={rendition.mimetype} />
                        {gettext('Your browser does not support playing audio')}
                    </audio>
                )}
                <button className="btn btn-outline-primary btn-with-icon btn-sm mt-3 mb-4"
                    onClick={() => download(rendition.href, rendition.media, rendition.mimetype)}>
                    <i className="icon--download"></i>{gettext('Download')}
                </button>
            </div>
        ) || null
    );
}

ArticleMedia.propTypes = {
    media: PropTypes.object.isRequired,
    isKilled: PropTypes.bool.isRequired,
    download: PropTypes.func,
};