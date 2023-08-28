import React from 'react';
import PropTypes from 'prop-types';
import {hasAudio, hasVideo} from 'wire/utils';

function WireListItemIcons({item, picture, divider}: any) {
    return (
        <div className='wire-articles__item__icons wire-articles__item__icons--compact'>
            {item.type === 'text' &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--text'></i>
                </span>
            }
            {picture &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--photo'></i>
                </span>
            }
            {hasVideo(item) &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--video'></i>
                </span>
            }
            {hasAudio(item) &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--audio'></i>
                </span>
            }
            {divider &&
                <span className='wire-articles__item__divider' />
            }
        </div>
    );
}

WireListItemIcons.propTypes = {
    item: PropTypes.object,
    picture: PropTypes.object,
    divider: PropTypes.bool,
};

export default WireListItemIcons;
