import React from 'react';
import PropTypes from 'prop-types';
import {hasAudio, hasVideo} from 'wire/utils';

function WireListItemIcons({item, picture, divider}) {
    return (
        <div className='wire-articles__item__icons'>
            {item.type === 'text' &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--text icon--gray'></i>
                </span>
            }
            {picture &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--photo icon--gray'></i>
                </span>
            }
            {hasVideo(item) &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--video icon--gray'></i>
                </span>
            }
            {hasAudio(item) &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--audio icon--gray'></i>
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
