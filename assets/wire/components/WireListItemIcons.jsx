import React from 'react';
import PropTypes from 'prop-types';
import {getContentTypes} from 'wire/utils';

function WireListItemIcons({item, divider}) {
    const contentTypes = getContentTypes(item);

    return (
        <div className='wire-articles__item__icons'>
            {/*{item.type === 'text' &&*/}
            {contentTypes.has('text') &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--text icon--gray-dark'></i>
                </span>
            }
            {contentTypes.has('picture') &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--photo icon--gray-dark'></i>
                </span>
            }
            {contentTypes.has('video') &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--video icon--gray-dark'></i>
                </span>
            }
            {contentTypes.has('audio') &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--audio icon--gray-dark'></i>
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
    divider: PropTypes.bool,
};

export default WireListItemIcons;
