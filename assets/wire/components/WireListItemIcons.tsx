import React from 'react';
import {IArticle} from 'interfaces';
import {getContentTypes} from 'wire/utils';

interface IProps {
    item: IArticle;
    divider?: boolean;
}

function WireListItemIcons({item, divider}: IProps) {
    const contentTypes = getContentTypes(item);

    return (
        <div className='wire-articles__item__icons wire-articles__item__icons--compact'>
            {contentTypes.has('text') &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--text'></i>
                </span>
            }
            {contentTypes.has('picture') &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--photo'></i>
                </span>
            }
            {contentTypes.has('video') &&
                <span className='wire-articles__item__icon'>
                    <i className='icon--video'></i>
                </span>
            }
            {contentTypes.has('audio') &&
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

export default WireListItemIcons;
